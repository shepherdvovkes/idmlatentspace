#!/usr/bin/env python3
"""
Ableton Live Project Analyzer - Enhanced Version
Анализирует .als файлы и создает подробную статистику проекта
Author: Ovcharov Vladimir
"""

import gzip
import xml.etree.ElementTree as ET
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

class AbletonProjectAnalyzer:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.als_file = None
        self.root = None
        self.analysis = {
            'project_info': {},
            'tracks': [],
            'devices': [],
            'clips': [],
            'automation': [],
            'samples': [],
            'statistics': {},
            'tempo_info': {},
            'master_track': {},
            'returns': [],
            'scenes': [],
            'locators': []
        }
        
    def find_als_file(self):
        """Найти главный .als файл в проекте"""
        als_files = list(self.project_path.glob("*.als"))
        if not als_files:
            print("❌ .als файл не найден в проекте")
            return False
            
        # Выбрать основной файл (не из Backup)
        main_als = None
        for als_file in als_files:
            if "Backup" not in str(als_file):
                main_als = als_file
                break
                
        if not main_als:
            main_als = als_files[0]  # Взять любой если основной не найден
            
        self.als_file = main_als
        print(f"📁 Найден .als файл: {self.als_file.name}")
        return True
        
    def load_and_parse(self):
        """Загрузить и распарсить .als файл"""
        try:
            print("🔓 Распаковка .als файла...")
            with gzip.open(self.als_file, 'rt', encoding='utf-8') as f:
                xml_content = f.read()
                
            print("📋 Парсинг XML структуры...")
            self.root = ET.fromstring(xml_content)
            print(f"✅ XML успешно загружен, root element: {self.root.tag}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при загрузке файла: {e}")
            return False
            
    def analyze_project_info(self):
        """Анализ общей информации о проекте"""
        print("📊 Анализ информации о проекте...")
        
        self.analysis['project_info'] = {
            'file_name': self.als_file.name,
            'file_size': os.path.getsize(self.als_file),
            'analysis_date': datetime.now().isoformat(),
            'ableton_version': self.get_text_value(self.root.find('.//Creator')),
            'project_name': self.project_path.name
        }
        
        # Версия Ableton
        revision = self.root.get('Revision')
        if revision:
            self.analysis['project_info']['revision'] = revision
            
        # Информация о времени
        major_version = self.get_text_value(self.root.find('.//MajorVersion'))
        minor_version = self.get_text_value(self.root.find('.//MinorVersion'))
        if major_version:
            self.analysis['project_info']['live_version'] = f"{major_version}.{minor_version}"
            
    def analyze_tempo_info(self):
        """Анализ темпа и тайм-сигнатуры"""
        print("🎵 Анализ темпа и метронома...")
        
        # Глобальный темп
        master_tempo = self.root.find('.//MasterTrack//Tempo//Manual')
        if master_tempo is not None:
            tempo_value = master_tempo.get('Value')
            self.analysis['tempo_info']['master_tempo'] = float(tempo_value) if tempo_value else None
            
        # Тайм-сигнатура
        time_signature = self.root.find('.//MasterTrack//TimeSignature//TimeSignatureNumerator')
        if time_signature is not None:
            numerator = time_signature.get('Value')
            denominator_elem = self.root.find('.//MasterTrack//TimeSignature//TimeSignatureDenominator')
            denominator = denominator_elem.get('Value') if denominator_elem is not None else '4'
            self.analysis['tempo_info']['time_signature'] = f"{numerator}/{denominator}"
            
        # Метроном
        metronome = self.root.find('.//MasterTrack//Metronome//IsOn')
        if metronome is not None:
            self.analysis['tempo_info']['metronome_on'] = metronome.get('Value') == 'true'
            
    def analyze_tracks(self):
        """Анализ всех треков"""
        print("🎛️ Анализ треков...")
        
        try:
            # MIDI треки
            midi_tracks = self.root.findall('.//MidiTrack')
            print(f"  📊 Найдено MIDI треков: {len(midi_tracks)}")
            for i, track in enumerate(midi_tracks):
                try:
                    track_info = self.analyze_single_track(track, 'MIDI', i)
                    self.analysis['tracks'].append(track_info)
                except Exception as e:
                    print(f"    ⚠️ Ошибка анализа MIDI трека {i}: {e}")
                    continue
                    
            # Аудио треки  
            audio_tracks = self.root.findall('.//AudioTrack')
            print(f"  📊 Найдено Audio треков: {len(audio_tracks)}")
            for i, track in enumerate(audio_tracks):
                try:
                    track_info = self.analyze_single_track(track, 'Audio', i)
                    self.analysis['tracks'].append(track_info)
                except Exception as e:
                    print(f"    ⚠️ Ошибка анализа Audio трека {i}: {e}")
                    continue
                    
            # Return треки
            return_tracks = self.root.findall('.//ReturnTrack')
            print(f"  📊 Найдено Return треков: {len(return_tracks)}")
            for i, track in enumerate(return_tracks):
                try:
                    track_info = self.analyze_single_track(track, 'Return', i)
                    self.analysis['returns'].append(track_info)
                except Exception as e:
                    print(f"    ⚠️ Ошибка анализа Return трека {i}: {e}")
                    continue
                    
            # Master трек
            master_track = self.root.find('.//MasterTrack')
            if master_track is not None:
                try:
                    self.analysis['master_track'] = self.analyze_single_track(master_track, 'Master', 0)
                    print("  📊 Master трек проанализирован")
                except Exception as e:
                    print(f"    ⚠️ Ошибка анализа Master трека: {e}")
                    
        except Exception as e:
            print(f"❌ Критическая ошибка при анализе треков: {e}")
            raise

    def analyze_single_track(self, track_elem, track_type, index):
        """Анализ одного трека"""
        track_info = {
            'type': track_type,
            'index': index,
            'name': 'Unnamed Track',
            'color': None,
            'muted': False,
            'soloed': False,
            'armed': False,
            'volume': 1.0,
            'pan': 0.0,
            'devices': [],
            'clips': [],
            'automation': [],
            'sends': []
        }
        
        try:
            # Название трека
            name_elem = track_elem.find('.//Name//EffectiveName')
            if name_elem is not None:
                track_info['name'] = name_elem.get('Value', 'Unnamed Track')
                
            # Цвет трека
            color_elem = track_elem.find('.//ColorIndex')
            if color_elem is not None:
                track_info['color'] = int(color_elem.get('Value', -1))
                
            # Состояние трека
            track_info['muted'] = self.get_bool_value(track_elem.find('.//TrackMute//IsOn'))
            track_info['soloed'] = self.get_bool_value(track_elem.find('.//Solo//IsOn'))
            track_info['armed'] = self.get_bool_value(track_elem.find('.//Arm//IsOn'))
            
            # Громкость и панорама
            volume_elem = track_elem.find('.//Volume//Manual')
            if volume_elem is not None:
                track_info['volume'] = float(volume_elem.get('Value', 1.0))
                
            pan_elem = track_elem.find('.//Pan//Manual')
            if pan_elem is not None:
                track_info['pan'] = float(pan_elem.get('Value', 0.0))
                
            # Устройства на треке
            device_chain = track_elem.find('.//DeviceChain//Devices')
            if device_chain is not None:
                for device in device_chain:
                    if 'Device' in device.tag:
                        try:
                            device_info = self.analyze_device(device)
                            if device_info:
                                track_info['devices'].append(device_info)
                        except Exception as e:
                            print(f"      ⚠️ Ошибка анализа устройства {device.tag}: {e}")
                            continue
                            
            # Клипы на треке - улучшенный поиск
            clip_slots = track_elem.find('.//ClipSlots')
            if clip_slots is not None:
                for slot_index, slot in enumerate(clip_slots):
                    if slot.tag == 'ClipSlot':
                        # Проверяем есть ли клип в слоте
                        clip_slot_elem = slot.find('.//ClipSlot')
                        if clip_slot_elem is not None:
                            slot = clip_slot_elem
                            
                        if track_type == 'MIDI':
                            midi_clip = slot.find('.//MidiClip')
                            if midi_clip is not None:
                                try:
                                    clip_info = self.analyze_midi_clip(midi_clip)
                                    clip_info['slot_index'] = slot_index
                                    track_info['clips'].append(clip_info)
                                except Exception as e:
                                    print(f"      ⚠️ Ошибка анализа MIDI клипа в слоте {slot_index}: {e}")
                                    continue
                        elif track_type == 'Audio':
                            audio_clip = slot.find('.//AudioClip')
                            if audio_clip is not None:
                                try:
                                    clip_info = self.analyze_audio_clip(audio_clip)
                                    clip_info['slot_index'] = slot_index
                                    track_info['clips'].append(clip_info)
                                except Exception as e:
                                    print(f"      ⚠️ Ошибка анализа Audio клипа в слоте {slot_index}: {e}")
                                    continue
            
            # Дополнительный поиск клипов напрямую в треке
            if track_type == 'MIDI':
                direct_clips = self.find_all_recursive(track_elem, 'MidiClip')
                for clip in direct_clips:
                    if not any(c.get('name') == clip.find('.//Name').get('Value', '') for c in track_info['clips'] if clip.find('.//Name') is not None):
                        try:
                            clip_info = self.analyze_midi_clip(clip)
                            clip_info['location'] = 'direct'
                            track_info['clips'].append(clip_info)
                        except Exception as e:
                            print(f"      ⚠️ Ошибка анализа прямого MIDI клипа: {e}")
                            continue
            elif track_type == 'Audio':
                direct_clips = self.find_all_recursive(track_elem, 'AudioClip')
                for clip in direct_clips:
                    if not any(c.get('name') == clip.find('.//Name').get('Value', '') for c in track_info['clips'] if clip.find('.//Name') is not None):
                        try:
                            clip_info = self.analyze_audio_clip(clip)
                            clip_info['location'] = 'direct'
                            track_info['clips'].append(clip_info)
                        except Exception as e:
                            print(f"      ⚠️ Ошибка анализа прямого Audio клипа: {e}")
                            continue
                            
            # Sends
            sends_section = track_elem.find('.//Sends')
            if sends_section is not None:
                for i, send in enumerate(sends_section):
                    if send.tag == 'Send':
                        try:
                            send_value = self.get_float_value(send.find('.//Manual'))
                            track_info['sends'].append({
                                'index': i,
                                'value': send_value,
                                'active': self.get_bool_value(send.find('.//IsOn'))
                            })
                        except Exception as e:
                            print(f"      ⚠️ Ошибка анализа Send {i}: {e}")
                            continue
                            
            # Автоматизация трека
            automation_section = track_elem.find('.//AutomationEnvelopes')
            if automation_section is not None:
                for envelope in automation_section:
                    if envelope.tag == 'AutomationEnvelope':
                        try:
                            automation_info = self.analyze_automation_envelope(envelope, track_info['name'])
                            if automation_info:
                                track_info['automation'].append(automation_info)
                        except Exception as e:
                            print(f"      ⚠️ Ошибка анализа автоматизации: {e}")
                            continue
                            
        except Exception as e:
            print(f"    ❌ Ошибка в analyze_single_track для {track_type} трека {index}: {e}")
            
        return track_info

    def analyze_device(self, device_elem):
        """Анализ устройства/плагина"""
        device_info = {
            'type': device_elem.tag,
            'name': 'Unknown Device',
            'enabled': True,
            'parameters': [],
            'plugin_info': None,
            'preset_name': None,
            'device_id': None,
            'raw_parameters': {}
        }
        
        # Включен/выключен
        on_elem = device_elem.find('.//IsOn')
        if on_elem is not None:
            device_info['enabled'] = on_elem.get('Value', 'true') == 'true'
            
        # ID устройства
        device_info['device_id'] = device_elem.get('Id', 'Unknown')
        
        # Название устройства в зависимости от типа
        if device_elem.tag == 'PluginDevice':
            # VST/AU плагины
            plugin_desc = device_elem.find('.//PluginDesc')
            if plugin_desc is not None:
                vst_info = plugin_desc.find('.//VstPluginInfo')
                au_info = plugin_desc.find('.//AuPluginInfo')
                
                if vst_info is not None:
                    # VST плагин
                    plugin_name = vst_info.find('.//PlugName')
                    if plugin_name is not None:
                        device_info['name'] = plugin_name.get('Value', 'Unknown VST')
                        
                    vendor_name = vst_info.find('.//VendorName')
                    device_info['plugin_info'] = {
                        'type': 'VST',
                        'vendor': vendor_name.get('Value', 'Unknown') if vendor_name is not None else 'Unknown',
                        'category': self.get_text_value(vst_info.find('.//Category')),
                        'version': self.get_text_value(vst_info.find('.//Version')),
                        'uid': self.get_text_value(vst_info.find('.//UniqueId'))
                    }
                elif au_info is not None:
                    # AU плагин
                    plugin_name = au_info.find('.//Name')
                    if plugin_name is not None:
                        device_info['name'] = plugin_name.get('Value', 'Unknown AU')
                        
                    manufacturer = au_info.find('.//Manufacturer')
                    device_info['plugin_info'] = {
                        'type': 'AU',
                        'manufacturer': manufacturer.get('Value', 'Unknown') if manufacturer is not None else 'Unknown',
                        'subtype': self.get_text_value(au_info.find('.//Subtype')),
                        'type_code': self.get_text_value(au_info.find('.//Type')),
                        'uid': self.get_text_value(au_info.find('.//UniqueId'))
                    }
                    
        elif device_elem.tag == 'AuPluginDevice':
            # Отдельный тип AU устройства
            plugin_desc = device_elem.find('.//PluginDesc//AuPluginInfo')
            if plugin_desc is not None:
                name_elem = plugin_desc.find('.//Name')
                device_info['name'] = name_elem.get('Value', 'AU Plugin') if name_elem is not None else 'AU Plugin'
                
                manufacturer = plugin_desc.find('.//Manufacturer')
                device_info['plugin_info'] = {
                    'type': 'AU',
                    'manufacturer': manufacturer.get('Value', 'Unknown') if manufacturer is not None else 'Unknown',
                    'subtype': self.get_text_value(plugin_desc.find('.//Subtype')),
                    'type_code': self.get_text_value(plugin_desc.find('.//Type'))
                }
                
        elif device_elem.tag == 'DrumGroupDevice':
            # Drum Rack
            device_info['name'] = 'Drum Rack'
            drum_branches = device_elem.findall('.//Branches//DrumBranch')
            device_info['drum_pads'] = len(drum_branches)
            
            # Анализ pad'ов в Drum Rack
            pads_info = []
            for branch in drum_branches:
                pad_info = {
                    'receiving_note': self.get_text_value(branch.find('.//ReceivingNote')),
                    'name': self.get_text_value(branch.find('.//Name')),
                    'devices': []
                }
                
                # Устройства на pad'е
                device_chain = branch.find('.//DeviceChain//Devices')
                if device_chain is not None:
                    for pad_device in device_chain:
                        if 'Device' in pad_device.tag:
                            pad_device_info = self.analyze_device(pad_device)
                            pad_info['devices'].append(pad_device_info)
                            
                pads_info.append(pad_info)
            device_info['pads'] = pads_info
            
        else:
            # Встроенные устройства Ableton
            user_name = device_elem.find('.//UserName')
            if user_name is not None:
                device_info['name'] = user_name.get('Value', device_elem.tag)
            else:
                display_name = device_elem.find('.//DisplayName')
                if display_name is not None:
                    device_info['name'] = display_name.get('Value', device_elem.tag)
                else:
                    # Человеко-читаемые названия для встроенных устройств
                    builtin_names = {
                        'Compressor2': 'Compressor',
                        'Eq8': 'EQ Eight',
                        'Reverb': 'Reverb',
                        'AutoFilter': 'Auto Filter',
                        'Delay': 'Simple Delay',
                        'Operator': 'Operator',
                        'Simpler': 'Simpler',
                        'Impulse': 'Impulse'
                    }
                    device_info['name'] = builtin_names.get(device_elem.tag, device_elem.tag)
                    
        # Название пресета
        preset_ref = device_elem.find('.//PresetRef//FileRef//Name')
        if preset_ref is not None:
            device_info['preset_name'] = preset_ref.get('Value')
            
        # Параметры устройства
        self.analyze_device_parameters(device_elem, device_info)
                
        return device_info
        
    def analyze_device_parameters(self, device_elem, device_info):
        """Детальный анализ параметров устройства"""
        parameters_section = device_elem.find('.//Parameters')
        if parameters_section is not None:
            for param_container in parameters_section:
                try:
                    param_info = self.extract_parameter_info(param_container)
                    if param_info:
                        device_info['parameters'].append(param_info)
                        device_info['raw_parameters'][param_container.tag] = param_info
                except Exception as e:
                    print(f"        ⚠️ Ошибка анализа параметра {param_container.tag}: {e}")
                    continue
                    
    def extract_parameter_info(self, param_elem):
        """Извлечение информации о параметре"""
        param_info = {
            'name': param_elem.tag,
            'value': None,
            'min': None,
            'max': None,
            'automated': False,
            'modulated': False
        }
        
        # Попытка найти значение параметра
        manual_elem = param_elem.find('.//Manual')
        if manual_elem is not None:
            try:
                param_info['value'] = float(manual_elem.get('Value', 0))
                param_info['id'] = manual_elem.get('Id', param_elem.tag)
            except (ValueError, TypeError):
                param_info['value'] = manual_elem.get('Value', 'Unknown')
                
        # Проверка автоматизации
        automation_target = param_elem.find('.//AutomationTarget')
        if automation_target is not None:
            param_info['automated'] = True
            param_info['automation_id'] = automation_target.get('Id')
            
        # Проверка модуляции
        modulation_target = param_elem.find('.//ModulationTarget')
        if modulation_target is not None:
            param_info['modulated'] = True
            
        # Диапазон значений
        min_elem = param_elem.find('.//Min')
        max_elem = param_elem.find('.//Max')
        if min_elem is not None:
            try:
                param_info['min'] = float(min_elem.get('Value', 0))
            except:
                pass
        if max_elem is not None:
            try:
                param_info['max'] = float(max_elem.get('Value', 1))
            except:
                pass
                
        if param_info['value'] is not None:
            return param_info
        return None

    def analyze_midi_clip(self, clip_elem):
        """Анализ MIDI клипа"""
        clip_info = {
            'type': 'MIDI',
            'name': 'MIDI Clip',
            'start_time': 0.0,
            'end_time': 0.0,
            'loop_start': 0.0,
            'loop_end': 0.0,
            'loop_enabled': False,
            'notes_count': 0,
            'automation_count': 0,
            'velocity_range': [0, 127],
            'pitch_range': [0, 127],
            'notes_detail': [],
            'cc_automation': [],
            'time_signature': None,
            'quantization': None
        }
        
        # Название клипа
        name_elem = clip_elem.find('.//Name')
        if name_elem is not None:
            clip_info['name'] = name_elem.get('Value', 'MIDI Clip')
            
        # Время начала и конца
        start_time = clip_elem.find('.//CurrentStart')
        if start_time is not None:
            clip_info['start_time'] = float(start_time.get('Value', 0))
            
        end_time = clip_elem.find('.//CurrentEnd')
        if end_time is not None:
            clip_info['end_time'] = float(end_time.get('Value', 0))
            
        # Петля
        loop_elem = clip_elem.find('.//Loop')
        if loop_elem is not None:
            loop_start = loop_elem.find('.//LoopStart')
            if loop_start is not None:
                clip_info['loop_start'] = float(loop_start.get('Value', 0))
                
            loop_end = loop_elem.find('.//LoopEnd')
            if loop_end is not None:
                clip_info['loop_end'] = float(loop_end.get('Value', 0))
                
            loop_on = loop_elem.find('.//LoopOn')
            if loop_on is not None:
                clip_info['loop_enabled'] = loop_on.get('Value', 'false') == 'true'
                
        # Анализ нот
        notes_section = clip_elem.find('.//Notes')
        notes = []
        if notes_section is not None:
            for note_event in notes_section:
                if note_event.tag == 'MidiNoteEvent':
                    note_info = {
                        'time': float(note_event.get('Time', 0)),
                        'duration': float(note_event.get('Duration', 0)),
                        'pitch': int(note_event.get('Pitch', 60)),
                        'velocity': int(note_event.get('Velocity', 100)),
                        'velocity_deviation': float(note_event.get('VelocityDeviation', 0)),
                        'offset_time': float(note_event.get('OffsetTime', 0))
                    }
                    notes.append(note_info)
                    clip_info['notes_detail'].append(note_info)
        
        clip_info['notes_count'] = len(notes)
        
        if notes:
            velocities = [note['velocity'] for note in notes]
            pitches = [note['pitch'] for note in notes]
            clip_info['velocity_range'] = [min(velocities), max(velocities)]
            clip_info['pitch_range'] = [min(pitches), max(pitches)]
            
        # Анализ CC автоматизации внутри клипа
        automation_section = clip_elem.find('.//AutomationEnvelopes')
        automation_count = 0
        if automation_section is not None:
            for envelope in automation_section:
                if envelope.tag == 'AutomationEnvelope':
                    automation_count += 1
                    cc_info = self.analyze_clip_automation(envelope)
                    if cc_info:
                        clip_info['cc_automation'].append(cc_info)
                        
        clip_info['automation_count'] = automation_count
        
        # Квантизация
        quantization = clip_elem.find('.//NoteQuantization')
        if quantization is not None:
            clip_info['quantization'] = quantization.get('Value', 'None')
            
        return clip_info
        
    def analyze_clip_automation(self, envelope_elem):
        """Анализ автоматизации внутри клипа"""
        automation_info = {
            'target': 'Unknown',
            'target_parameter': None,
            'points_count': 0,
            'value_range': [0.0, 1.0],
            'time_range': [0.0, 0.0],
            'points': []
        }
        
        # Цель автоматизации
        target = envelope_elem.find('.//Target')
        if target is not None:
            automation_info['target'] = target.get('Value', 'Unknown')
            
        # Подробная информация о цели
        target_detail = envelope_elem.find('.//TargetDetail')
        if target_detail is not None:
            automation_info['target_parameter'] = target_detail.get('Value', 'Unknown')
            
        # Точки автоматизации
        events_section = envelope_elem.find('.//AutomationEvents')
        points = []
        if events_section is not None:
            for event in events_section:
                if event.tag == 'FloatEvent':
                    point_info = {
                        'time': float(event.get('Time', 0)),
                        'value': float(event.get('Value', 0))
                    }
                    points.append(point_info)
                    automation_info['points'].append(point_info)
                    
        automation_info['points_count'] = len(points)
        
        if points:
            values = [point['value'] for point in points]
            times = [point['time'] for point in points]
            automation_info['value_range'] = [min(values), max(values)]
            automation_info['time_range'] = [min(times), max(times)]
            
        return automation_info if automation_info['points_count'] > 0 else None

    def analyze_audio_clip(self, clip_elem):
        """Анализ аудио клипа"""
        clip_info = {
            'type': 'Audio',
            'name': 'Audio Clip',
            'start_time': 0.0,
            'end_time': 0.0,
            'sample_ref': None,
            'warped': False,
            'reverse': False,
            'fade_in': 0.0,
            'fade_out': 0.0
        }
        
        # Название клипа
        name_elem = clip_elem.find('.//Name')
        if name_elem is not None:
            clip_info['name'] = name_elem.get('Value', 'Audio Clip')
            
            # Время
        start_time = clip_elem.find('.//CurrentStart')
        if start_time is not None:
            clip_info['start_time'] = float(start_time.get('Value', 0))
            
        end_time = clip_elem.find('.//CurrentEnd')
        if end_time is not None:
            clip_info['end_time'] = float(end_time.get('Value', 0))
            
        # Ссылка на семпл
        sample_ref = clip_elem.find('.//SampleRef//FileRef//Name')
        if sample_ref is not None:
            clip_info['sample_ref'] = sample_ref.get('Value')
            
        # Warp и reverse
        clip_info['warped'] = self.get_bool_value(clip_elem.find('.//WarpMode//IsWarped'))
        clip_info['reverse'] = self.get_bool_value(clip_elem.find('.//Reverse'))
        
        # Fade In/Out
        fade_in = clip_elem.find('.//FadeInLength')
        if fade_in is not None:
            clip_info['fade_in'] = float(fade_in.get('Value', 0))
            
        fade_out = clip_elem.find('.//FadeOutLength')
        if fade_out is not None:
            clip_info['fade_out'] = float(fade_out.get('Value', 0))
            
        return clip_info
        
    def analyze_automation_envelope(self, envelope_elem, track_name):
        """Анализ автоматизации"""
        automation_info = {
            'track_name': track_name,
            'target': 'Unknown',
            'points_count': 0,
            'value_range': [0.0, 1.0],
            'time_range': [0.0, 0.0]
        }
        
        # Цель автоматизации
        target = envelope_elem.find('.//Target')
        if target is not None:
            automation_info['target'] = target.get('Value', 'Unknown')
            
        # Точки автоматизации
        events_section = envelope_elem.find('.//AutomationEvents')
        points = []
        if events_section is not None:
            for event in events_section:
                if event.tag == 'FloatEvent':
                    points.append(event)
                    
        automation_info['points_count'] = len(points)
        
        if points:
            values = []
            times = []
            for point in points:
                time_val = point.get('Time')
                value_val = point.get('Value')
                if time_val:
                    times.append(float(time_val))
                if value_val:
                    values.append(float(value_val))
                    
            if values:
                automation_info['value_range'] = [min(values), max(values)]
            if times:
                automation_info['time_range'] = [min(times), max(times)]
                
        return automation_info

    def analyze_scenes_and_locators(self):
        """Анализ сцен и локаторов"""
        print("🎬 Анализ сцен и локаторов...")
        
        # Сцены
        scenes = self.root.findall('.//Scenes//Scene')
        for i, scene in enumerate(scenes):
            scene_info = {
                'index': i,
                'name': 'Scene',
                'tempo': None,
                'time_signature': None,
                'annotation': None
            }
            
            # Название сцены
            name_elem = scene.find('.//Name')
            if name_elem is not None:
                scene_info['name'] = name_elem.get('Value', f'Scene {i+1}')
                
            # Аннотация
            annotation = scene.find('.//Annotation')
            if annotation is not None:
                scene_info['annotation'] = annotation.get('Value')
                
            # Темп сцены
            tempo = scene.find('.//Tempo')
            if tempo is not None:
                scene_info['tempo'] = float(tempo.get('Value', 120))
                
            self.analysis['scenes'].append(scene_info)
            
        # Локаторы
        locators = self.root.findall('.//Locators//Locator')
        for locator in locators:
            locator_info = {
                'time': 0.0,
                'name': 'Locator',
                'annotation': None
            }
            
            # Время локатора
            time_elem = locator.find('.//Time')
            if time_elem is not None:
                locator_info['time'] = float(time_elem.get('Value', 0))
                
            # Название
            name_elem = locator.find('.//Name')
            if name_elem is not None:
                locator_info['name'] = name_elem.get('Value', 'Locator')
                
            # Аннотация
            annotation = locator.find('.//Annotation')
            if annotation is not None:
                locator_info['annotation'] = annotation.get('Value')
                
            self.analysis['locators'].append(locator_info)
            
    def analyze_global_automation(self):
        """Анализ глобальной автоматизации"""
        print("🎚️ Анализ глобальной автоматизации...")
        
        # Поиск всех envelope автоматизации в проекте
        all_automation = self.root.findall('.//AutomationEnvelopes//AutomationEnvelope')
        
        for envelope in all_automation:
            automation_info = self.analyze_automation_envelope(envelope, 'Global')
            if automation_info:
                self.analysis['automation'].append(automation_info)
                
    def analyze_samples(self):
        """Анализ семплов в проекте"""
        print("🎵 Анализ семплов...")
        
        samples_folder = self.project_path / "Samples"
        if samples_folder.exists():
            for sample_file in samples_folder.rglob("*.wav"):
                self.analysis['samples'].append({
                    'name': sample_file.name,
                    'path': str(sample_file.relative_to(self.project_path)),
                    'size': sample_file.stat().st_size,
                    'modified': datetime.fromtimestamp(sample_file.stat().st_mtime).isoformat()
                })
                
    def calculate_statistics(self):
        """Подсчет общей статистики"""
        print("📈 Подсчет статистики...")
        
        stats = {
            'total_tracks': len(self.analysis['tracks']),
            'midi_tracks': len([t for t in self.analysis['tracks'] if t['type'] == 'MIDI']),
            'audio_tracks': len([t for t in self.analysis['tracks'] if t['type'] == 'Audio']),
            'return_tracks': len(self.analysis['returns']),
            'total_clips': 0,
            'midi_clips': 0,
            'audio_clips': 0,
            'total_devices': 0,
            'plugin_devices': 0,
            'builtin_devices': 0,
            'automation_envelopes': 0,
            'total_notes': 0,
            'samples_count': len(self.analysis['samples'])
        }
        
        # Подсчет клипов и устройств
        all_tracks = self.analysis['tracks'] + self.analysis['returns']
        if self.analysis['master_track']:
            all_tracks.append(self.analysis['master_track'])
            
        for track in all_tracks:
            stats['total_clips'] += len(track['clips'])
            stats['total_devices'] += len(track['devices'])
            stats['automation_envelopes'] += len(track['automation'])
            
            for clip in track['clips']:
                if clip['type'] == 'MIDI':
                    stats['midi_clips'] += 1
                    stats['total_notes'] += clip.get('notes_count', 0)
                elif clip['type'] == 'Audio':
                    stats['audio_clips'] += 1
                    
            for device in track['devices']:
                if device['type'] == 'PluginDevice':
                    stats['plugin_devices'] += 1
                else:
                    stats['builtin_devices'] += 1
                    
        self.analysis['statistics'] = stats

    def generate_report(self):
        """Создать текстовый отчет"""
        report_lines = []
        
        # Заголовок
        report_lines.extend([
            "=" * 80,
            "🎵 ABLETON LIVE PROJECT ANALYSIS REPORT",
            "=" * 80,
            f"📁 Project: {self.analysis['project_info']['project_name']}",
            f"📄 File: {self.analysis['project_info']['file_name']}",
            f"📅 Analysis Date: {self.analysis['project_info']['analysis_date']}",
            f"🎛️ Ableton Version: {self.analysis['project_info'].get('live_version', 'Unknown')}",
            ""
        ])
        
        # Общая статистика
        stats = self.analysis['statistics']
        report_lines.extend([
            "📊 GENERAL STATISTICS",
            "-" * 40,
            f"Total Tracks: {stats['total_tracks']}",
            f"  • MIDI Tracks: {stats['midi_tracks']}",
            f"  • Audio Tracks: {stats['audio_tracks']}",
            f"  • Return Tracks: {stats['return_tracks']}",
            f"Total Clips: {stats['total_clips']}",
            f"  • MIDI Clips: {stats['midi_clips']}",
            f"  • Audio Clips: {stats['audio_clips']}",
            f"Total Devices: {stats['total_devices']}",
            f"  • Plugin Devices: {stats['plugin_devices']}",
            f"  • Built-in Devices: {stats['builtin_devices']}",
            f"Automation Envelopes: {stats['automation_envelopes']}",
            f"Total MIDI Notes: {stats['total_notes']}",
            f"Samples: {stats['samples_count']}",
            ""
        ])
        
        # Информация о темпе
        if self.analysis['tempo_info']:
            tempo_info = self.analysis['tempo_info']
            report_lines.extend([
                "🎵 TEMPO & TIME SIGNATURE",
                "-" * 40,
                f"Master Tempo: {tempo_info.get('master_tempo', 'Unknown')} BPM",
                f"Time Signature: {tempo_info.get('time_signature', 'Unknown')}",
                f"Metronome: {'On' if tempo_info.get('metronome_on') else 'Off'}",
                ""
            ])
            
        # Детали треков
        report_lines.extend([
            "🎛️ TRACKS DETAILS",
            "-" * 40
        ])
        
        for track in self.analysis['tracks']:
            status_flags = []
            if track['muted']:
                status_flags.append("MUTED")
            if track['soloed']:
                status_flags.append("SOLO")
            if track['armed']:
                status_flags.append("ARMED")
                
            status_str = f" [{', '.join(status_flags)}]" if status_flags else ""
            
            report_lines.extend([
                f"📍 {track['type']} Track: '{track['name']}'{status_str}",
                f"   Volume: {track['volume']:.2f}, Pan: {track['pan']:.2f}",
                f"   Clips: {len(track['clips'])}, Devices: {len(track['devices'])}, Automation: {len(track['automation'])}"
            ])
            
            # Устройства на треке
            if track['devices']:
                report_lines.append("   🔌 Devices:")
                for device in track['devices']:
                    enabled_str = "✅" if device['enabled'] else "❌"
                    
                    # Показать информацию о плагине
                    plugin_info = ""
                    if device.get('plugin_info'):
                        plugin_type = device['plugin_info'].get('type', 'Unknown')
                        vendor = device['plugin_info'].get('vendor') or device['plugin_info'].get('manufacturer', 'Unknown')
                        plugin_info = f" ({plugin_type}: {vendor})"
                    
                    # Показать пресет если есть
                    preset_info = ""
                    if device.get('preset_name'):
                        preset_info = f" [Preset: {device['preset_name']}]"
                    
                    report_lines.append(f"     {enabled_str} {device['name']}{plugin_info}{preset_info}")
                    
                    # Показать ключевые параметры
                    if device['parameters'] and len(device['parameters']) <= 10:
                        for param in device['parameters'][:5]:
                            if isinstance(param['value'], (int, float)):
                                report_lines.append(f"       • {param['name']}: {param['value']:.3f}")
                    elif len(device['parameters']) > 10:
                        report_lines.append(f"       • Parameters: {len(device['parameters'])} total")
                    
                    # Drum Rack pads
                    if device.get('pads'):
                        report_lines.append(f"       • Drum Pads: {len(device['pads'])} configured")
                        for pad in device['pads'][:3]:
                            pad_name = pad.get('name', f"Note {pad.get('receiving_note', 'Unknown')}")
                            devices_count = len(pad.get('devices', []))
                            report_lines.append(f"         - {pad_name}: {devices_count} devices")
                    
            # Клипы на треке
            if track['clips']:
                report_lines.append("   🎵 Clips:")
                for clip in track['clips']:
                    duration = clip['end_time'] - clip['start_time']
                    if clip['type'] == 'MIDI':
                        extra_info = f", Notes: {clip['notes_count']}"
                        if clip['automation_count'] > 0:
                            extra_info += f", CC Automation: {clip['automation_count']}"
                        if clip.get('velocity_range'):
                            vel_min, vel_max = clip['velocity_range']
                            extra_info += f", Velocity: {vel_min}-{vel_max}"
                    else:
                        extra_info = f", Sample: {clip.get('sample_ref', 'Unknown')}"
                        if clip.get('warped'):
                            extra_info += " [Warped]"
                        if clip.get('reverse'):
                            extra_info += " [Reversed]"
                    
                    location_info = f" (Slot {clip.get('slot_index', '?')})" if clip.get('slot_index') is not None else ""
                    report_lines.append(f"     📄 {clip['name']}{location_info} (Duration: {duration:.2f}{extra_info})")
                    
                    # Показать детали CC автоматизации
                    if clip.get('cc_automation'):
                        for cc in clip['cc_automation'][:3]:
                            target = cc.get('target', 'Unknown')
                            points = cc.get('points_count', 0)
                            value_range = cc.get('value_range', [0, 1])
                            report_lines.append(f"       • CC {target}: {points} points, range {value_range[0]:.2f}-{value_range[1]:.2f}")
                    
            # Автоматизация трека
            if track['automation']:
                report_lines.append("   🎚️ Track Automation:")
                for auto in track['automation'][:5]:
                    target = auto.get('target', 'Unknown')
                    points = auto.get('points_count', 0)
                    report_lines.append(f"     • {target}: {points} automation points")
                    
            report_lines.append("")
            
        # Return треки
        if self.analysis['returns']:
            report_lines.extend([
                "🔄 RETURN TRACKS",
                "-" * 40
            ])
            for track in self.analysis['returns']:
                report_lines.extend([
                    f"📍 Return {track['index']}: '{track['name']}'",
                    f"   Volume: {track['volume']:.2f}, Devices: {len(track['devices'])}"
                ])
                for device in track['devices']:
                    enabled_str = "✅" if device['enabled'] else "❌"
                    plugin_info = ""
                    if device.get('plugin_info'):
                        vendor = device['plugin_info'].get('vendor') or device['plugin_info'].get('manufacturer', '')
                        if vendor:
                            plugin_info = f" ({vendor})"
                    report_lines.append(f"     {enabled_str} {device['name']}{plugin_info}")
            report_lines.append("")
            
        # Master трек
        if self.analysis['master_track']:
            master = self.analysis['master_track']
            report_lines.extend([
                "🎚️ MASTER TRACK",
                "-" * 40,
                f"Volume: {master['volume']:.2f}",
                f"Devices: {len(master['devices'])}"
            ])
            for device in master['devices']:
                enabled_str = "✅" if device['enabled'] else "❌"
                plugin_info = ""
                if device.get('plugin_info'):
                    vendor = device['plugin_info'].get('vendor') or device['plugin_info'].get('manufacturer', '')
                    if vendor:
                        plugin_info = f" ({vendor})"
                report_lines.append(f"   {enabled_str} {device['name']}{plugin_info}")
            report_lines.append("")
            
        # Сцены
        if self.analysis['scenes']:
            report_lines.extend([
                "🎬 SCENES",
                "-" * 40
            ])
            for scene in self.analysis['scenes']:
                tempo_info = f" (Tempo: {scene['tempo']})" if scene.get('tempo') else ""
                annotation_info = f" - {scene['annotation']}" if scene.get('annotation') else ""
                report_lines.append(f"🎬 {scene['name']}{tempo_info}{annotation_info}")
            report_lines.append("")
            
        # Локаторы
        if self.analysis['locators']:
            report_lines.extend([
                "📍 LOCATORS",
                "-" * 40
            ])
            for locator in self.analysis['locators']:
                time_info = f" (Time: {locator['time']:.2f})"
                annotation_info = f" - {locator['annotation']}" if locator.get('annotation') else ""
                report_lines.append(f"📍 {locator['name']}{time_info}{annotation_info}")
            report_lines.append("")
            
        # Семплы
        if self.analysis['samples']:
            report_lines.extend([
                "🎵 SAMPLES",
                "-" * 40
            ])
            for sample in self.analysis['samples']:
                size_mb = sample['size'] / (1024 * 1024)
                report_lines.append(f"📄 {sample['name']} ({size_mb:.1f} MB)")
            report_lines.append("")
                
        return "\n".join(report_lines)

    def generate_cc_automation_report(self):
        """Создать специальный отчет по CC автоматизации для исследования синтезаторов"""
        report_lines = []
        
        # Заголовок
        report_lines.extend([
            "=" * 80,
            "🎛️ CC AUTOMATION ANALYSIS REPORT",
            "=" * 80,
            f"📁 Project: {self.analysis['project_info']['project_name']}",
            f"📄 File: {self.analysis['project_info']['file_name']}",
            f"📅 Analysis Date: {self.analysis['project_info']['analysis_date']}",
            ""
        ])
        
        # Сводка по CC автоматизации
        total_cc_envelopes = 0
        total_cc_points = 0
        cc_targets = {}
        
        # Собираем данные по всем трекам
        all_tracks = self.analysis['tracks'] + self.analysis['returns']
        if self.analysis['master_track']:
            all_tracks.append(self.analysis['master_track'])
            
        for track in all_tracks:
            for clip in track['clips']:
                if clip.get('cc_automation'):
                    for cc in clip['cc_automation']:
                        total_cc_envelopes += 1
                        total_cc_points += cc.get('points_count', 0)
                        target = cc.get('target', 'Unknown')
                        if target not in cc_targets:
                            cc_targets[target] = {'count': 0, 'total_points': 0}
                        cc_targets[target]['count'] += 1
                        cc_targets[target]['total_points'] += cc.get('points_count', 0)
                        
            for auto in track['automation']:
                total_cc_envelopes += 1
                total_cc_points += auto.get('points_count', 0)
                target = auto.get('target', 'Unknown')
                if target not in cc_targets:
                    cc_targets[target] = {'count': 0, 'total_points': 0}
                cc_targets[target]['count'] += 1
                cc_targets[target]['total_points'] += auto.get('points_count', 0)
                
        report_lines.extend([
            "📊 CC AUTOMATION SUMMARY",
            "-" * 40,
            f"Total CC Automation Envelopes: {total_cc_envelopes}",
            f"Total Automation Points: {total_cc_points}",
            f"Average Points per Envelope: {total_cc_points/max(total_cc_envelopes, 1):.1f}",
            f"Unique CC Targets: {len(cc_targets)}",
            ""
        ])
        
        # Детали по каждому треку с синтезаторами
        report_lines.extend([
            "🎹 SYNTHESIZER TRACKS WITH CC AUTOMATION",
            "-" * 60
        ])
        
        for track in self.analysis['tracks']:
            if track['type'] == 'MIDI' and (track['devices'] or track['clips']):
                # Найти синтезаторы на треке
                synths = [d for d in track['devices'] if d['type'] in ['PluginDevice', 'AuPluginDevice'] or 'synth' in d['name'].lower()]
                
                if synths or any(clip.get('cc_automation') for clip in track['clips']):
                    report_lines.extend([
                        f"🎹 Track: '{track['name']}'",
                        f"   Type: {track['type']}, Volume: {track['volume']:.2f}"
                    ])
                    
                    # Синтезаторы
                    if synths:
                        report_lines.append("   🔌 Synthesizers:")
                        for synth in synths:
                            plugin_info = ""
                            if synth.get('plugin_info'):
                                vendor = synth['plugin_info'].get('vendor') or synth['plugin_info'].get('manufacturer', '')
                                plugin_type = synth['plugin_info'].get('type', '')
                                if vendor or plugin_type:
                                    plugin_info = f" ({plugin_type}: {vendor})" if vendor else f" ({plugin_type})"
                            
                            report_lines.append(f"     • {synth['name']}{plugin_info}")
                            
                            # Ключевые параметры синтезатора
                            if synth['parameters']:
                                filter_params = [p for p in synth['parameters'] if 'filter' in p['name'].lower() or 'cutoff' in p['name'].lower()]
                                lfo_params = [p for p in synth['parameters'] if 'lfo' in p['name'].lower()]
                                env_params = [p for p in synth['parameters'] if 'env' in p['name'].lower() or 'attack' in p['name'].lower() or 'decay' in p['name'].lower()]
                                
                                if filter_params:
                                    report_lines.append("       Filter Parameters:")
                                    for param in filter_params[:3]:
                                        report_lines.append(f"         - {param['name']}: {param['value']:.3f}")
                                        
                                if lfo_params:
                                    report_lines.append("       LFO Parameters:")
                                    for param in lfo_params[:3]:
                                        report_lines.append(f"         - {param['name']}: {param['value']:.3f}")
                                        
                                if env_params:
                                    report_lines.append("       Envelope Parameters:")
                                    for param in env_params[:3]:
                                        report_lines.append(f"         - {param['name']}: {param['value']:.3f}")
                    
                    # CC автоматизация в клипах
                    total_clip_automation = 0
                    for clip in track['clips']:
                        if clip.get('cc_automation'):
                            if total_clip_automation == 0:
                                report_lines.append("   🎵 CC Automation in Clips:")
                            total_clip_automation += len(clip['cc_automation'])
                            
                            report_lines.append(f"     📄 Clip '{clip['name']}':")
                            for cc in clip['cc_automation']:
                                target = cc.get('target', 'Unknown')
                                points = cc.get('points_count', 0)
                                value_range = cc.get('value_range', [0, 1])
                                time_range = cc.get('time_range', [0, 0])
                                
                                report_lines.append(f"       • {target}: {points} points")
                                report_lines.append(f"         Range: {value_range[0]:.3f} to {value_range[1]:.3f}")
                                report_lines.append(f"         Time: {time_range[0]:.2f} to {time_range[1]:.2f}")
                    
                    # Автоматизация на уровне трека
                    if track['automation']:
                        report_lines.append("   🎚️ Track-level Automation:")
                        for auto in track['automation']:
                            target = auto.get('target', 'Unknown')
                            points = auto.get('points_count', 0)
                            report_lines.append(f"     • {target}: {points} automation points")
                    
                    report_lines.append("")
        
        # Анализ плотности автоматизации
        if cc_targets:
            report_lines.extend([
                "📈 CC AUTOMATION DENSITY ANALYSIS",
                "-" * 50
            ])
            
            # Сортировка по количеству точек
            sorted_targets = sorted(cc_targets.items(), key=lambda x: x[1]['total_points'], reverse=True)
            
            for target, data in sorted_targets[:10]:
                avg_points = data['total_points'] / data['count']
                report_lines.append(f"🎛️ {target}:")
                report_lines.append(f"   Envelopes: {data['count']}, Total Points: {data['total_points']}")
                report_lines.append(f"   Average Points per Envelope: {avg_points:.1f}")
                
        # Рекомендации для исследования
        report_lines.extend([
            "",
            "💡 RECOMMENDATIONS FOR SYNTHESIZER RESEARCH",
            "-" * 50,
            "Based on this analysis, consider focusing on:",
            ""
        ])
        
        if total_cc_envelopes > 0:
            density = total_cc_points / total_cc_envelopes
            if density > 10:
                report_lines.append("✅ High CC automation density detected - excellent for latent space modeling")
            elif density > 5:
                report_lines.append("⚠️ Moderate CC automation density - may need additional data")
            else:
                report_lines.append("❌ Low CC automation density - consider projects with more parameter automation")
        
        # Конкретные рекомендации
        if any('filter' in target.lower() for target in cc_targets.keys()):
            report_lines.append("🎛️ Filter automation detected - good for timbral evolution analysis")
        if any('lfo' in target.lower() for target in cc_targets.keys()):
            report_lines.append("🌊 LFO automation detected - useful for rhythmic modulation patterns")
        if len([t for t in self.analysis['tracks'] if t['type'] == 'MIDI' and len(t['devices']) > 0]) >= 2:
            report_lines.append("🎹 Multiple synthesizer tracks - good for comparative analysis")
            
        return "\n".join(report_lines)

    def export_for_synthesizer_research(self):
        """Экспорт данных в формате для исследования синтезаторов"""
        print("🔬 Экспорт данных для исследования синтезаторов...")
        
        research_data = {
            'project_info': self.analysis['project_info'],
            'synthesizer_tracks': [],
            'cc_automation_summary': {
                'total_envelopes': 0,
                'total_points': 0,
                'cc_controllers_used': {},
                'parameter_types': {
                    'filter': [],
                    'lfo': [],
                    'envelope': [],
                    'oscillator': [],
                    'effects': []
                }
            },
            'midi_clips_with_automation': [],
            'recommended_segments': []
        }
        
        # Анализ треков с синтезаторами
        for track in self.analysis['tracks']:
            if track['type'] == 'MIDI' and track['devices']:
                synth_track = {
                    'track_name': track['name'],
                    'track_index': track['index'],
                    'volume': track['volume'],
                    'pan': track['pan'],
                    'synthesizers': [],
                    'clips': [],
                    'automation_density': 0
                }
                
                # Найти синтезаторы
                for device in track['devices']:
                    if device['type'] in ['PluginDevice', 'AuPluginDevice'] or any(keyword in device['name'].lower() for keyword in ['synth', 'operator', 'wavetable', 'serum', 'massive', 'sylenth']):
                        synth_info = {
                            'name': device['name'],
                            'type': device['type'],
                            'enabled': device['enabled'],
                            'plugin_info': device.get('plugin_info'),
                            'preset_name': device.get('preset_name'),
                            'parameters': device['parameters'],
                            'cc_mappings': []
                        }
                        
                        # Категоризировать параметры
                        for param in device['parameters']:
                            param_name = param['name'].lower()
                            if any(keyword in param_name for keyword in ['filter', 'cutoff', 'resonance']):
                                research_data['cc_automation_summary']['parameter_types']['filter'].append({
                                    'track': track['name'],
                                    'device': device['name'],
                                    'parameter': param['name'],
                                    'value': param['value']
                                })
                            elif any(keyword in param_name for keyword in ['lfo', 'oscillator']):
                                research_data['cc_automation_summary']['parameter_types']['lfo'].append({
                                    'track': track['name'],
                                    'device': device['name'],
                                    'parameter': param['name'],
                                    'value': param['value']
                                })
                            elif any(keyword in param_name for keyword in ['env', 'attack', 'decay', 'sustain', 'release']):
                                research_data['cc_automation_summary']['parameter_types']['envelope'].append({
                                    'track': track['name'],
                                    'device': device['name'],
                                    'parameter': param['name'],
                                    'value': param['value']
                                })
                        
                        synth_track['synthesizers'].append(synth_info)
                
                # Анализ клипов с автоматизацией
                for clip in track['clips']:
                    if clip.get('cc_automation') or clip['notes_count'] > 0:
                        clip_info = {
                            'name': clip['name'],
                            'start_time': clip['start_time'],
                            'end_time': clip['end_time'],
                            'duration': clip['end_time'] - clip['start_time'],
                            'notes_count': clip['notes_count'],
                            'cc_automation': clip.get('cc_automation', []),
                            'velocity_range': clip.get('velocity_range'),
                            'pitch_range': clip.get('pitch_range'),
                            'suitable_for_research': False
                        }
                        
                        # Оценить пригодность для исследования
                        if (clip['notes_count'] >= 10 and 
                            len(clip.get('cc_automation', [])) >= 2 and
                            clip_info['duration'] >= 2.0):
                            clip_info['suitable_for_research'] = True
                            research_data['recommended_segments'].append({
                                'track': track['name'],
                                'clip': clip['name'],
                                'duration': clip_info['duration'],
                                'automation_count': len(clip.get('cc_automation', [])),
                                'notes_count': clip['notes_count'],
                                'reason': 'High note density with multiple CC automation'
                            })
                        
                        synth_track['clips'].append(clip_info)
                        
                        # Подсчет плотности автоматизации
                        for cc in clip.get('cc_automation', []):
                            synth_track['automation_density'] += cc.get('points_count', 0)
                            research_data['cc_automation_summary']['total_envelopes'] += 1
                            research_data['cc_automation_summary']['total_points'] += cc.get('points_count', 0)
                            
                            # Подсчет использования CC контроллеров
                            target = cc.get('target', 'Unknown')
                            if target not in research_data['cc_automation_summary']['cc_controllers_used']:
                                research_data['cc_automation_summary']['cc_controllers_used'][target] = 0
                            research_data['cc_automation_summary']['cc_controllers_used'][target] += 1
                
                if synth_track['synthesizers'] or synth_track['clips']:
                    research_data['synthesizer_tracks'].append(synth_track)
        
        # Сохранить исследовательские данные
        research_file = self.project_path / "synthesizer_research_data.json"
        with open(research_file, 'w', encoding='utf-8') as f:
            json.dump(research_data, f, indent=2, ensure_ascii=False)
        print(f"🔬 Данные для исследования сохранены: {research_file}")
        
        # Создать CSV для быстрого анализа
        self.create_csv_exports(research_data)
        
        return research_file
        
    def create_csv_exports(self, research_data):
        """Создать CSV файлы для быстрого анализа"""
        import csv
        
        # CSV с информацией о клипах
        clips_csv = self.project_path / "clips_analysis.csv"
        with open(clips_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Track', 'Clip_Name', 'Duration', 'Notes_Count', 'CC_Automation_Count', 
                           'Velocity_Min', 'Velocity_Max', 'Pitch_Min', 'Pitch_Max', 'Suitable_For_Research'])
            
            for track in research_data['synthesizer_tracks']:
                for clip in track['clips']:
                    vel_range = clip.get('velocity_range', [0, 127])
                    pitch_range = clip.get('pitch_range', [0, 127])
                    writer.writerow([
                        track['track_name'],
                        clip['name'],
                        clip['duration'],
                        clip['notes_count'],
                        len(clip.get('cc_automation', [])),
                        vel_range[0] if vel_range else 0,
                        vel_range[1] if vel_range else 127,
                        pitch_range[0] if pitch_range else 0,
                        pitch_range[1] if pitch_range else 127,
                        clip['suitable_for_research']
                    ])
        
        # CSV с информацией о синтезаторах
        synths_csv = self.project_path / "synthesizers_analysis.csv"
        with open(synths_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Track', 'Synthesizer_Name', 'Plugin_Type', 'Vendor', 'Preset', 
                           'Parameters_Count', 'Enabled'])
            
            for track in research_data['synthesizer_tracks']:
                for synth in track['synthesizers']:
                    plugin_info = synth.get('plugin_info', {})
                    vendor = plugin_info.get('vendor') or plugin_info.get('manufacturer', 'Unknown')
                    writer.writerow([
                        track['track_name'],
                        synth['name'],
                        synth['type'],
                        vendor,
                        synth.get('preset_name', 'Unknown'),
                        len(synth['parameters']),
                        synth['enabled']
                    ])
        
        print(f"📊 CSV анализ сохранен: {clips_csv.name}, {synths_csv.name}")

    def save_results(self):
        """Сохранить результаты анализа"""
        # JSON файл с полными данными
        json_file = self.project_path / "project_analysis.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis, f, indent=2, ensure_ascii=False)
        print(f"💾 JSON результаты сохранены: {json_file}")
        
        # Текстовый отчет
        report_file = self.project_path / "project_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(self.generate_report())
        print(f"📄 Текстовый отчет сохранен: {report_file}")
        
        # CC автоматизация отчет для исследования
        cc_report_file = self.project_path / "cc_automation_report.txt"
        with open(cc_report_file, 'w', encoding='utf-8') as f:
            f.write(self.generate_cc_automation_report())
        print(f"🎛️ CC автоматизация отчет сохранен: {cc_report_file}")
        
        return json_file, report_file

    def find_elements_by_tag_contains(self, parent, tag_substring):
        """Безопасный поиск элементов по части имени тега"""
        found_elements = []
        if parent is not None:
            for child in parent.iter():
                if tag_substring in child.tag:
                    found_elements.append(child)
        return found_elements
    
    def find_all_recursive(self, parent, tag_name):
        """Рекурсивный поиск всех элементов с определенным тегом"""
        found_elements = []
        if parent is not None:
            # Поиск в прямых детях
            for child in parent:
                if child.tag == tag_name:
                    found_elements.append(child)
                # Рекурсивный поиск в подэлементах
                found_elements.extend(self.find_all_recursive(child, tag_name))
        return found_elements
        
    def get_text_value(self, element):
        """Получить текстовое значение элемента"""
        if element is not None:
            return element.get('Value')
        return None
        
    def get_bool_value(self, element):
        """Получить boolean значение элемента"""
        if element is not None:
            return element.get('Value', 'false').lower() == 'true'
        return False
        
    def get_float_value(self, element):
        """Получить float значение элемента"""
        if element is not None:
            try:
                return float(element.get('Value', 0))
            except (ValueError, TypeError):
                return 0.0
        return 0.0

    def print_summary(self):
        """Print analysis summary"""
        print("\n📊 ANALYSIS SUMMARY")
        print("-" * 30)
        
        stats = self.analysis['statistics']
        print(f"Total tracks: {stats['total_tracks']}")
        print(f"MIDI tracks: {stats['midi_tracks']}")
        print(f"Audio tracks: {stats['audio_tracks']}")
        print(f"Total clips: {stats['total_clips']}")
        print(f"Total devices: {stats['total_devices']}")
        print(f"Plugin devices: {stats['plugin_devices']}")
        print(f"Automation envelopes: {stats['automation_envelopes']}")
        print(f"Samples: {stats['samples_count']}")
        
        # Синтезаторы
        synth_count = 0
        for track in self.analysis['tracks']:
            for device in track['devices']:
                if device['type'] in ['PluginDevice', 'AuPluginDevice']:
                    synth_count += 1
        
        print(f"Synthesizer plugins: {synth_count}")
        
        # CC автоматизация
        cc_automation_count = 0
        for track in self.analysis['tracks']:
            for clip in track['clips']:
                cc_automation_count += len(clip.get('cc_automation', []))
            cc_automation_count += len(track['automation'])
            
        print(f"CC automation envelopes: {cc_automation_count}")
        
        if cc_automation_count > 10:
            print("✅ Excellent CC automation density for research!")
        elif cc_automation_count > 5:
            print("⚠️ Moderate CC automation density")
        else:
            print("❌ Low CC automation density")
        
    def run_analysis(self):
        """Запустить полный анализ"""
        print("🚀 Запуск анализа Ableton проекта...")
        print(f"📁 Путь к проекту: {self.project_path}")
        
        # Поиск .als файла
        if not self.find_als_file():
            return False
            
        # Загрузка и парсинг
        if not self.load_and_parse():
            return False
            
        # Анализ компонентов
        self.analyze_project_info()
        self.analyze_tempo_info()
        self.analyze_tracks()
        self.analyze_scenes_and_locators()
        self.analyze_global_automation()
        self.analyze_samples()
        self.calculate_statistics()
        
        # Сохранение результатов
        json_file, report_file = self.save_results()
        
        # Экспорт для исследования синтезаторов
        research_file = self.export_for_synthesizer_research()
        
        print("\n✅ Анализ завершен успешно!")
        print(f"📊 Проанализировано треков: {self.analysis['statistics']['total_tracks']}")
        print(f"🎵 Проанализировано клипов: {self.analysis['statistics']['total_clips']}")
        print(f"🔌 Проанализировано устройств: {self.analysis['statistics']['total_devices']}")
        print(f"📄 Результаты: {json_file.name}, {report_file.name}")
        print(f"🔬 Исследовательские данные: {research_file.name}")
        
        # Показать краткую сводку
        self.print_summary()
        
        return True

def main():
    """Главная функция"""
    if len(sys.argv) != 2:
        print("Использование: python ableton_analyzer.py <путь_к_папке_проекта>")
        print("Пример: python ableton_analyzer.py 'A2ML1 Project'")
        sys.exit(1)
        
    project_path = sys.argv[1]
    
    # Проверка существования папки
    if not os.path.exists(project_path):
        print(f"❌ Папка проекта не найдена: {project_path}")
        sys.exit(1)
        
    try:
        # Создание анализатора и запуск
        analyzer = AbletonProjectAnalyzer(project_path)
        success = analyzer.run_analysis()
        
        if success:
            print("\n🎉 Анализ завершен! Проверьте файлы результатов в папке проекта.")
        else:
            print("\n❌ Анализ завершился с ошибками.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Анализ прерван пользователем.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()