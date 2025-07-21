#!/usr/bin/env python3
import gzip
import xml.etree.ElementTree as ET
import csv
from collections import defaultdict
import json

def analyze_project_by_track_types():
    """Анализ проекта с учетом типов треков и их специфики"""
    print("🎛️ Анализ треков с учетом их типов и характеристик...")
    
    try:
        with gzip.open('A2ML1.als', 'rt', encoding='utf-8') as f:
            xml_content = f.read()
        
        root = ET.fromstring(xml_content)
        
        # Отладочная информация о структуре
        print("\n🔍 Отладка структуры треков:")
        
        # Найти все возможные типы треков
        midi_tracks = list(root.iter('MidiTrack'))
        audio_tracks = list(root.iter('AudioTrack'))
        
        print(f"Найдено MIDI треков: {len(midi_tracks)}")
        print(f"Найдено Audio треков: {len(audio_tracks)}")
        
        # Показать структуру первого трека для отладки
        if midi_tracks:
            print(f"\nСтруктура первого MIDI трека:")
            debug_track_structure(midi_tracks[0])
        
        # Найти все треки
        tracks_data = []
        
        # Анализ MIDI треков
        for i, track in enumerate(midi_tracks):
            print(f"\n--- Обработка MIDI трека {i+1}/{len(midi_tracks)} ---")
            track_info = analyze_midi_track(track)
            if track_info:
                tracks_data.append(track_info)
        
        # Анализ аудио треков
        for i, track in enumerate(audio_tracks):
            print(f"\n--- Обработка Audio трека {i+1}/{len(audio_tracks)} ---")
            track_info = analyze_audio_track(track)
            if track_info:
                tracks_data.append(track_info)
        
        # Анализ по типам треков
        if tracks_data:
            analyze_by_track_types(tracks_data)
            # Сохранить детальные данные
            save_track_analysis(tracks_data)
        else:
            print("⚠️ Не удалось извлечь данные треков")
        
        return tracks_data
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return []

def debug_track_structure(track):
    """Отладочная функция для показа структуры трека"""
    print("  Элементы трека:")
    
    # Показать прямые дочерние элементы
    for child in list(track)[:10]:  # Первые 10 элементов
        print(f"    - {child.tag}")
        if child.tag == 'Name' and child.get('Value'):
            print(f"      Value: {child.get('Value')}")
        
        # Показать вложенные элементы
        for subchild in list(child)[:3]:  # Первые 3 подэлемента
            print(f"      - {subchild.tag}")
            if subchild.get('Value'):
                print(f"        Value: {subchild.get('Value')}")
    
    # Поиск всех элементов с атрибутом Value
    print("  Элементы с Value:")
    for elem in track.iter():
        if elem.get('Value') and elem.tag in ['Name', 'EffectiveName', 'UserName']:
            print(f"    {elem.tag}: {elem.get('Value')}")

def analyze_midi_track(track):
    """Анализ MIDI трека с определением типа (бас, барабаны, мелодия)"""
    
    # Получить имя трека - пробуем разные варианты
    track_name = get_track_name(track)
    
    print(f"\n🎹 Анализ MIDI трека: '{track_name}'")
    
    track_data = {
        'name': track_name,
        'type': 'MIDI',
        'track_type': determine_track_type(track_name, track),
        'clips': [],
        'devices': [],
        'automation': [],
        'sends': [],
        'volume': None,
        'pan': None
    }
    
    # Анализ устройств на треке
    devices = analyze_track_devices(track)
    track_data['devices'] = devices
    
    # Анализ клипов
    clips = analyze_track_clips(track)
    track_data['clips'] = clips
    
    # Анализ микшера
    mixer_data = analyze_track_mixer(track)
    track_data.update(mixer_data)
    
    # Анализ автоматизации
    automation = analyze_track_automation(track)
    track_data['automation'] = automation
    
    return track_data

