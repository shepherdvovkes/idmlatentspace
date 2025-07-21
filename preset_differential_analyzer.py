#!/usr/bin/env python3
"""
Анализатор различий пресетов для редукции латентного пространства
Сравнивает пользовательский пресет с фабричными для выделения значимых параметров
"""

import numpy as np
import json
from collections import OrderedDict
import struct

class PresetDifferentialAnalyzer:
    """Анализатор различий между пресетами для редукции размерности"""
    
    def __init__(self, osirus_decoder):
        self.decoder = osirus_decoder
        self.factory_presets = {}
        self.significant_parameters = []
        self.reduced_latent_dimensions = {}
        
    def load_factory_presets(self, factory_sysex_file):
        """Загрузить все фабричные пресеты из .syx файла"""
        
        print(f"📦 Загрузка фабричных пресетов из {factory_sysex_file}...")
        
        try:
            with open(factory_sysex_file, 'rb') as f:
                sysex_data = f.read()
            
            # Парсинг множественных SysEx сообщений
            presets = self.parse_multiple_sysex(sysex_data)
            
            print(f"✅ Загружено {len(presets)} фабричных пресетов")
            
            # Декодировать каждый пресет
            for i, preset_sysex in enumerate(presets):
                preset_name = self.extract_preset_name(preset_sysex)
                
                if not preset_name:
                    preset_name = f"Factory_Preset_{i+1}"
                
                # Декодировать параметры
                decoded = self.decoder.decode_sysex_bytes(preset_sysex)
                
                if decoded:
                    self.factory_presets[preset_name] = {
                        'sysex_data': preset_sysex,
                        'parameters': decoded,
                        'preset_index': i
                    }
                    
                    print(f"   {i+1:3d}. {preset_name}")
            
            return len(self.factory_presets)
            
        except Exception as e:
            print(f"❌ Ошибка загрузки фабричных пресетов: {e}")
            return 0
    
    def parse_multiple_sysex(self, sysex_data):
        """Парсинг множественных SysEx сообщений из одного файла"""
        
        presets = []
        current_pos = 0
        
        while current_pos < len(sysex_data):
            # Найти начало SysEx (0xF0)
            start_pos = sysex_data.find(0xF0, current_pos)
            
            if start_pos == -1:
                break
            
            # Найти конец SysEx (0xF7)
            end_pos = sysex_data.find(0xF7, start_pos)
            
            if end_pos == -1:
                break
            
            # Извлечь SysEx сообщение
            preset_sysex = sysex_data[start_pos:end_pos + 1]
            
            # Проверить что это Access Virus SysEx
            if self.is_virus_sysex(preset_sysex):
                presets.append(preset_sysex)
            
            current_pos = end_pos + 1
        
        return presets
    
    def is_virus_sysex(self, sysex_bytes):
        """Проверить что это SysEx Access Virus"""
        
        # Access Virus SysEx: F0 00 20 33 01 00
        virus_header = bytes([0xF0, 0x00, 0x20, 0x33, 0x01, 0x00])
        
        return len(sysex_bytes) >= len(virus_header) and sysex_bytes[:len(virus_header)] == virus_header
    
    def extract_preset_name(self, sysex_bytes):
        """Извлечь имя пресета из SysEx данных"""
        
        # Имя пресета обычно находится в конце SysEx сообщения
        # Для Access Virus C это ASCII строка перед 0xF7
        
        try:
            # Поиск ASCII текста в конце сообщения
            name_bytes = []
            
            # Начинаем с конца и ищем printable ASCII
            for i in range(len(sysex_bytes) - 20, len(sysex_bytes) - 1):
                if i >= 0 and 32 <= sysex_bytes[i] <= 126:  # Printable ASCII
                    name_bytes.append(sysex_bytes[i])
                elif name_bytes:  # Если уже собрали имя и встретили non-ASCII
                    break
            
            if name_bytes:
                preset_name = bytes(name_bytes).decode('ascii').strip()
                return preset_name if preset_name else None
            
        except:
            pass
        
        return None
    
    def find_baseline_preset(self, target_name="Contra"):
        """Найти базовый пресет по имени"""
        
        print(f"🔍 Поиск базового пресета '{target_name}'...")
        
        # Поиск по точному совпадению
        for preset_name, preset_data in self.factory_presets.items():
            if target_name.lower() in preset_name.lower():
                print(f"✅ Найден базовый пресет: '{preset_name}'")
                return preset_name, preset_data
        
        # Поиск по частичному совпадению
        candidates = []
        for preset_name, preset_data in self.factory_presets.items():
            if any(word in preset_name.lower() for word in target_name.lower().split()):
                candidates.append((preset_name, preset_data))
        
        if candidates:
            print(f"📋 Найдены кандидаты:")
            for i, (name, _) in enumerate(candidates):
                print(f"   {i+1}. {name}")
            
            # Вернуть первый кандидат
            return candidates[0]
        
        print(f"❌ Базовый пресет '{target_name}' не найден")
        return None, None
    
    def compare_presets(self, user_preset_data, baseline_preset_data, threshold=0.01):
        """Сравнить пользовательский пресет с базовым"""
        
        print(f"🔍 Сравнение пресетов (порог различий: {threshold})...")
        
        user_params = user_preset_data['parameters']
        baseline_params = baseline_preset_data['parameters']
        
        differences = {}
        significant_changes = []
        
        # Сравнить каждый параметр
        for param_name in user_params.keys():
            if param_name == 'meta':
                continue
            
            if param_name in baseline_params:
                user_val = user_params[param_name]['normalized_value']
                baseline_val = baseline_params[param_name]['normalized_value']
                
                difference = abs(user_val - baseline_val)
                
                differences[param_name] = {
                    'user_value': user_val,
                    'baseline_value': baseline_val,
                    'difference': difference,
                    'relative_change': difference / (baseline_val + 1e-8),  # Избежать деления на 0
                    'category': user_params[param_name]['category'],
                    'cc_number': user_params[param_name].get('cc_number'),
                    'is_significant': difference > threshold
                }
                
                if difference > threshold:
                    significant_changes.append({
                        'parameter': param_name,
                        'category': user_params[param_name]['category'],
                        'difference': difference,
                        'user_value': user_val,
                        'baseline_value': baseline_val,
                        'cc_number': user_params[param_name].get('cc_number')
                    })
        
        # Сортировать по величине изменения
        significant_changes.sort(key=lambda x: x['difference'], reverse=True)
        
        print(f"✅ Найдено {len(significant_changes)} значимых изменений")
        
        return differences, significant_changes
    
    def analyze_parameter_importance(self, significant_changes):
        """Анализ важности измененных параметров"""
        
        print(f"\n📊 АНАЛИЗ ВАЖНОСТИ ПАРАМЕТРОВ:")
        
        # Группировка по категориям
        category_changes = {}
        cc_mapped_changes = []
        
        for change in significant_changes:
            category = change['category']
            
            if category not in category_changes:
                category_changes[category] = []
            
            category_changes[category].append(change)
            
            if change['cc_number']:
                cc_mapped_changes.append(change)
        
        # Вывод по категориям
        for category, changes in category_changes.items():
            print(f"\n   🎛️ {category.upper()} ({len(changes)} параметров):")
            
            for change in changes[:5]:  # Топ 5 в категории
                cc_info = f" (CC{change['cc_number']})" if change['cc_number'] else ""
                print(f"      {change['parameter']}{cc_info}: {change['baseline_value']:.3f} → {change['user_value']:.3f} (Δ{change['difference']:.3f})")
        
        # CC маппированные параметры (критично для автоматизации)
        if cc_mapped_changes:
            print(f"\n   🎚️ CC АВТОМАТИЗИРУЕМЫЕ ({len(cc_mapped_changes)} параметров):")
            for change in cc_mapped_changes:
                print(f"      CC{change['cc_number']}: {change['parameter']} (Δ{change['difference']:.3f})")
        
        return category_changes, cc_mapped_changes
    
    def create_reduced_latent_space(self, significant_changes, target_dimensions=[32, 64, 128]):
        """Создать редуцированное латентное пространство"""
        
        print(f"\n🎯 СОЗДАНИЕ РЕДУЦИРОВАННОГО ЛАТЕНТНОГО ПРОСТРАНСТВА:")
        
        # Ранжировать параметры по важности
        importance_scores = []
        
        for change in significant_changes:
            # Комплексная оценка важности
            importance = (
                change['difference'] * 2.0 +  # Величина изменения
                (1.0 if change['cc_number'] else 0.0) * 1.5 +  # CC маппинг
                (1.0 if change['category'] == 'filter' else 0.0) * 1.2 +  # Фильтр важен для wobble
                (1.0 if change['category'] == 'lfo' else 0.0) * 1.0 +  # LFO важен для модуляции
                (1.0 if change['category'] == 'effects' else 0.0) * 0.8  # Эффекты менее критичны
            )
            
            importance_scores.append({
                'parameter': change['parameter'],
                'importance': importance,
                'change_data': change
            })
        
        # Сортировать по важности
        importance_scores.sort(key=lambda x: x['importance'], reverse=True)
        
        # Создать редуцированные пространства разной размерности
        reduced_spaces = {}
        
        for target_dim in target_dimensions:
            selected_params = importance_scores[:target_dim]
            
            reduced_spaces[f'{target_dim}d'] = {
                'dimension': target_dim,
                'selected_parameters': [p['parameter'] for p in selected_params],
                'importance_scores': [p['importance'] for p in selected_params],
                'parameter_details': selected_params,
                'coverage': len(selected_params) / len(significant_changes) if significant_changes else 0
            }
            
            print(f"   📐 {target_dim}D пространство: {len(selected_params)} параметров ({reduced_spaces[f'{target_dim}d']['coverage']:.1%} покрытие)")
        
        self.reduced_latent_dimensions = reduced_spaces
        return reduced_spaces
    
    def create_reduced_feature_vectors(self, user_preset_data, reduced_space_config):
        """Создать редуцированные векторы признаков"""
        
        user_params = user_preset_data['parameters']
        
        reduced_vectors = {}
        
        for space_name, config in reduced_space_config.items():
            dimension = config['dimension']
            selected_params = config['selected_parameters']
            
            # Извлечь значения только выбранных параметров
            feature_vector = []
            feature_names = []
            
            for param_name in selected_params:
                if param_name in user_params:
                    feature_vector.append(user_params[param_name]['normalized_value'])
                    feature_names.append(param_name)
            
            # Дополнить до целевой размерности если нужно
            while len(feature_vector) < dimension:
                feature_vector.append(0.0)
                feature_names.append(f'padding_{len(feature_names)}')
            
            # Обрезать если превышает
            feature_vector = feature_vector[:dimension]
            feature_names = feature_names[:dimension]
            
            reduced_vectors[space_name] = {
                'vector': np.array(feature_vector),
                'feature_names': feature_names,
                'dimension': dimension,
                'non_zero_features': len([x for x in feature_vector if x > 0.001])
            }
        
        return reduced_vectors
    
    def validate_reduction_quality(self, original_latent_features, reduced_vectors):
        """Оценить качество редукции размерности"""
        
        print(f"\n📈 ОЦЕНКА КАЧЕСТВА РЕДУКЦИИ:")
        
        validation_results = {}
        
        # Оригинальные векторы
        orig_384d = original_latent_features['feature_vector_384d']
        orig_512d = original_latent_features['feature_vector_512d']
        
        for space_name, reduced_data in reduced_vectors.items():
            reduced_vector = reduced_data['vector']
            dimension = reduced_data['dimension']
            
            # Metrics
            information_retention = reduced_data['non_zero_features'] / dimension
            compression_ratio = dimension / len(orig_384d)
            
            # Dubstep характеристики сохранены?
            dubstep_features = original_latent_features['dubstep_features']
            wobble_preserved = any('filter' in name for name in reduced_data['feature_names'][:10])
            lfo_preserved = any('lfo' in name for name in reduced_data['feature_names'][:10])
            
            validation_results[space_name] = {
                'dimension': dimension,
                'information_retention': information_retention,
                'compression_ratio': compression_ratio,
                'dubstep_features_preserved': {
                    'wobble_components': wobble_preserved,
                    'lfo_components': lfo_preserved,
                    'overall_preservation': (wobble_preserved and lfo_preserved)
                },
                'efficiency_score': information_retention / compression_ratio
            }
            
            print(f"   🎯 {space_name.upper()}:")
            print(f"      Информация: {information_retention:.1%}")
            print(f"      Сжатие: {compression_ratio:.3f}x")
            print(f"      Wobble сохранен: {'✅' if wobble_preserved else '❌'}")
            print(f"      LFO сохранен: {'✅' if lfo_preserved else '❌'}")
            print(f"      Эффективность: {validation_results[space_name]['efficiency_score']:.2f}")
        
        return validation_results
    
    def analyze_user_vs_factory_preset(self, user_preset_file, factory_sysex_file, baseline_name="Contra"):
        """Полный анализ различий пользователя vs фабричный пресет"""
        
        print(f"🔍 ПОЛНЫЙ ДИФФЕРЕНЦИАЛЬНЫЙ АНАЛИЗ")
        print(f"   User preset: {user_preset_file}")
        print(f"   Factory presets: {factory_sysex_file}")
        print(f"   Baseline: {baseline_name}")
        
        # 1. Загрузить фабричные пресеты
        factory_count = self.load_factory_presets(factory_sysex_file)
        
        if factory_count == 0:
            print("❌ Не удалось загрузить фабричные пресеты")
            return None
        
        # 2. Найти базовый пресет
        baseline_name, baseline_data = self.find_baseline_preset(baseline_name)
        
        if not baseline_data:
            print("❌ Базовый пресет не найден")
            return None
        
        # 3. Загрузить пользовательский пресет
        user_ml_data = self.decoder.analyze_preset_for_ml(user_preset_file)
        
        if not user_ml_data:
            print("❌ Не удалось загрузить пользовательский пресет")
            return None
        
        # 4. Сравнить пресеты
        differences, significant_changes = self.compare_presets(
            user_ml_data, baseline_data, threshold=0.01
        )
        
        # 5. Анализ важности параметров
        category_changes, cc_changes = self.analyze_parameter_importance(significant_changes)
        
        # 6. Создать редуцированное латентное пространство
        reduced_spaces = self.create_reduced_latent_space(significant_changes)
        
        # 7. Создать редуцированные векторы
        reduced_vectors = self.create_reduced_feature_vectors(user_ml_data, reduced_spaces)
        
        # 8. Валидация качества редукции
        validation = self.validate_reduction_quality(
            user_ml_data['latent_features'], reduced_vectors
        )
        
        # Собрать результаты
        analysis_results = {
            'user_preset': user_preset_file,
            'baseline_preset': baseline_name,
            'factory_presets_count': factory_count,
            'differences_analysis': {
                'total_parameters': len(differences),
                'significant_changes': len(significant_changes),
                'differences_by_parameter': differences,
                'top_changes': significant_changes
            },
            'importance_analysis': {
                'category_changes': category_changes,
                'cc_mapped_changes': cc_changes
            },
            'reduced_latent_spaces': reduced_spaces,
            'reduced_vectors': {k: {**v, 'vector': v['vector'].tolist()} for k, v in reduced_vectors.items()},
            'validation_results': validation,
            'recommendations': self.generate_recommendations(validation, significant_changes)
        }
        
        return analysis_results
    
    def generate_recommendations(self, validation_results, significant_changes):
        """Генерировать рекомендации по выбору размерности"""
        
        recommendations = {
            'optimal_dimension': None,
            'reasoning': [],
            'trade_offs': {},
            'ml_training_advice': []
        }
        
        # Найти оптимальную размерность
        best_efficiency = 0
        best_dimension = None
        
        for space_name, metrics in validation_results.items():
            efficiency = metrics['efficiency_score']
            
            if efficiency > best_efficiency and metrics['dubstep_features_preserved']['overall_preservation']:
                best_efficiency = efficiency
                best_dimension = space_name
        
        recommendations['optimal_dimension'] = best_dimension
        
        # Рассуждения
        if len(significant_changes) <= 32:
            recommendations['reasoning'].append("32D достаточно - мало значимых изменений")
        elif len(significant_changes) <= 64:
            recommendations['reasoning'].append("64D рекомендуется - умеренная сложность")
        else:
            recommendations['reasoning'].append("128D необходимо - высокая сложность изменений")
        
        # Советы для ML
        cc_count = len([c for c in significant_changes if c.get('cc_number')])
        
        if cc_count > 5:
            recommendations['ml_training_advice'].append("Высокий потенциал автоматизации - фокус на CC events")
        
        filter_changes = len([c for c in significant_changes if c['category'] == 'filter'])
        if filter_changes > 2:
            recommendations['ml_training_advice'].append("Активная фильтровая модуляция - идеально для Dubstep")
        
        return recommendations
    
    def save_differential_analysis(self, analysis_results, output_prefix='differential_analysis'):
        """Сохранить результаты дифференциального анализа"""
        
        # Полный анализ
        with open(f'{output_prefix}_complete.json', 'w') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        
        # Редуцированные векторы
        for space_name, vector_data in analysis_results['reduced_vectors'].items():
            np.save(f'{output_prefix}_{space_name}.npy', np.array(vector_data['vector']))
        
        # Отчет с рекомендациями
        with open(f'{output_prefix}_recommendations.json', 'w') as f:
            json.dump(analysis_results['recommendations'], f, indent=2)
        
        print(f"\n💾 Дифференциальный анализ сохранен:")
        print(f"   - {output_prefix}_complete.json")
        for space_name in analysis_results['reduced_vectors'].keys():
            print(f"   - {output_prefix}_{space_name}.npy")
        print(f"   - {output_prefix}_recommendations.json")


