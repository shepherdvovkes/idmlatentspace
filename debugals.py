#!/usr/bin/env python3
import gzip
import xml.etree.ElementTree as ET
import csv
from collections import defaultdict

def extract_all_notes():
    """Extract all MIDI notes from A2ML1.als with complete information"""
    print("🎵 Extracting all MIDI notes from A2ML1.als...")
    
    try:
        with gzip.open('A2ML1.als', 'rt', encoding='utf-8') as f:
            xml_content = f.read()
        
        root = ET.fromstring(xml_content)
        
        # Find all MIDI clips
        all_clips_data = []
        
        for clip in root.iter('MidiClip'):
            # Get clip name
            name_elem = clip.find('.//Name')
            clip_name = name_elem.get('Value') if name_elem is not None else "Unnamed"
            
            print(f"\n🎹 Processing clip: '{clip_name}'")
            
            # Get clip timing info
            current_start_elem = clip.find('./CurrentStart')
            current_end_elem = clip.find('./CurrentEnd')
            
            clip_start = float(current_start_elem.get('Value', 0)) if current_start_elem is not None else 0
            clip_end = float(current_end_elem.get('Value', 0)) if current_end_elem is not None else 0
            
            # Find the Notes section
            notes_section = clip.find('.//Notes')
            if notes_section is None:
                print(f"  ⚠️  No Notes section found")
                continue
                
            # Find KeyTracks
            key_tracks_section = notes_section.find('./KeyTracks')
            if key_tracks_section is None:
                print(f"  ⚠️  No KeyTracks found")
                continue
            
            # Process each KeyTrack (each represents one MIDI note/pitch)
            key_tracks = key_tracks_section.findall('./KeyTrack')
            
            clip_notes = []
            total_notes_in_clip = 0
            
            for key_track in key_tracks:
                # Get the MIDI key (pitch) for this track
                midi_key_elem = key_track.find('./MidiKey')
                if midi_key_elem is None:
                    continue
                    
                midi_pitch = int(midi_key_elem.get('Value'))
                
                # Get the Notes container within this KeyTrack
                track_notes_section = key_track.find('./Notes')
                if track_notes_section is None:
                    continue
                
                # Find all MidiNoteEvents in this KeyTrack
                note_events = track_notes_section.findall('./MidiNoteEvent')
                
                print(f"    Pitch {midi_pitch} ({midi_to_note_name(midi_pitch)}): {len(note_events)} notes")
                
                for note_event in note_events:
                    attrs = note_event.attrib
                    
                    # Extract note data
                    time = float(attrs.get('Time', 0))
                    duration = float(attrs.get('Duration', 0))
                    velocity = int(attrs.get('Velocity', 64))
                    is_enabled = attrs.get('IsEnabled', 'true').lower() == 'true'
                    note_id = attrs.get('NoteId', '')
                    
                    # Calculate absolute time (relative to project start)
                    absolute_time = clip_start + time
                    
                    note_data = {
                        'clip_name': clip_name,
                        'clip_start': clip_start,
                        'clip_end': clip_end,
                        'time_in_clip': time,
                        'absolute_time': absolute_time,
                        'duration': duration,
                        'midi_pitch': midi_pitch,
                        'note_name': midi_to_note_name(midi_pitch),
                        'velocity': velocity,
                        'is_enabled': is_enabled,
                        'note_id': note_id
                    }
                    
                    clip_notes.append(note_data)
                    total_notes_in_clip += 1
            
            print(f"  ✅ Total notes extracted: {total_notes_in_clip}")
            all_clips_data.extend(clip_notes)
        
        # Sort all notes by absolute time
        all_clips_data.sort(key=lambda x: x['absolute_time'])
        
        print(f"\n🎼 SUMMARY:")
        print(f"   Total notes extracted: {len(all_clips_data)}")
        
        # Group by clip for summary
        clips_summary = defaultdict(int)
        for note in all_clips_data:
            clips_summary[note['clip_name']] += 1
        
        for clip_name, count in clips_summary.items():
            print(f"   - {clip_name}: {count} notes")
        
        # Save to CSV
        csv_filename = 'extracted_notes.csv'
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'clip_name', 'absolute_time', 'time_in_clip', 'duration', 
                'midi_pitch', 'note_name', 'velocity', 'is_enabled', 
                'clip_start', 'clip_end', 'note_id'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for note in all_clips_data:
                writer.writerow(note)
        
        print(f"\n💾 Notes saved to: {csv_filename}")
        
        # Show first few notes as example
        print(f"\n📝 First 10 notes:")
        print("Time    | Clip          | Note  | Vel | Dur   | Enabled")
        print("-" * 60)
        
        for note in all_clips_data[:10]:
            enabled_mark = "✓" if note['is_enabled'] else "✗"
            print(f"{note['absolute_time']:7.2f} | {note['clip_name'][:12]:12s} | {note['note_name']:5s} | {note['velocity']:3d} | {note['duration']:5.2f} | {enabled_mark}")
        
        if len(all_clips_data) > 10:
            print(f"... and {len(all_clips_data) - 10} more notes")
        
        return all_clips_data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []

def midi_to_note_name(midi_number):
    """Convert MIDI number to note name (e.g., 60 -> C4)"""
    if midi_number < 0 or midi_number > 127:
        return f"MIDI{midi_number}"
    
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_number // 12) - 1
    note = note_names[midi_number % 12]
    return f"{note}{octave}"

def analyze_notes_by_clip(notes_data):
    """Analyze extracted notes grouped by clip"""
    print(f"\n🔍 DETAILED ANALYSIS BY CLIP:")
    
    clips = defaultdict(list)
    for note in notes_data:
        clips[note['clip_name']].append(note)
    
    for clip_name, notes in clips.items():
        print(f"\n📋 {clip_name}:")
        print(f"   Total notes: {len(notes)}")
        
        # Get unique pitches
        pitches = sorted(set(note['midi_pitch'] for note in notes))
        print(f"   Pitches used: {[midi_to_note_name(p) for p in pitches]}")
        
        # Time range
        if notes:
            min_time = min(note['time_in_clip'] for note in notes)
            max_time = max(note['time_in_clip'] + note['duration'] for note in notes)
            print(f"   Time range: {min_time:.2f} - {max_time:.2f} beats")
        
        # Velocity range
        velocities = [note['velocity'] for note in notes if note['is_enabled']]
        if velocities:
            print(f"   Velocity range: {min(velocities)} - {max(velocities)}")
        
        # Enabled vs disabled
        enabled_count = sum(1 for note in notes if note['is_enabled'])
        disabled_count = len(notes) - enabled_count
        print(f"   Enabled: {enabled_count}, Disabled: {disabled_count}")

def create_piano_roll_view(notes_data, clip_name=None):
    """Create a simple text-based piano roll view"""
    print(f"\n🎹 PIANO ROLL VIEW:")
    
    # Filter by clip if specified
    if clip_name:
        notes = [n for n in notes_data if n['clip_name'] == clip_name]
        print(f"Showing clip: {clip_name}")
    else:
        notes = notes_data
        print("Showing all clips")
    
    if not notes:
        print("No notes to display")
        return
    
    # Group notes by pitch
    pitch_notes = defaultdict(list)
    for note in notes:
        if note['is_enabled']:  # Only show enabled notes
            pitch_notes[note['midi_pitch']].append(note)
    
    if not pitch_notes:
        print("No enabled notes to display")
        return
    
    # Get time range
    max_time = max(note['time_in_clip'] + note['duration'] for note in notes)
    time_resolution = 0.25  # Quarter note resolution
    
    # Sort pitches from high to low
    sorted_pitches = sorted(pitch_notes.keys(), reverse=True)
    
    print(f"\nTime:  0    1    2    3    4    5    6    7    8    9   10   11   12   13   14   15")
    print("     " + "".join([f"{i:5.0f}" for i in range(0, int(max_time) + 1)]))
    print("     " + "-" * (int(max_time) * 5 + 5))
    
    for pitch in sorted_pitches:
        line = f"{midi_to_note_name(pitch):4s} |"
        
        # Create timeline for this pitch
        timeline = [' '] * int(max_time * 4 + 1)  # 4 positions per beat
        
        for note in pitch_notes[pitch]:
            start_pos = int(note['time_in_clip'] * 4)
            duration_pos = max(1, int(note['duration'] * 4))
            
            # Mark note start
            if start_pos < len(timeline):
                timeline[start_pos] = '█'
            
            # Mark note duration
            for i in range(1, duration_pos):
                pos = start_pos + i
                if pos < len(timeline):
                    timeline[pos] = '─'
        
        # Convert timeline to string with proper spacing
        display_line = ""
        for i, char in enumerate(timeline):
            if i % 4 == 0:  # Beat positions
                display_line += char
            elif i % 2 == 0:  # Half-beat positions  
                display_line += char
            # Skip 16th note positions for readability
        
        print(line + display_line[:80])  # Limit line length

if __name__ == "__main__":
    # Extract all notes
    notes = extract_all_notes()
    
    if notes:
        # Analyze by clip
        analyze_notes_by_clip(notes)
        
        # Show piano roll for bass clip
        create_piano_roll_view(notes, "bass")