def analyze_audio_track(track):
    """Анализ аудио трека"""
    track_name = get_track_name(track)
    
    print(f"\n🔊 Анализ Audio трека: '{track_name}'")
    
    track_data = {
        'name': track_name,
        'type': 'Audio',
        'track_type': 'master' if 'master' in track_name.lower() else 'audio',
        'clips': [],
        'devices': [],
        'automation': [],
        'sends': [],
        'volume': None,
        'pan': None
    }
    
    # Анализ аудио клипов
    audio_clips = track.findall('.//AudioClip')
    for clip in audio_clips:
        clip_info = analyze_audio_clip(clip)
        if clip_info:
            track_data['clips'].append(clip_info)
    
    # Анализ устройств
    devices = analyze_track_devices(track)
    track_data['devices'] = devices
    
    return track_data

def get_track_name(track):
    """Надежное получение имени трека из разных возможных мест"""
    
    # Вариант 1: Прямое имя в Name
    name_elem = track.find('.//Name')
    if name_elem is not None and name_elem.get('Value'):
        return name_elem.get('Value')
    
    # Вариант 2: Имя в EffectiveName  
    effective_name = track.find('.//EffectiveName')
    if effective_name is not None and effective_name.get('Value'):
        return effective_name.get('Value')
    
    # Вариант 3: Имя в UserName
    user_name = track.find('.//UserName')
    if user_name is not None and user_name.get('Value'):
        return user_name.get('Value')
    
    # Вариант 4: Поиск по LomId для определения номера трека
    lom_id = track.find('.//LomId')
    if lom_id is not None:
        track_id = lom_id.get('Value', 'Unknown')
        return f"Track_{track_id}"
    
    return "Unnamed_Track"

def determine_track_type(track_name, track_element):
    """Определение типа трека по имени и содержимому"""
    
    # Безопасная проверка имени
    if track_name is None:
        track_name = "unknown"
    
    name_lower = track_name.lower()
    
    # Проверка по имени - более точные паттерны
    if any(word in name_lower for word in ['bass', 'бас', 'sub', 'osirus']):
        return 'bass'
    elif any(word in name_lower for word in ['drum', 'kit', 'kick', 'snare', 'hat', 'perc', 'барабан', 'coral']):
        return 'drums'
    elif any(word in name_lower for word in ['lead', 'melody', 'мелодия', 'соло']):
        return 'lead'
    elif any(word in name_lower for word in ['pad', 'string', 'chord', 'аккорд']):
        return 'harmony'
    elif any(word in name_lower for word in ['fx', 'effect', 'эффект']):
        return 'fx'
    elif 'master' in name_lower:
        return 'master'
    
    # Анализ по MIDI нотам (если есть клипы)
    clips = track_element.findall('.//MidiClip')
    if clips:
        midi_notes = []
        clip_names = []
        
        for clip in clips:
            # Получить имя клипа для дополнительного анализа
            clip_name_elem = clip.find('.//Name')
            if clip_name_elem is not None:
                clip_name = clip_name_elem.get('Value', '').lower()
                clip_names.append(clip_name)
                
                # Анализ по именам клипов
                if any(word in clip_name for word in ['funk', 'beat', 'straight', 'swing', 'groove']):
                    return 'drums'
                elif any(word in clip_name for word in ['bass', 'sub']):
                    return 'bass'
            
            for key_track in clip.findall('.//KeyTrack'):
                midi_key_elem = key_track.find('./MidiKey')
                if midi_key_elem is not None:
                    midi_notes.append(int(midi_key_elem.get('Value')))
        
        if midi_notes:
            avg_pitch = sum(midi_notes) / len(midi_notes)
            unique_pitches = len(set(midi_notes))
            pitch_range = max(midi_notes) - min(midi_notes)
            
            print(f"    MIDI анализ: avg_pitch={avg_pitch:.1f}, unique={unique_pitches}, range={pitch_range}")
            print(f"    Питчи: {sorted(set(midi_notes))}")
            print(f"    Имена клипов: {clip_names}")
            
            # Улучшенная логика определения по питчам
            # Барабаны: стандартный GM диапазон 35-81, много уникальных питчей
            if (35 <= min(midi_notes) <= 51 and 
                35 <= max(midi_notes) <= 81 and 
                unique_pitches >= 3):
                print(f"    -> Определен как DRUMS (GM диапазон + много питчей)")
                return 'drums'
            
            # Бас: низкие ноты, мало вариаций
            elif avg_pitch < 50 and unique_pitches <= 3 and pitch_range <= 20:
                print(f"    -> Определен как BASS (низкие ноты + мало вариаций)")
                return 'bass'
            
            # Мелодия: высокие ноты, средний диапазон
            elif avg_pitch > 60 and pitch_range > 12:
                print(f"    -> Определен как LEAD (высокие ноты + широкий диапазон)")
                return 'lead'
            
            # Гармония: средние ноты, много питчей
            elif 50 <= avg_pitch <= 70 and unique_pitches > 5:
                print(f"    -> Определен как HARMONY (средние ноты + много питчей)")
                return 'harmony'
    
    print(f"    -> Не удалось определить тип, остается UNKNOWN")
    return 'unknown'

