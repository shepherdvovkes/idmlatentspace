#!/usr/bin/env python3
import gzip
import xml.etree.ElementTree as ET
import os
import json
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
import csv
from collections import defaultdict
from datetime import datetime

class AudioMLAnalyzer:
    """Анализатор аудио для машинного обучения в мультимодальном пространстве"""
    
    def __init__(self, als_file_path):
        self.als_file = als_file_path
        self.project_dir = Path(als_file_path).parent
        self.audio_files = {}
        self.analysis_results = {}
        
    def analyze_project_for_ml(self):
        """Полный анализ проекта для ML"""
        print("🎵 Анализ аудио для машинного обучения...")
        
        # 1. Извлечь пути к аудиофайлам из ALS
        audio_references = self.extract_audio_file_references()
        
        # 2. Найти и проанализировать аудиофайлы
        for track_name, file_info in audio_references.items():
            print(f"\n🎧 Анализ трека: {track_name}")
            
            # Найти аудиофайл
            audio_path = self.find_audio_file(file_info)
            
            if audio_path and os.path.exists(audio_path):
                print(f"   Найден файл: {audio_path}")
                
                # Загрузить и проанализировать аудио
                audio_features = self.analyze_audio_file(audio_path, track_name)
                
                if audio_features:
                    self.analysis_results[track_name] = {
                        'file_path': str(audio_path),
                        'track_type': self.determine_track_type_by_audio(audio_features, track_name),
                        'audio_features': audio_features,
                        'ml_descriptors': self.extract_ml_descriptors(audio_features)
                    }
            else:
                print(f"   ⚠️ Аудиофайл не найден: {file_info}")
        
        # 3. Создать ML-дескрипторы для каждого типа трека
        self.create_ml_descriptors()
        
        # 4. Сохранить результаты
        self.save_ml_analysis()
        
        return self.analysis_results
    
    def extract_audio_file_references(self):
        """Извлечь ссылки на аудиофайлы из ALS"""
        print("🔍 Извлечение ссылок на аудиофайлы...")
        
        try:
            with gzip.open(self.als_file, 'rt', encoding='utf-8') as f:
                xml_content = f.read()
            
            root = ET.fromstring(xml_content)
            audio_refs = {}
            
            # Сначала поиск в MIDI треках (басовые треки часто здесь)
            for track in root.iter('MidiTrack'):
                track_name = self.get_track_name(track)
                print(f"   Проверка MIDI трека: {track_name}")
                
                # Поиск аудио клипов (рендеры MIDI)
                for audio_clip in track.findall('.//AudioClip'):
                    clip_name = self.get_clip_name(audio_clip)
                    print(f"     Найден аудио клип: {clip_name}")
                    
                    file_ref = audio_clip.find('.//FileRef')
                    if file_ref is not None:
                        name_elem = file_ref.find('.//Name')
                        path_elem = file_ref.find('.//Path')
                        relative_path = file_ref.find('.//RelativePath')
                        
                        file_info = {
                            'clip_name': clip_name,
                            'track_name': track_name,
                            'name': name_elem.get('Value') if name_elem is not None else None,
                            'path': path_elem.get('Value') if path_elem is not None else None,
                            'relative_path': relative_path.get('Value') if relative_path is not None else None,
                            'is_rendered_midi': True
                        }
                        
                        print(f"       Файл: {file_info['name']}")
                        audio_refs[f"{track_name}_{clip_name}"] = file_info
                
                # Также поиск в Arrangement клипах
                arrangement_clips = track.findall('.//ArrangementClipsListWrapper//AudioClip')
                for audio_clip in arrangement_clips:
                    clip_name = self.get_clip_name(audio_clip)
                    print(f"     Найден arrangement аудио клип: {clip_name}")
                    
                    file_ref = audio_clip.find('.//FileRef')
                    if file_ref is not None:
                        name_elem = file_ref.find('.//Name')
                        
                        file_info = {
                            'clip_name': clip_name,
                            'track_name': track_name,
                            'name': name_elem.get('Value') if name_elem is not None else None,
                            'is_arrangement': True
                        }
                        
                        print(f"       Arrangement файл: {file_info['name']}")
                        audio_refs[f"{track_name}_{clip_name}_arr"] = file_info
            
            # Поиск в аудио треках
            for track in root.iter('AudioTrack'):
                track_name = self.get_track_name(track)
                print(f"   Проверка Audio трека: {track_name}")
                
                # Найти аудиоклипы в треке
                for audio_clip in track.findall('.//AudioClip'):
                    clip_name = self.get_clip_name(audio_clip)
                    print(f"     Найден аудио клип: {clip_name}")
                    
                    # Найти ссылку на файл
                    file_ref = audio_clip.find('.//FileRef')
                    if file_ref is not None:
                        name_elem = file_ref.find('.//Name')
                        path_elem = file_ref.find('.//Path')
                        relative_path = file_ref.find('.//RelativePath')
                        
                        file_info = {
                            'clip_name': clip_name,
                            'track_name': track_name,
                            'name': name_elem.get('Value') if name_elem is not None else None,
                            'path': path_elem.get('Value') if path_elem is not None else None,
                            'relative_path': relative_path.get('Value') if relative_path is not None else None,
                            'is_audio_track': True
                        }
                        
                        print(f"       Файл: {file_info['name']}")
                        audio_refs[f"{track_name}_{clip_name}"] = file_info
            
            # Показать все найденные файлы
            print(f"\n📋 Найдено аудио ссылок: {len(audio_refs)}")
            for key, info in audio_refs.items():
                print(f"   {key}: {info['name']} (трек: {info['track_name']})")
            
            # Если не найдено ссылок, попробовать найти файлы напрямую
            if len(audio_refs) == 0:
                print("\n🔍 Ссылки не найдены, поиск файлов напрямую...")
                direct_files = self.find_audio_files_directly()
                
                for i, file_path in enumerate(direct_files):
                    # Попытаться определить тип трека по имени файла
                    file_name = file_path.name.lower()
                    if any(word in file_name for word in ['bass', 'osirus', '1-']):
                        track_type = 'bass'
                    elif any(word in file_name for word in ['drum', 'coral', 'kit', '2-']):
                        track_type = 'drums'
                    elif any(word in file_name for word in ['master', 'mix']):
                        track_type = 'master'
                    else:
                        track_type = f'unknown_{i}'
                    
                    audio_refs[f"direct_{track_type}"] = {
                        'clip_name': file_path.stem,
                        'track_name': track_type,
                        'name': file_path.name,
                        'path': str(file_path),
                        'is_direct_find': True
                    }
                    print(f"   Найден напрямую: {track_type} -> {file_path.name}")
            
            return audio_refs
            
        except Exception as e:
            print(f"❌ Ошибка извлечения аудио ссылок: {e}")
            return {}
    
    def find_audio_files_directly(self):
        """Прямой поиск аудио файлов в проекте"""
        
        audio_files = []
        search_dirs = [
            self.project_dir,
            self.project_dir / "Samples",
            self.project_dir / "Samples" / "Recorded",
            self.project_dir / "Samples" / "Imported",
            self.project_dir / f"{Path(self.als_file).stem} Project" / "Samples",
        ]
        
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
                
            print(f"     Поиск в: {search_dir}")
            
            for ext in ['.wav', '.aif', '.aiff', '.mp3', '.flac']:
                files = list(search_dir.glob(f"**/*{ext}"))
                audio_files.extend(files)
        
        # Удалить дубликаты
        unique_files = list(set(audio_files))
        
        print(f"     Найдено {len(unique_files)} аудио файлов")
        for f in unique_files:
            print(f"       {f.name}")
        
        return unique_files

    def get_track_name(self, track):
        """Получить имя трека"""
        name_elem = track.find('.//EffectiveName')
        if name_elem is not None and name_elem.get('Value'):
            return name_elem.get('Value')
        
        name_elem = track.find('.//Name')
        if name_elem is not None and name_elem.get('Value'):
            return name_elem.get('Value')
        
        return "Unknown"
    
    def get_clip_name(self, clip):
        """Получить имя клипа"""
        name_elem = clip.find('.//Name')
        if name_elem is not None and name_elem.get('Value'):
            return name_elem.get('Value')
        return "Unknown"
    
    def find_audio_file(self, file_info):
        """Найти аудиофайл на диске"""
        
        print(f"     🔍 Поиск файла для: {file_info}")
        
        # Попробовать разные пути
        possible_paths = []
        
        if file_info.get('name'):
            # Прямое имя файла
            possible_paths.append(self.project_dir / file_info['name'])
            
        if file_info.get('path'):
            # Абсолютный путь
            possible_paths.append(Path(file_info['path']))
            
        if file_info.get('relative_path'):
            # Относительный путь
            possible_paths.append(self.project_dir / file_info['relative_path'])
        
        # Поиск в стандартных папках Ableton
        search_dirs = [
            self.project_dir,
            self.project_dir / "Samples",
            self.project_dir / "Samples" / "Recorded", 
            self.project_dir / "Samples" / "Imported",
            self.project_dir / f"{Path(self.als_file).stem} Project" / "Samples",
            self.project_dir / f"{Path(self.als_file).stem} Project" / "Samples" / "Recorded",
        ]
        
        print(f"       Поиск в папках: {[str(d) for d in search_dirs if d.exists()]}")
        
        # Если имя файла None, попробовать найти по названию трека/клипа
        if file_info.get('name') is None:
            track_name = file_info.get('track_name', '')
            clip_name = file_info.get('clip_name', '')
            
            # Поиск файлов с именами, содержащими название трека
            search_patterns = []
            if 'osirus' in track_name.lower() or 'bass' in track_name.lower():
                search_patterns.extend(['*bass*', '*osirus*', '*1-*'])
            if 'coral' in track_name.lower() or 'kit' in track_name.lower():
                search_patterns.extend(['*drum*', '*coral*', '*kit*', '*2-*'])
            if 'master' in track_name.lower():
                search_patterns.extend(['*master*', '*mix*', '*final*'])
            
            # Добавить общие паттерны
            search_patterns.extend(['*Audio*', '*Recorded*', '*Rendered*'])
            
            print(f"       Поиск по паттернам: {search_patterns}")
            
            for search_dir in search_dirs:
                if not search_dir.exists():
                    continue
                    
                for pattern in search_patterns:
                    # Поиск .wav файлов
                    for ext in ['.wav', '.aif', '.aiff', '.mp3', '.flac']:
                        files = list(search_dir.glob(f"**/{pattern}{ext}"))
                        files.extend(list(search_dir.glob(f"**/{pattern.upper()}{ext}")))
                        possible_paths.extend(files)
        
        # Поиск по имени файла в стандартных папках
        if file_info.get('name'):
            filename = file_info['name']
            for search_dir in search_dirs:
                if search_dir.exists():
                    possible_paths.extend(search_dir.glob(f"**/{filename}"))
                    # Также без расширения
                    name_without_ext = Path(filename).stem
                    for ext in ['.wav', '.aif', '.aiff', '.mp3', '.flac']:
                        possible_paths.extend(search_dir.glob(f"**/{name_without_ext}{ext}"))
        
        print(f"       Найдено потенциальных файлов: {len(possible_paths)}")
        
        # Проверить существование файлов и приоритеты
        valid_files = []
        for path in possible_paths:
            if path.exists() and path.suffix.lower() in ['.wav', '.aif', '.aiff', '.mp3', '.flac']:
                valid_files.append(path)
                print(f"         Валидный: {path}")
        
        if not valid_files:
            print(f"       ❌ Аудиофайлы не найдены")
            return None
        
        # Приоритеты для выбора лучшего файла
        def get_file_priority(file_path):
            name = file_path.name.lower()
            score = 0
            
            # Высокий приоритет для файла, указанного в path
            if file_info.get('path') and str(file_path) in file_info['path']:
                score += 1000
                print(f"           ПРИОРИТЕТ: Точное совпадение с path: +1000")
            
            # Приоритет по имени трека
            track_name = file_info.get('track_name', '').lower()
            if 'bass' in track_name or 'osirus' in track_name:
                if 'bass' in name or 'osirus' in name or '1-' in name:
                    score += 100
            elif 'drum' in track_name or 'coral' in track_name or 'kit' in track_name:
                if 'drum' in name or 'coral' in name or 'kit' in name or '2-' in name:
                    score += 100
            elif 'master' in track_name:
                if 'master' in name or 'mix' in name:
                    score += 100
                # Специальная проверка для 3-Audio файлов из master трека
                if '3-audio' in name and 'master' in track_name:
                    score += 50
            
            # Приоритет по времени (более новые файлы)
            if '181342' in name:  # Конкретный файл из вашего примера
                score += 200
                print(f"           ПРИОРИТЕТ: Целевой файл 181342: +200")
            elif '181421' in name:
                score += 150
            
            # Приоритет по расширению
            if file_path.suffix.lower() == '.wav':
                score += 10
            elif file_path.suffix.lower() in ['.aif', '.aiff']:
                score += 8
            
            print(f"           {file_path.name}: score = {score}")
            return score
        
        # Выбрать файл с наивысшим приоритетом
        best_file = max(valid_files, key=get_file_priority)
        print(f"       ✅ Выбран: {best_file}")
        
        return best_file
    
    def analyze_audio_file(self, audio_path, track_name):
        """Анализ аудиофайла для ML"""
        try:
            print(f"   🎼 Загрузка аудио: {audio_path}")
            
            # Попробовать разные способы загрузки
            y = None
            sr = None
            
            try:
                # Способ 1: librosa (предпочтительный)
                y, sr = librosa.load(audio_path, sr=None)
                print(f"   ✅ Загружено через librosa")
            except Exception as e1:
                print(f"   ⚠️ librosa failed: {e1}")
                try:
                    # Способ 2: soundfile
                    import soundfile as sf
                    y, sr = sf.read(str(audio_path))
                    y = y.astype(np.float32)
                    if len(y.shape) > 1:  # Стерео в моно
                        y = np.mean(y, axis=1)
                    print(f"   ✅ Загружено через soundfile")
                except Exception as e2:
                    print(f"   ⚠️ soundfile failed: {e2}")
                    try:
                        # Способ 3: scipy
                        from scipy.io import wavfile
                        sr, y = wavfile.read(str(audio_path))
                        y = y.astype(np.float32)
                        if len(y.shape) > 1:  # Стерео в моно
                            y = np.mean(y, axis=1)
                        # Нормализация
                        y = y / np.max(np.abs(y)) if np.max(np.abs(y)) > 0 else y
                        print(f"   ✅ Загружено через scipy")
                    except Exception as e3:
                        print(f"   ❌ Все методы загрузки failed: {e1}, {e2}, {e3}")
                        return None
            
            if y is None or sr is None:
                print(f"   ❌ Не удалось загрузить аудио")
                return None
            
            print(f"   📊 Анализ характеристик...")
            print(f"      Длительность: {len(y)/sr:.2f} сек")
            print(f"      Sample rate: {sr} Hz")
            print(f"      Samples: {len(y)}")
            
            # Базовые характеристики
            duration = len(y) / sr
            
            # Проверка на слишком короткие файлы
            if duration < 0.1:
                print(f"   ⚠️ Файл слишком короткий: {duration:.3f} сек")
                return None
            
            # Спектральные характеристики
            stft = librosa.stft(y)
            magnitude = np.abs(stft)
            
            # Извлечь ML-признаки с обработкой ошибок
            features = {
                'basic': self.extract_basic_features(y, sr, duration),
                'spectral': self.extract_spectral_features(y, sr, magnitude),
                'rhythm': self.extract_rhythm_features(y, sr),
                'timbral': self.extract_timbral_features(y, sr, magnitude),
                'frequency_analysis': self.analyze_frequency_content(y, sr),
                'dynamic_analysis': self.analyze_dynamics(y, sr),
            }
            
            print(f"   ✅ Анализ завершен")
            return features
            
        except Exception as e:
            print(f"   ❌ Ошибка анализа аудио: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def extract_basic_features(self, y, sr, duration):
        """Извлечь базовые характеристики"""
        try:
            return {
                'duration': duration,
                'sample_rate': int(sr),
                'n_samples': len(y),
                'rms_energy': float(np.sqrt(np.mean(y**2))),
                'zero_crossing_rate': float(np.mean(librosa.feature.zero_crossing_rate(y))),
            }
        except Exception as e:
            print(f"      ⚠️ Ошибка базовых признаков: {e}")
            return {'duration': duration, 'sample_rate': int(sr), 'n_samples': len(y)}
    
    def extract_spectral_features(self, y, sr, magnitude):
        """Извлечь спектральные характеристики"""
        try:
            return {
                'spectral_centroid': librosa.feature.spectral_centroid(y=y, sr=sr)[0],
                'spectral_rolloff': librosa.feature.spectral_rolloff(y=y, sr=sr)[0],
                'spectral_bandwidth': librosa.feature.spectral_bandwidth(y=y, sr=sr)[0],
                'spectral_contrast': librosa.feature.spectral_contrast(y=y, sr=sr),
            }
        except Exception as e:
            print(f"      ⚠️ Ошибка спектральных признаков: {e}")
            return {}
    
    def extract_rhythm_features(self, y, sr):
        """Извлечь ритмические характеристики"""
        try:
            if len(y) < sr:  # Слишком короткий файл
                return {'tempo': 120.0, 'beat_track': np.array([])}
            
            tempo = librosa.beat.tempo(y=y, sr=sr)[0]
            beat_track = librosa.beat.beat_track(y=y, sr=sr)[1]
            
            return {
                'tempo': float(tempo),
                'beat_track': beat_track,
            }
        except Exception as e:
            print(f"      ⚠️ Ошибка ритмических признаков: {e}")
            return {'tempo': 120.0, 'beat_track': np.array([])}
    
    def extract_timbral_features(self, y, sr, magnitude):
        """Извлечь тембральные характеристики"""
        try:
            return {
                'mfcc': librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13),
                'chroma': librosa.feature.chroma_stft(S=magnitude, sr=sr),
                'tonnetz': librosa.feature.tonnetz(y=y, sr=sr),
            }
        except Exception as e:
            print(f"      ⚠️ Ошибка тембральных признаков: {e}")
            return {}

    def analyze_frequency_content(self, y, sr):
        """Анализ частотного содержания для определения типа трека"""
        
        # FFT для частотного анализа
        fft = np.abs(np.fft.fft(y))
        freqs = np.fft.fftfreq(len(fft), 1/sr)
        
        # Positive frequencies only
        positive_freqs = freqs[:len(freqs)//2]
        positive_fft = fft[:len(fft)//2]
        
        # Frequency bands
        sub_bass = np.sum(positive_fft[(positive_freqs >= 20) & (positive_freqs <= 60)])
        bass = np.sum(positive_fft[(positive_freqs >= 60) & (positive_freqs <= 250)])
        low_mid = np.sum(positive_fft[(positive_freqs >= 250) & (positive_freqs <= 500)])
        mid = np.sum(positive_fft[(positive_freqs >= 500) & (positive_freqs <= 2000)])
        high_mid = np.sum(positive_fft[(positive_freqs >= 2000) & (positive_freqs <= 4000)])
        high = np.sum(positive_fft[(positive_freqs >= 4000) & (positive_freqs <= 8000)])
        very_high = np.sum(positive_fft[positive_freqs >= 8000])
        
        total_energy = np.sum(positive_fft)
        
        return {
            'sub_bass_ratio': float(sub_bass / total_energy) if total_energy > 0 else 0,
            'bass_ratio': float(bass / total_energy) if total_energy > 0 else 0,
            'low_mid_ratio': float(low_mid / total_energy) if total_energy > 0 else 0,
            'mid_ratio': float(mid / total_energy) if total_energy > 0 else 0,
            'high_mid_ratio': float(high_mid / total_energy) if total_energy > 0 else 0,
            'high_ratio': float(high / total_energy) if total_energy > 0 else 0,
            'very_high_ratio': float(very_high / total_energy) if total_energy > 0 else 0,
            'fundamental_freq': float(positive_freqs[np.argmax(positive_fft)]),
            'peak_frequencies': self.find_peak_frequencies(positive_freqs, positive_fft)
        }
    
    def find_peak_frequencies(self, freqs, fft_data, n_peaks=5):
        """Найти пиковые частоты"""
        from scipy.signal import find_peaks
        
        peaks, _ = find_peaks(fft_data, height=np.max(fft_data) * 0.1)
        peak_freqs = freqs[peaks]
        peak_magnitudes = fft_data[peaks]
        
        # Сортировать по магнитуде
        sorted_indices = np.argsort(peak_magnitudes)[::-1]
        top_peaks = peak_freqs[sorted_indices[:n_peaks]]
        
        return [float(freq) for freq in top_peaks]
    
    def analyze_dynamics(self, y, sr):
        """Анализ динамики аудио"""
        
        # RMS в окнах для анализа динамики
        hop_length = 512
        frame_length = 2048
        
        rms = librosa.feature.rms(y=y, hop_length=hop_length, frame_length=frame_length)[0]
        
        # Конвертировать в dB
        rms_db = librosa.amplitude_to_db(rms)
        
        return {
            'dynamic_range_db': float(np.max(rms_db) - np.min(rms_db)),
            'avg_rms_db': float(np.mean(rms_db)),
            'rms_std': float(np.std(rms_db)),
            'peak_to_avg_ratio': float(np.max(rms) / np.mean(rms)) if np.mean(rms) > 0 else 0,
            'crest_factor': float(np.max(np.abs(y)) / np.sqrt(np.mean(y**2))) if np.mean(y**2) > 0 else 0,
        }
    
    def determine_track_type_by_audio(self, features, track_name):
        """Определить тип трека по аудио характеристикам"""
        
        freq_analysis = features['frequency_analysis']
        name_lower = track_name.lower()
        
        print(f"       🔍 Определение типа трека для: {track_name}")
        print(f"         Суб-бас: {freq_analysis['sub_bass_ratio']:.3f}")
        print(f"         Бас: {freq_analysis['bass_ratio']:.3f}")
        print(f"         Средние: {freq_analysis['mid_ratio']:.3f}")
        print(f"         Высокие: {freq_analysis['high_ratio']:.3f}")
        
        # Анализ по имени
        if any(word in name_lower for word in ['bass', 'sub', 'low', 'osirus']):
            print(f"         Тип по имени: BASS")
            return 'bass'
        elif any(word in name_lower for word in ['drum', 'kit', 'beat', 'perc', 'coral']):
            print(f"         Тип по имени: DRUMS")
            return 'drums'
        elif 'master' in name_lower:
            print(f"         Тип по имени: MASTER (полный микс)")
            return 'master'
        
        # Анализ по частотному содержанию для неопределенных треков
        if freq_analysis['sub_bass_ratio'] > 0.25 and freq_analysis['bass_ratio'] > 0.35:
            print(f"         Тип по спектру: BASS (много низких частот)")
            return 'bass'
        elif freq_analysis['high_ratio'] > 0.15 and freq_analysis['very_high_ratio'] > 0.08:
            print(f"         Тип по спектру: DRUMS (много высоких частот)")
            return 'drums'
        elif (freq_analysis['sub_bass_ratio'] + freq_analysis['bass_ratio'] + 
              freq_analysis['mid_ratio'] + freq_analysis['high_ratio']) > 0.8:
            print(f"         Тип по спектру: MASTER (полный спектр)")
            return 'master'
        elif freq_analysis['mid_ratio'] > 0.4:
            print(f"         Тип по спектру: LEAD (средние частоты)")
            return 'lead'
        
        print(f"         Тип: UNKNOWN")
        return 'unknown'
    
    def extract_ml_descriptors(self, features):
        """Извлечь ML дескрипторы для мультимодального обучения"""
        
        # Статистические дескрипторы для каждого признака
        descriptors = {}
        
        # Базовые характеристики
        descriptors['basic'] = features['basic']
        
        # Спектральные дескрипторы (статистика)
        for key, values in features['spectral'].items():
            if hasattr(values, 'shape') and len(values.shape) > 0:
                descriptors[f'{key}_mean'] = float(np.mean(values))
                descriptors[f'{key}_std'] = float(np.std(values))
                descriptors[f'{key}_median'] = float(np.median(values))
                descriptors[f'{key}_min'] = float(np.min(values))
                descriptors[f'{key}_max'] = float(np.max(values))
            else:
                descriptors[key] = float(values)
        
        # MFCC дескрипторы (первые 13 коэффициентов)
        mfcc = features['timbral']['mfcc']
        for i in range(min(13, mfcc.shape[0])):
            descriptors[f'mfcc_{i}_mean'] = float(np.mean(mfcc[i]))
            descriptors[f'mfcc_{i}_std'] = float(np.std(mfcc[i]))
        
        # Хромаграмма (12 полутонов)
        chroma = features['timbral']['chroma']
        for i in range(min(12, chroma.shape[0])):
            descriptors[f'chroma_{i}_mean'] = float(np.mean(chroma[i]))
        
        # Частотные характеристики
        descriptors.update(features['frequency_analysis'])
        
        # Динамические характеристики
        descriptors.update(features['dynamic_analysis'])
        
        # Ритмические характеристики
        descriptors['tempo'] = float(features['rhythm']['tempo'])
        
        return descriptors
    
    def create_ml_descriptors(self):
        """Создать ML дескрипторы для каждого типа трека"""
        
        print("\n🤖 Создание ML дескрипторов...")
        
        # Группировать по типам треков
        tracks_by_type = defaultdict(list)
        for track_name, track_data in self.analysis_results.items():
            track_type = track_data['track_type']
            tracks_by_type[track_type].append(track_data)
        
        # Создать эталонные дескрипторы для каждого типа
        type_descriptors = {}
        
        for track_type, tracks in tracks_by_type.items():
            print(f"   📊 {track_type.upper()} треки ({len(tracks)} шт.)")
            
            if len(tracks) == 0:
                continue
            
            # Усреднить дескрипторы для создания эталона типа
            all_descriptors = [track['ml_descriptors'] for track in tracks]
            
            # Получить все ключи
            all_keys = set()
            for desc in all_descriptors:
                all_keys.update(desc.keys())
            
            # Усреднить каждый дескриптор (только числовые значения)
            averaged_descriptors = {}
            for key in all_keys:
                values = []
                for desc in all_descriptors:
                    if key in desc:
                        value = desc[key]
                        # Проверить что это число, а не словарь или список
                        if isinstance(value, (int, float, np.integer, np.floating)):
                            values.append(float(value))
                        elif isinstance(value, bool):
                            values.append(1.0 if value else 0.0)
                
                if values:  # Если есть числовые значения
                    averaged_descriptors[key] = {
                        'mean': float(np.mean(values)),
                        'std': float(np.std(values)),
                        'min': float(np.min(values)),
                        'max': float(np.max(values)),
                        'count': len(values)
                    }
            
            type_descriptors[track_type] = averaged_descriptors
            
            # Специфический анализ для каждого типа
            if track_type == 'bass':
                self.analyze_bass_audio_characteristics(tracks)
            elif track_type == 'drums':
                self.analyze_drums_audio_characteristics(tracks)
            elif track_type == 'master':
                self.analyze_master_audio_characteristics(tracks)
        
        self.type_descriptors = type_descriptors
    
    def analyze_bass_audio_characteristics(self, bass_tracks):
        """Специальный анализ басовых аудио треков"""
        print("     🎸 Специфический анализ баса:")
        
        for track in bass_tracks:
            features = track['audio_features']
            freq_analysis = features['frequency_analysis']
            
            print(f"       Трек: {track['file_path']}")
            print(f"         Суб-бас энергия: {freq_analysis['sub_bass_ratio']:.3f}")
            print(f"         Бас энергия: {freq_analysis['bass_ratio']:.3f}")
            print(f"         Основная частота: {freq_analysis['fundamental_freq']:.1f} Hz")
            print(f"         Динамический диапазон: {features['dynamic_analysis']['dynamic_range_db']:.1f} dB")
            
            # Анализ для ML: важные признаки баса
            bass_ml_features = {
                'sub_bass_dominance': freq_analysis['sub_bass_ratio'] > 0.25,
                'bass_dominance': freq_analysis['bass_ratio'] > 0.35,
                'low_frequency_focus': freq_analysis['fundamental_freq'] < 200,
                'tight_dynamics': features['dynamic_analysis']['dynamic_range_db'] < 20
            }
            
            track['bass_specific_ml'] = bass_ml_features
    
    def analyze_drums_audio_characteristics(self, drum_tracks):
        """Специальный анализ барабанных аудио треков"""
        print("     🥁 Специфический анализ барабанов:")
        
        for track in drum_tracks:
            features = track['audio_features']
            freq_analysis = features['frequency_analysis']
            dynamic_analysis = features['dynamic_analysis']
            
            print(f"       Трек: {track['file_path']}")
            print(f"         Высокие частоты: {freq_analysis['high_ratio']:.3f}")
            print(f"         Очень высокие: {freq_analysis['very_high_ratio']:.3f}")
            print(f"         Динамический диапазон: {dynamic_analysis['dynamic_range_db']:.1f} dB")
            print(f"         Крест-фактор: {dynamic_analysis['crest_factor']:.2f}")
            
            # Анализ для ML: важные признаки барабанов
            drums_ml_features = {
                'high_frequency_content': freq_analysis['high_ratio'] > 0.15,
                'percussive_transients': dynamic_analysis['crest_factor'] > 3.0,
                'wide_dynamics': dynamic_analysis['dynamic_range_db'] > 25,
                'peak_to_avg_high': dynamic_analysis['peak_to_avg_ratio'] > 2.0
            }
            
            track['drums_specific_ml'] = drums_ml_features
    
    def analyze_master_audio_characteristics(self, master_tracks):
        """Специальный анализ master треков (полный микс)"""
        print("     🎚️ Специфический анализ мастер-трека:")
        
        for track in master_tracks:
            features = track['audio_features']
            freq_analysis = features['frequency_analysis']
            dynamic_analysis = features['dynamic_analysis']
            
            print(f"       Трек: {track['file_path']}")
            print(f"         Полный спектр:")
            print(f"           Суб-бас: {freq_analysis['sub_bass_ratio']:.3f}")
            print(f"           Бас: {freq_analysis['bass_ratio']:.3f}")
            print(f"           Средние: {freq_analysis['mid_ratio']:.3f}")
            print(f"           Высокие: {freq_analysis['high_ratio']:.3f}")
            print(f"         Основная частота: {freq_analysis['fundamental_freq']:.1f} Hz")
            print(f"         Динамический диапазон: {dynamic_analysis['dynamic_range_db']:.1f} dB")
            print(f"         RMS энергия: {features['basic']['rms_energy']:.4f}")
            
            # Анализ для ML: характеристики полного микса
            master_ml_features = {
                'full_spectrum_coverage': (freq_analysis['sub_bass_ratio'] + 
                                         freq_analysis['bass_ratio'] + 
                                         freq_analysis['mid_ratio'] + 
                                         freq_analysis['high_ratio']) > 0.7,
                'balanced_mix': abs(freq_analysis['bass_ratio'] - freq_analysis['mid_ratio']) < 0.2,
                'professional_dynamics': 15 < dynamic_analysis['dynamic_range_db'] < 30,
                'good_loudness': 0.01 < features['basic']['rms_energy'] < 0.5,
                'tempo': features['rhythm']['tempo'],
                'spectral_balance': {
                    'bass_energy': freq_analysis['sub_bass_ratio'] + freq_analysis['bass_ratio'],
                    'mid_energy': freq_analysis['low_mid_ratio'] + freq_analysis['mid_ratio'],
                    'high_energy': freq_analysis['high_ratio'] + freq_analysis['very_high_ratio']
                }
            }
            
            print(f"         ML характеристики:")
            print(f"           Полный спектр: {master_ml_features['full_spectrum_coverage']}")
            print(f"           Сбалансированный микс: {master_ml_features['balanced_mix']}")
            print(f"           Профессиональная динамика: {master_ml_features['professional_dynamics']}")
            print(f"           Темп: {master_ml_features['tempo']:.1f} BPM")
            
            track['master_specific_ml'] = master_ml_features
    
    def save_ml_analysis(self):
        """Сохранить результаты ML анализа"""
        
        # Сохранить полные результаты
        output_file = self.project_dir / 'audio_ml_analysis.json'
        
        # Подготовить данные для сохранения (конвертировать numpy в обычные типы)
        save_data = {
            'project_info': {
                'als_file': str(self.als_file),
                'project_dir': str(self.project_dir),
                'analysis_timestamp': datetime.now().isoformat()
            },
            'tracks': {},
            'type_descriptors': getattr(self, 'type_descriptors', {})
        }
        
        # Конвертировать numpy массивы в списки для JSON
        for track_name, track_data in self.analysis_results.items():
            save_track_data = {}
            
            for key, value in track_data.items():
                if key == 'audio_features':
                    # Конвертировать numpy массивы
                    converted_features = self.convert_numpy_for_json(value)
                    save_track_data[key] = converted_features
                else:
                    save_track_data[key] = value
            
            save_data['tracks'][track_name] = save_track_data
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 ML анализ сохранен: {output_file}")
        
        # Создать CSV с ML дескрипторами для быстрого доступа
        csv_file = self.project_dir / 'ml_descriptors.csv'
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if self.analysis_results:
                # Получить все возможные ключи дескрипторов
                all_keys = set()
                for track_data in self.analysis_results.values():
                    all_keys.update(track_data['ml_descriptors'].keys())
                
                fieldnames = ['track_name', 'track_type', 'file_path'] + sorted(all_keys)
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for track_name, track_data in self.analysis_results.items():
                    row = {
                        'track_name': track_name,
                        'track_type': track_data['track_type'],
                        'file_path': track_data['file_path']
                    }
                    row.update(track_data['ml_descriptors'])
                    writer.writerow(row)
        
        print(f"💾 ML дескрипторы сохранены: {csv_file}")
    
    def convert_numpy_for_json(self, obj):
        """Конвертировать numpy объекты для JSON сериализации"""
        if isinstance(obj, dict):
            return {key: self.convert_numpy_for_json(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_numpy_for_json(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        else:
            return obj

def main():
    """Основная функция"""
    
    # Проверить наличие библиотек
    try:
        import librosa
        import soundfile
        import scipy
    except ImportError as e:
        print(f"❌ Необходимо установить аудио библиотеки:")
        print("pip install librosa soundfile scipy")
        return
    
    als_file = 'A2ML1.als'
    
    if not os.path.exists(als_file):
        print(f"❌ ALS файл не найден: {als_file}")
        return
    
    # Создать анализатор
    analyzer = AudioMLAnalyzer(als_file)
    
    # Запустить анализ
    results = analyzer.analyze_project_for_ml()
    
    if results:
        print(f"\n✅ Анализ завершен. Проанализировано {len(results)} аудио треков.")
        print("\n📊 Результаты:")
        
        for track_name, data in results.items():
            print(f"   🎵 {track_name}: {data['track_type']}")
            print(f"      Файл: {data['file_path']}")
            
            if 'bass_specific_ml' in data:
                bass_ml = data['bass_specific_ml']
                print(f"      Бас характеристики: суб-бас={bass_ml['sub_bass_dominance']}, низкие частоты={bass_ml['low_frequency_focus']}")
            
            if 'drums_specific_ml' in data:
                drums_ml = data['drums_specific_ml']
                print(f"      Барабан характеристики: высокие частоты={drums_ml['high_frequency_content']}, динамика={drums_ml['wide_dynamics']}")
    else:
        print("⚠️ Аудио треки не найдены или не удалось проанализировать")

if __name__ == "__main__":
    main()