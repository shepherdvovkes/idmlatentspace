#!/usr/bin/env python3
"""
Обновленный анализатор пресетов с использованием SysEx Toolkit
"""

# Импорт библиотеки (после установки)
from sysex_toolkit import SysExLibrary, SysExFormat, decode_sysex_file
import numpy as np
import json

class ModernPresetAnalyzer:
    """Современный анализатор пресетов с SysEx Toolkit"""
    
    def __init__(self):
        self.sysex_library = SysExLibrary()
        
    def analyze_user_vs_factory_preset(self, user_preset_file, factory_sysex_file, baseline_name="Contra"):
        """Упрощенный анализ с библиотекой"""
        
        print(f"🎹 Анализ с SysEx Toolkit v1.0.0")
        
        # 1. Загрузить пользовательский пресет
        user_presets = decode_sysex_file(user_preset_file, SysExFormat.ACCESS_VIRUS)
        
        if not user_presets:
            print("❌ Не удалось загрузить пользовательский пресет")
            return None
        
        user_preset = user_presets[0]
        
        # 2. Загрузить фабричные пресеты
        decoder = self.sysex_library.get_decoder(SysExFormat.ACCESS_VIRUS)
        factory_presets = decoder.decode_sysex_file(factory_sysex_file)
        
        print(f"📦 Загружено {len(factory_presets)} фабричных пресетов")
        
        # 3. Найти базовый пресет
        baseline_preset = None
        for preset in factory_presets:
            preset_name = preset['metadata'].get('preset_name', '')
            if baseline_name.lower() in preset_name.lower():
                baseline_preset = preset
                print(f"✅ Найден базовый: {preset_name}")
                break
        
        if not baseline_preset:
            print(f"❌ Базовый пресет '{baseline_name}' не найден")
            return None
        
        # 4. Сравнить параметры
        differences = self.compare_presets(user_preset, baseline_preset)
        
        # 5. Создать редуцированное пространство
        reduced_space = self.create_reduced_space(differences)
        
        return {
            'user_preset': user_preset,
            'baseline_preset': baseline_preset,
            'differences': differences,
            'reduced_space': reduced_space
        }
    
    def compare_presets(self, user_preset, baseline_preset, threshold=0.01):
        """Сравнить два пресета"""
        
        user_params = user_preset['parameters']
        baseline_params = baseline_preset['parameters']
        
        significant_changes = []
        
        for param_name in user_params:
            if param_name in baseline_params:
                user_val = user_params[param_name]['normalized_value']
                baseline_val = baseline_params[param_name]['normalized_value']
                
                difference = abs(user_val - baseline_val)
                
                if difference > threshold:
                    change = {
                        'parameter': param_name,
                        'category': user_params[param_name]['category'],
                        'cc_number': user_params[param_name]['cc_number'],
                        'user_value': user_val,
                        'baseline_value': baseline_val,
                        'difference': difference,
                        'importance': self.calculate_importance(param_name, difference, user_params[param_name])
                    }
                    significant_changes.append(change)
        
        # Сортировать по важности
        significant_changes.sort(key=lambda x: x['importance'], reverse=True)
        
        print(f"🔄 Найдено {len(significant_changes)} значимых изменений")
        
        return significant_changes
    
    def calculate_importance(self, param_name, difference, param_data):
        """Вычислить важность параметра"""
        
        importance = difference * 2.0  # Базовая важность
        
        # CC контроллеры важнее (можно автоматизировать)
        if param_data['cc_number']:
            importance += 1.5
        
        # Фильтровые параметры критичны для Dubstep
        if param_data['category'] == 'filter':
            importance += 1.2
        
        # LFO важен для модуляции
        if param_data['category'] == 'lfo':
            importance += 1.0
        
        # Специальные параметры
        if 'cutoff' in param_name.lower():
            importance += 2.0  # Cutoff сверх-важен
        
        return importance
    
    def create_reduced_space(self, significant_changes, target_dimensions=[32, 64, 128]):
        """Создать редуцированные пространства"""
        
        reduced_spaces = {}
        
        for dim in target_dimensions:
            selected_params = significant_changes[:dim]
            
            # Создать вектор признаков
            feature_vector = []
            feature_names = []
            cc_mappings = {}
            
            for change in selected_params:
                feature_vector.append(change['user_value'])
                feature_names.append(change['parameter'])
                
                if change['cc_number']:
                    cc_mappings[f"CC{change['cc_number']}"] = change['parameter']
            
            # Дополнить до целевой размерности
            while len(feature_vector) < dim:
                feature_vector.append(0.0)
                feature_names.append(f'padding_{len(feature_names)}')
            
            reduced_spaces[f'{dim}d'] = {
                'dimension': dim,
                'feature_vector': np.array(feature_vector[:dim]),
                'feature_names': feature_names[:dim],
                'cc_mappings': cc_mappings,
                'parameters_used': len(selected_params),
                'compression_ratio': dim / 384,  # Сравнение с оригинальными 384D
                'dubstep_ready': any('filter' in change['category'] for change in selected_params[:10])
            }
        
        return reduced_spaces
    
    def save_analysis_results(self, results, output_prefix='sysex_analysis'):
        """Сохранить результаты анализа"""
        
        # Полный анализ
        analysis_data = {
            'metadata': {
                'user_preset_name': results['user_preset']['metadata'].get('preset_name', 'Unknown'),
                'baseline_preset_name': results['baseline_preset']['metadata'].get('preset_name', 'Unknown'),
                'total_differences': len(results['differences']),
                'sysex_toolkit_version': '1.0.0'
            },
            'differences': results['differences'],
            'reduced_spaces': {}
        }
        
        # Конвертировать numpy в списки для JSON
        for space_name, space_data in results['reduced_space'].items():
            analysis_data['reduced_spaces'][space_name] = {
                **space_data,
                'feature_vector': space_data['feature_vector'].tolist()
            }
        
        # Сохранить JSON
        with open(f'{output_prefix}_complete.json', 'w') as f:
            json.dump(analysis_data, f, indent=2, default=str)
        
        # Сохранить векторы отдельно
        for space_name, space_data in results['reduced_space'].items():
            np.save(f'{output_prefix}_{space_name}.npy', space_data['feature_vector'])
        
        # Создать отчет
        self.create_analysis_report(results, f'{output_prefix}_report.txt')
        
        print(f"\n💾 Анализ сохранен:")
        print(f"   - {output_prefix}_complete.json")
        for space_name in results['reduced_space'].keys():
            print(f"   - {output_prefix}_{space_name}.npy")
        print(f"   - {output_prefix}_report.txt")
    
    def create_analysis_report(self, results, report_path):
        """Создать текстовый отчет"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("🎹 ОТЧЕТ АНАЛИЗА ПРЕСЕТОВ (SysEx Toolkit)\n")
            f.write("=" * 50 + "\n\n")
            
            # Метаданные
            user_name = results['user_preset']['metadata'].get('preset_name', 'Unknown')
            baseline_name = results['baseline_preset']['metadata'].get('preset_name', 'Unknown')
            
            f.write(f"Пользовательский пресет