def analyze_track_devices(track):
    """Анализ устройств на треке"""
    devices = []
    
    # Найти все устройства
    device_chain = track.find('.//DeviceChain')
    if device_chain is None:
        return devices
    
    for device in device_chain.findall('.//AudioEffectGroupDevice'):
        device_info = {
            'type': 'EffectRack',
            'name': get_device_name(device),
            'parameters': get_device_parameters(device)
        }
        devices.append(device_info)
    
    for device in device_chain.findall('.//PluginDevice'):
        device_info = {
            'type': 'Plugin',
            'name': get_device_name(device),
            'plugin_desc': get_plugin_info(device),
            'parameters': get_device_parameters(device)
        }
        devices.append(device_info)
    
    # Специфические устройства Ableton
    device_types = [
        'Operator', 'Simpler', 'Impulse', 'Bass', 'Collision',
        'AutoFilter', 'EqEight', 'Compressor2', 'Reverb', 'Delay'
    ]
    
    for device_type in device_types:
        for device in device_chain.findall(f'.//{device_type}'):
            device_info = {
                'type': device_type,
                'name': device_type,
                'parameters': get_device_parameters(device)
            }
            devices.append(device_info)
    
    return devices

def get_device_name(device):
    """Получить имя устройства"""
    name_elem = device.find('.//UserName')
    if name_elem is not None:
        return name_elem.get('Value', 'Unnamed Device')
    return 'Unnamed Device'

def get_plugin_info(device):
    """Получить информацию о плагине"""
    plugin_desc = device.find('.//PluginDesc')
    if plugin_desc is not None:
        vst_info = plugin_desc.find('.//VstPluginInfo')
        if vst_info is not None:
            plugin_name = vst_info.find('.//PluginName')
            if plugin_name is not None:
                return plugin_name.get('Value', 'Unknown Plugin')
    return 'Unknown Plugin'

def get_device_parameters(device):
    """Получить параметры устройства"""
    parameters = {}
    
    # Найти все параметры
    for param in device.findall('.//FloatEvent'):
        param_id = param.get('Id', '')
        param_value = param.get('Value', '')
        if param_id and param_value:
            parameters[f"param_{param_id}"] = float(param_value)
    
    # Специфические параметры для разных устройств
    for param in device.findall('.//BoolEvent'):
        param_id = param.get('Id', '')
        param_value = param.get('Value', '')
        if param_id and param_value:
            parameters[f"bool_{param_id}"] = param_value.lower() == 'true'
    
    return parameters

def analyze_track_clips(track):
    """Анализ клипов трека"""
    clips = []
    
    midi_clips = track.findall('.//MidiClip')
    for clip in midi_clips:
        clip_info = analyze_midi_clip_detailed(clip)
        if clip_info:
            clips.append(clip_info)
    
    return clips