def main():
    """Главная функция дифференциального анализа"""
    
    # Импортировать декодер Osirus
    from osirus_preset_decoder import OsirusPresetDecoder
    
    # Создать анализатор
    decoder = OsirusPresetDecoder()
    analyzer = PresetDifferentialAnalyzer(decoder)
    
    # Провести дифференциальный анализ
    results = analyzer.analyze_user_vs_factory_preset(
        user_preset_file='osiris_preset.txt',
        factory_sysex_file='osiris_all_presets.syx',
        baseline_name='Contra'
    )
    
    if results:
        print(f"\n🎯 РЕЗУЛЬТАТЫ ДИФФЕРЕНЦИАЛЬНОГО АНАЛИЗА:")
        
        diff_analysis = results['differences_analysis']
        print(f"   📊 Всего параметров: {diff_analysis['total_parameters']}")
        print(f"   🔄 Значимых изменений: {diff_analysis['significant_changes']}")
        
        recommendations = results['recommendations']
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        print(f"   🎯 Оптимальная размерность: {recommendations['optimal_dimension']}")
        
        for reason in recommendations['reasoning']:
            print(f"   💭 {reason}")
        
        for advice in recommendations['ml_training_advice']:
            print(f"   🤖 {advice}")
        
        # Сохранить результаты
        analyzer.save_differential_analysis(results)
        
        print(f"\n✅ Дифференциальный анализ завершен!")
        print(f"   Редуцированное латентное пространство готово для ML обучения")
        
    else:
        print("❌ Дифференциальный анализ не удался")


if __name__ == "__main__":
    main()