def analyze_midi_clip_detailed(clip):
    """Детальный анализ MIDI клипа"""
    name_elem = clip.find('.//Name')
    clip_name = name_elem.get('Value') if name_elem is not None else "Unnamed"
    
    # Базовая информация
    current_start = float(clip.find('./CurrentStart').get('Value', 0))
    current_end = float(clip.find('./CurrentEnd').get('Value', 0))
    
    # Анализ нот
    notes_data = extract_clip_notes(clip)
    
    # Статистика по нотам
    note_stats = calculate_note_statistics(notes_data)
    
    clip_info = {
        'name': clip_name,
        'start': current_start,
        'end': current_end,
        'duration': current_end - current_start,
        'notes_count': len(notes_data),
        'note_statistics': note_stats,
        'notes': notes_data
    }
    
    return clip_info

def extract_clip_notes(clip):
    """Извлечь ноты из клипа"""
    notes = []
    
    key_tracks_section = clip.find('.//KeyTracks')
    if key_tracks_section is None:
        return notes
    
    for key_track in key_tracks_section.findall('./KeyTrack'):
        midi_key_elem = key_track.find('./MidiKey')
        if midi_key_elem is None:
            continue
            
        midi_pitch = int(midi_key_elem.get('Value'))
        
        track_notes_section = key_track.find('./Notes')
        if track_notes_section is None:
            continue
        
        for note_event in track_notes_section.findall('./MidiNoteEvent'):
            attrs = note_event.attrib
            
            note_data = {
                'time': float(attrs.get('Time', 0)),
                'duration': float(attrs.get('Duration', 0)),
                'pitch': midi_pitch,
                'velocity': int(attrs.get('Velocity', 64)),
                'enabled': attrs.get('IsEnabled', 'true').lower() == 'true'
            }
            notes.append(note_data)
    
    return notes

def calculate_note_statistics(notes):
    """Вычислить статистику по нотам"""
    if not notes:
        return {}
    
    enabled_notes = [n for n in notes if n['enabled']]
    
    if not enabled_notes:
        return {'enabled_notes': 0}
    
    pitches = [n['pitch'] for n in enabled_notes]
    velocities = [n['velocity'] for n in enabled_notes]
    durations = [n['duration'] for n in enabled_notes]
    
    stats = {
        'enabled_notes': len(enabled_notes),
        'disabled_notes': len(notes) - len(enabled_notes),
        'pitch_range': {
            'min': min(pitches),
            'max': max(pitches),
            'unique_count': len(set(pitches))
        },
        'velocity_range': {
            'min': min(velocities),
            'max': max(velocities),
            'avg': sum(velocities) / len(velocities)
        },
        'duration_range': {
            'min': min(durations),
            'max': max(durations),
            'avg': sum(durations) / len(durations)
        },
        'note_density': len(enabled_notes) / (max([n['time'] + n['duration'] for n in enabled_notes]) if enabled_notes else 1)
    }
    
    return stats

def analyze_track_mixer(track):
    """Анализ микшерных параметров трека"""
    mixer_data = {}
    
    # Громкость
    volume_elem = track.find('.//Volume')
    if volume_elem is not None:
        manual_elem = volume_elem.find('./Manual')
        if manual_elem is not None:
            mixer_data['volume'] = float(manual_elem.get('Value', 0.85))
    
    # Панорама
    pan_elem = track.find('.//Pan')
    if pan_elem is not None:
        manual_elem = pan_elem.find('./Manual')
        if manual_elem is not None:
            mixer_data['pan'] = float(manual_elem.get('Value', 0))
    
    # Sends (посылы на шины)
    sends = []
    sends_section = track.find('.//Sends')
    if sends_section is not None:
        for send in sends_section.findall('./TrackSendHolder'):
            send_info = {
                'active': send.find('./Send/Active').get('Value', 'false').lower() == 'true' if send.find('./Send/Active') is not None else False,
                'value': float(send.find('./Send/Manual').get('Value', 0)) if send.find('./Send/Manual') is not None else 0
            }
            sends.append(send_info)
    
    mixer_data['sends'] = sends
    
    return mixer_data

def analyze_track_automation(track):
    """Анализ автоматизации трека"""
    automation_data = []
    
    # Найти все огибающие автоматизации
    for envelope in track.findall('.//ClipEnvelope'):
        envelope_info = analyze_envelope(envelope)
        if envelope_info:
            automation_data.append(envelope_info)
    
    return automation_data

def analyze_envelope(envelope):
    """Анализ огибающей автоматизации"""
    target_elem = envelope.find('.//EnvelopeTarget')
    if target_elem is None:
        return None
    
    # Получить информацию о цели автоматизации
    device_id = target_elem.find('./Id').get('Value') if target_elem.find('./Id') is not None else None
    
    # Получить точки автоматизации
    automation_events = envelope.findall('.//FloatEvent')
    
    if not automation_events:
        return None
    
    points = []
    for event in automation_events:
        point = {
            'time': float(event.get('Time', 0)),
            'value': float(event.get('Value', 0))
        }
        points.append(point)
    
    envelope_info = {
        'device_id': device_id,
        'points_count': len(points),
        'points': points[:10]  # Первые 10 точек для примера
    }
    
    return envelope_info

def analyze_audio_clip(clip):
    """Анализ аудио клипа"""
    name_elem = clip.find('.//Name')
    clip_name = name_elem.get('Value') if name_elem is not None else "Unnamed"
    
    current_start = float(clip.find('./CurrentStart').get('Value', 0))
    current_end = float(clip.find('./CurrentEnd').get('Value', 0))
    
    clip_info = {
        'name': clip_name,
        'type': 'Audio',
        'start': current_start,
        'end': current_end,
        'duration': current_end - current_start
    }
    
    return clip_info

def analyze_by_track_types(tracks_data):
    """Анализ треков по их типам с разными подходами"""
    
    print(f"\n🎯 АНАЛИЗ ПО ТИПАМ ТРЕКОВ:")
    
    # Группировка по типам
    tracks_by_type = defaultdict(list)
    for track in tracks_data:
        tracks_by_type[track['track_type']].append(track)
    
    for track_type, tracks in tracks_by_type.items():
        print(f"\n📊 {track_type.upper()} ТРЕКИ ({len(tracks)} шт.):")
        
        if track_type == 'bass':
            analyze_bass_tracks(tracks)
        elif track_type == 'drums':
            analyze_drum_tracks(tracks)
        elif track_type == 'lead':
            analyze_lead_tracks(tracks)
        elif track_type == 'harmony':
            analyze_harmony_tracks(tracks)
        elif track_type == 'master':
            analyze_master_tracks(tracks)
        elif track_type == 'unknown':
            analyze_unknown_tracks(tracks)
        else:
            analyze_generic_tracks(tracks)

def analyze_unknown_tracks(tracks):
    """Анализ треков неопределенного типа"""
    print("  ❓ НЕОПРЕДЕЛЕННЫЕ ТРЕКИ:")
    for track in tracks:
        print(f"    {track['name']}: {track['type']}")
        
        # Показать дополнительную информацию для определения типа
        for clip in track['clips']:
            if clip['note_statistics']:
                stats = clip['note_statistics']
                print(f"      Клип '{clip['name']}': {stats['enabled_notes']} нот")
                if 'pitch_range' in stats:
                    pitches = f"{stats['pitch_range']['min']}-{stats['pitch_range']['max']}"
                    print(f"        Питчи: {pitches} ({stats['pitch_range']['unique_count']} уникальных)")

def analyze_harmony_tracks(tracks):
    """Анализ гармонических треков"""
    print("  🎹 ГАРМОНИЧЕСКИЕ ТРЕКИ:")
    for track in tracks:
        print(f"    {track['name']}: аккорды и гармония")
        
        for clip in track['clips']:
            if clip['note_statistics']:
                stats = clip['note_statistics']
                print(f"      Клип '{clip['name']}':")
                print(f"        Голосоведение: {stats['pitch_range']['unique_count']} уникальных нот")
                
                # Анализ аккордов (если много нот одновременно)
                if stats['note_density'] > 2:
                    print(f"        🎼 Плотная гармония (плотность: {stats['note_density']:.1f})")
                elif stats['note_density'] < 0.5:
                    print(f"        🎵 Разреженная текстура (плотность: {stats['note_density']:.1f})")

def analyze_bass_tracks(tracks):
    """Специализированный анализ басовых треков"""
    print("  🎸 БАС-СПЕЦИФИЧЕСКИЙ АНАЛИЗ:")
    
    for track in tracks:
        print(f"\n    Трек: {track['name']}")
        
        # Анализ устройств (особенно фильтры и эффекты)
        bass_devices = analyze_bass_devices(track['devices'])
        if bass_devices:
            print(f"      Басовые устройства: {bass_devices}")
        
        # Анализ частотного диапазона
        for clip in track['clips']:
            if clip['note_statistics']:
                stats = clip['note_statistics']
                print(f"      Клип '{clip['name']}':")
                print(f"        Питч-диапазон: {stats['pitch_range']['min']}-{stats['pitch_range']['max']} MIDI")
                print(f"        Уникальных нот: {stats['pitch_range']['unique_count']}")
                
                # Басовая динамика зависит от фильтрации, не только от velocity
                if 'velocity_range' in stats:
                    print(f"        Velocity: {stats['velocity_range']['min']}-{stats['velocity_range']['max']} (avg: {stats['velocity_range']['avg']:.1f})")
                
                # Проверка на суб-басы
                if stats['pitch_range']['min'] < 40:
                    print(f"        🔊 Содержит суб-басы (MIDI < 40)")
        
        # Анализ автоматизации (важно для баса)
        if track['automation']:
            print(f"      Автоматизация: {len(track['automation'])} параметров")
            for auto in track['automation'][:3]:  # Первые 3
                print(f"        - {auto['points_count']} точек автоматизации")

def analyze_drum_tracks(tracks):
    """Специализированный анализ барабанных треков"""
    print("  🥁 БАРАБАН-СПЕЦИФИЧЕСКИЙ АНАЛИЗ:")
    
    for track in tracks:
        print(f"\n    Трек: {track['name']}")
        
        # Анализ барабанной карты
        drum_map = analyze_drum_mapping(track)
        if drum_map:
            print(f"      Барабанная карта:")
            for pitch, info in drum_map.items():
                drum_name = get_drum_name(pitch)
                print(f"        {drum_name} (MIDI {pitch}): {info['hits']} ударов, vel {info['vel_range']}")
        
        # Анализ динамики (для барабанов velocity очень важна)
        for clip in track['clips']:
            if clip['note_statistics'] and 'velocity_range' in clip['note_statistics']:
                vel_stats = clip['note_statistics']['velocity_range']
                print(f"      Клип '{clip['name']}':")
                print(f"        Динамический диапазон: {vel_stats['min']}-{vel_stats['max']}")
                
                # Анализ выразительности
                vel_range = vel_stats['max'] - vel_stats['min']
                if vel_range > 50:
                    print(f"        🎭 Высокая выразительность (диапазон {vel_range})")
                elif vel_range < 20:
                    print(f"        🔄 Монотонная игра (диапазон {vel_range})")

def analyze_drum_mapping(track):
    """Анализ барабанной карты"""
    drum_map = {}
    
    for clip in track['clips']:
        for note in clip.get('notes', []):
            if not note['enabled']:
                continue
                
            pitch = note['pitch']
            if pitch not in drum_map:
                drum_map[pitch] = {
                    'hits': 0,
                    'velocities': []
                }
            
            drum_map[pitch]['hits'] += 1
            drum_map[pitch]['velocities'].append(note['velocity'])
    
    # Вычислить диапазоны velocity для каждого инструмента
    for pitch in drum_map:
        velocities = drum_map[pitch]['velocities']
        drum_map[pitch]['vel_range'] = f"{min(velocities)}-{max(velocities)}"
    
    return drum_map

def get_drum_name(midi_pitch):
    """Получить название барабана по MIDI ноте"""
    drum_names = {
        35: "Kick (Acoustic)",
        36: "Kick (Electric)",
        37: "Side Stick",
        38: "Snare (Acoustic)",
        39: "Hand Clap",
        40: "Snare (Electric)",
        41: "Low Floor Tom",
        42: "Closed Hi-hat",
        43: "High Floor Tom",
        44: "Pedal Hi-hat",
        45: "Low Tom",
        46: "Open Hi-hat",
        47: "Low-Mid Tom",
        48: "Hi-Mid Tom",
        49: "Crash Cymbal 1",
        50: "High Tom",
        51: "Ride Cymbal 1",
        52: "Chinese Cymbal",
        53: "Ride Bell",
        54: "Tambourine",
        55: "Splash Cymbal",
        56: "Cowbell",
        57: "Crash Cymbal 2",
        58: "Vibra Slap",
        59: "Ride Cymbal 2"
    }
    
    return drum_names.get(midi_pitch, f"Drum {midi_pitch}")

def analyze_bass_devices(devices):
    """Анализ устройств специфичных для баса"""
    bass_specific = []
    
    for device in devices:
        device_name = device['name'].lower()
        device_type = device['type'].lower()
        
        # Басовые синтезаторы и эффекты
        if any(word in device_name for word in ['bass', 'sub', 'operator', 'collision']):
            bass_specific.append(f"{device['type']}: {device['name']}")
        elif any(word in device_type for word in ['autofilter', 'eq', 'compressor']):
            bass_specific.append(f"{device['type']} (басовая обработка)")
    
    return bass_specific

def analyze_lead_tracks(tracks):
    """Анализ ведущих треков"""
    print("  🎺 ЛИДЕР-ТРЕКИ:")
    for track in tracks:
        print(f"    {track['name']}: {len(track['clips'])} клипов")

def analyze_master_tracks(tracks):
    """Анализ мастер-треков"""
    print("  🎚️ МАСТЕР-ТРЕКИ:")
    for track in tracks:
        print(f"    {track['name']}: обработка и сведение")
        if track['devices']:
            print(f"      Устройства мастеринга: {len(track['devices'])}")

def analyze_generic_tracks(tracks):
    """Общий анализ неопределенных треков"""
    print("  ❓ ПРОЧИЕ ТРЕКИ:")
    for track in tracks:
        print(f"    {track['name']}: {track['type']}")

def save_track_analysis(tracks_data):
    """Сохранить результаты анализа"""
    
    # Сохранить JSON с полными данными
    with open('track_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(tracks_data, f, ensure_ascii=False, indent=2)
    
    # Сохранить CSV с основной информацией
    with open('tracks_summary.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'track_name', 'track_type', 'clips_count', 'devices_count', 
            'automation_count', 'volume', 'pan'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for track in tracks_data:
            writer.writerow({
                'track_name': track['name'],
                'track_type': track['track_type'],
                'clips_count': len(track['clips']),
                'devices_count': len(track['devices']),
                'automation_count': len(track['automation']),
                'volume': track.get('volume'),
                'pan': track.get('pan')
            })
    
    print(f"\n💾 Анализ сохранен:")
    print(f"   - track_analysis.json (полные данные)")
    print(f"   - tracks_summary.csv (сводка)")

if __name__ == "__main__":
    tracks = analyze_project_by_track_types()
    print(f"\n✅ Анализ завершен. Обработано {len(tracks)} треков.")