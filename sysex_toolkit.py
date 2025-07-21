#!/usr/bin/env python3
"""
SysEx Toolkit - Универсальная библиотека для декодирования и кодирования SysEx файлов
Поддерживает множественные синтезаторы через конфигурационные файлы
"""

import json
import struct
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

__version__ = "1.0.0"
__author__ = "SystematicLabs"
__email__ = "ovcharov@systematiclabs.com"

class SysExFormat(Enum):
    """Поддерживаемые форматы SysEx"""
    ACCESS_VIRUS = "access_virus"
    ROLAND_JP8000 = "roland_jp8000"
    NOVATION_BASS_STATION = "novation_bass_station"
    KORG_ELECTRIBE = "korg_electribe"
    GENERIC = "generic"

@dataclass
class ParameterDefinition:
    """Определение параметра синтезатора"""
    name: str
    byte_offset: int
    bit_mask: int = 0xFF
    bit_shift: int = 0
    value_range: Tuple[int, int] = (0, 127)
    category: str = "unknown"
    cc_number: Optional[int] = None
    data_type: str = "uint8"  # uint8, uint16, int8, int16, float
    description: str = ""
    
    def normalize_value(self, raw_value: int) -> float:
        """Нормализовать значение в диапазон 0.0-1.0"""
        min_val, max_val = self.value_range
        clamped = max(min_val, min(max_val, raw_value))
        
        if max_val > min_val:
            return (clamped - min_val) / (max_val - min_val)
        return 0.0
    
    def denormalize_value(self, normalized: float) -> int:
        """Конвертировать нормализованное значение обратно в raw"""
        min_val, max_val = self.value_range
        raw_value = int(round(normalized * (max_val - min_val) + min_val))
        return max(min_val, min(max_val, raw_value))

@dataclass
class SysExHeader:
    """Заголовок SysEx сообщения"""
    manufacturer_id: List[int]
    device_id: Optional[int] = None
    model_id: Optional[int] = None
    command: Optional[int] = None
    
    def matches(self, sysex_data: bytes) -> bool:
        """Проверить соответствие заголовка"""
        if len(sysex_data) < len(self.manufacturer_id) + 1:
            return False
        
        # Проверить начало SysEx (0xF0)
        if sysex_data[0] != 0xF0:
            return False
        
        # Проверить manufacturer ID
        manufacturer_bytes = sysex_data[1:1+len(self.manufacturer_id)]
        return list(manufacturer_bytes) == self.manufacturer_id

@dataclass
class SysExDefinition:
    """Полное определение формата SysEx для синтезатора"""
    name: str
    header: SysExHeader
    parameters: Dict[str, ParameterDefinition]
    preset_name_offset: Optional[int] = None
    preset_name_length: Optional[int] = 16
    checksum_offset: Optional[int] = None
    total_length: Optional[int] = None
    version: str = "1.0"
    
    @classmethod
    def from_config_file(cls, config_path: Union[str, Path]) -> 'SysExDefinition':
        """Загрузить определение из конфигурационного файла"""
        
        config_path = Path(config_path)
        
        if config_path.suffix.lower() == '.json':
            with open(config_path, 'r') as f:
                config = json.load(f)
        elif config_path.suffix.lower() in ['.yml', '.yaml']:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        else:
            raise ValueError(f"Неподдерживаемый формат конфигурации: {config_path.suffix}")
        
        return cls.from_dict(config)
    
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'SysExDefinition':
        """Создать определение из словаря"""
        
        # Парсинг заголовка
        header_config = config['header']
        header = SysExHeader(
            manufacturer_id=header_config['manufacturer_id'],
            device_id=header_config.get('device_id'),
            model_id=header_config.get('model_id'),
            command=header_config.get('command')
        )
        
        # Парсинг параметров
        parameters = {}
        for param_name, param_config in config['parameters'].items():
            param = ParameterDefinition(
                name=param_name,
                byte_offset=param_config['byte_offset'],
                bit_mask=param_config.get('bit_mask', 0xFF),
                bit_shift=param_config.get('bit_shift', 0),
                value_range=tuple(param_config.get('value_range', [0, 127])),
                category=param_config.get('category', 'unknown'),
                cc_number=param_config.get('cc_number'),
                data_type=param_config.get('data_type', 'uint8'),
                description=param_config.get('description', '')
            )
            parameters[param_name] = param
        
        return cls(
            name=config['name'],
            header=header,
            parameters=parameters,
            preset_name_offset=config.get('preset_name_offset'),
            preset_name_length=config.get('preset_name_length', 16),
            checksum_offset=config.get('checksum_offset'),
            total_length=config.get('total_length'),
            version=config.get('version', '1.0')
        )

class SysExDecoder:
    """Универсальный декодер SysEx файлов"""
    
    def __init__(self, definition: SysExDefinition):
        self.definition = definition
        
    def decode_file(self, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """Декодировать SysEx файл"""
        
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == '.syx':
            return self.decode_sysex_file(file_path)
        elif file_path.suffix.lower() == '.json':
            return self.decode_json_preset(file_path)
        else:
            raise ValueError(f"Неподдерживаемый формат файла: {file_path.suffix}")
    
    def decode_sysex_file(self, syx_path: Path) -> List[Dict[str, Any]]:
        """Декодировать .syx файл"""
        
        with open(syx_path, 'rb') as f:
            sysex_data = f.read()
        
        # Найти все SysEx сообщения в файле
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
            message = sysex_data[start_pos:end_pos + 1]
            
            # Проверить соответствие заголовку
            if self.definition.header.matches(message):
                decoded = self.decode_sysex_message(message)
                if decoded:
                    presets.append(decoded)
            
            current_pos = end_pos + 1
        
        return presets
    
    def decode_json_preset(self, json_path: Path) -> List[Dict[str, Any]]:
        """Декодировать JSON пресет с SysEx данными"""
        
        with open(json_path, 'r') as f:
            preset_data = json.load(f)
        
        sysex_hex = preset_data.get('sysex', '')
        
        if not sysex_hex:
            raise ValueError("SysEx данные не найдены в JSON файле")
        
        # Конвертировать hex в bytes
        sysex_bytes = bytes.fromhex(sysex_hex.replace(' ', ''))
        
        decoded = self.decode_sysex_message(sysex_bytes)
        
        if decoded:
            # Добавить метаданные из JSON
            decoded['metadata'].update({
                'source_file': str(json_path),
                'plugin': preset_data.get('plugin'),
                'plugin_version': preset_data.get('pluginVersion')
            })
        
        return [decoded] if decoded else []
    
    def decode_sysex_message(self, sysex_data: bytes) -> Optional[Dict[str, Any]]:
        """Декодировать одно SysEx сообщение"""
        
        if not self.definition.header.matches(sysex_data):
            return None
        
        decoded_preset = {
            'parameters': {},
            'metadata': {
                'synthesizer': self.definition.name,
                'sysex_length': len(sysex_data),
                'definition_version': self.definition.version
            },
            'raw_data': {
                'sysex_bytes': sysex_data,
                'sysex_hex': sysex_data.hex(' ')
            }
        }
        
        # Извлечь имя пресета если определено
        if self.definition.preset_name_offset:
            preset_name = self.extract_preset_name(sysex_data)
            decoded_preset['metadata']['preset_name'] = preset_name
        
        # Декодировать параметры
        for param_name, param_def in self.definition.parameters.items():
            value = self.extract_parameter_value(sysex_data, param_def)
            
            if value is not None:
                decoded_preset['parameters'][param_name] = {
                    'raw_value': value,
                    'normalized_value': param_def.normalize_value(value),
                    'category': param_def.category,
                    'cc_number': param_def.cc_number,
                    'description': param_def.description
                }
        
        # Проверить контрольную сумму если определена
        if self.definition.checksum_offset:
            checksum_valid = self.verify_checksum(sysex_data)
            decoded_preset['metadata']['checksum_valid'] = checksum_valid
        
        return decoded_preset
    
    def extract_parameter_value(self, sysex_data: bytes, param_def: ParameterDefinition) -> Optional[int]:
        """Извлечь значение параметра из SysEx данных"""
        
        if param_def.byte_offset >= len(sysex_data):
            return None
        
        if param_def.data_type == 'uint8':
            raw_byte = sysex_data[param_def.byte_offset]
            
            # Применить битовую маску и сдвиг
            value = (raw_byte & param_def.bit_mask) >> param_def.bit_shift
            
            return value
        
        elif param_def.data_type == 'uint16':
            if param_def.byte_offset + 1 >= len(sysex_data):
                return None
            
            # Big-endian 16-bit
            value = (sysex_data[param_def.byte_offset] << 8) | sysex_data[param_def.byte_offset + 1]
            value = (value & param_def.bit_mask) >> param_def.bit_shift
            
            return value
        
        # Другие типы данных можно добавить здесь
        
        return None
    
    def extract_preset_name(self, sysex_data: bytes) -> str:
        """Извлечь имя пресета"""
        
        if not self.definition.preset_name_offset:
            return "Unknown"
        
        start = self.definition.preset_name_offset
        end = start + self.definition.preset_name_length
        
        if end > len(sysex_data):
            end = len(sysex_data)
        
        name_bytes = sysex_data[start:end]
        
        # Конвертировать в строку, убирая null-терминаторы
        try:
            name = name_bytes.decode('ascii').rstrip('\x00').strip()
            return name if name else "Unknown"
        except UnicodeDecodeError:
            return "Unknown"
    
    def verify_checksum(self, sysex_data: bytes) -> bool:
        """Проверить контрольную сумму"""
        
        if not self.definition.checksum_offset:
            return True
        
        # Простая реализация - сумма всех байтов
        checksum_pos = self.definition.checksum_offset
        
        if checksum_pos >= len(sysex_data):
            return False
        
        expected_checksum = sysex_data[checksum_pos]
        
        # Вычислить сумму всех байтов кроме заголовка, хвоста и самой контрольной суммы
        data_sum = sum(sysex_data[1:checksum_pos]) + sum(sysex_data[checksum_pos+1:-1])
        calculated_checksum = (128 - (data_sum % 128)) % 128
        
        return calculated_checksum == expected_checksum

class SysExEncoder:
    """Универсальный кодировщик SysEx файлов"""
    
    def __init__(self, definition: SysExDefinition):
        self.definition = definition
        
    def encode_preset(self, parameters: Dict[str, float], preset_name: str = "Custom") -> bytes:
        """Кодировать пресет в SysEx данные"""
        
        # Определить размер SysEx сообщения
        total_size = self.definition.total_length or 256
        sysex_data = bytearray(total_size)
        
        # Заголовок SysEx
        sysex_data[0] = 0xF0  # Начало SysEx
        
        # Manufacturer ID
        for i, mid in enumerate(self.definition.header.manufacturer_id):
            sysex_data[1 + i] = mid
        
        # Device ID, Model ID, Command если определены
        offset = 1 + len(self.definition.header.manufacturer_id)
        
        if self.definition.header.device_id is not None:
            sysex_data[offset] = self.definition.header.device_id
            offset += 1
        
        if self.definition.header.model_id is not None:
            sysex_data[offset] = self.definition.header.model_id
            offset += 1
        
        if self.definition.header.command is not None:
            sysex_data[offset] = self.definition.header.command
            offset += 1
        
        # Кодировать параметры
        for param_name, param_def in self.definition.parameters.items():
            if param_name in parameters:
                normalized_value = parameters[param_name]
                raw_value = param_def.denormalize_value(normalized_value)
                
                # Записать значение в нужную позицию
                if param_def.data_type == 'uint8':
                    current_byte = sysex_data[param_def.byte_offset]
                    
                    # Очистить биты параметра
                    current_byte &= ~param_def.bit_mask
                    
                    # Установить новое значение
                    new_value = (raw_value << param_def.bit_shift) & param_def.bit_mask
                    current_byte |= new_value
                    
                    sysex_data[param_def.byte_offset] = current_byte
        
        # Записать имя пресета
        if self.definition.preset_name_offset:
            self.encode_preset_name(sysex_data, preset_name)
        
        # Вычислить и записать контрольную сумму
        if self.definition.checksum_offset:
            checksum = self.calculate_checksum(sysex_data)
            sysex_data[self.definition.checksum_offset] = checksum
        
        # Завершить SysEx
        sysex_data[-1] = 0xF7
        
        return bytes(sysex_data)
    
    def encode_preset_name(self, sysex_data: bytearray, preset_name: str):
        """Кодировать имя пресета"""
        
        start = self.definition.preset_name_offset
        max_length = self.definition.preset_name_length
        
        # Ограничить длину имени
        encoded_name = preset_name[:max_length].encode('ascii', errors='replace')
        
        # Дополнить нулями если нужно
        padded_name = encoded_name.ljust(max_length, b'\x00')
        
        # Записать в SysEx данные
        for i, byte_val in enumerate(padded_name):
            if start + i < len(sysex_data):
                sysex_data[start + i] = byte_val
    
    def calculate_checksum(self, sysex_data: bytearray) -> int:
        """Вычислить контрольную сумму"""
        
        checksum_pos = self.definition.checksum_offset
        
        # Сумма всех байтов кроме заголовка, хвоста и самой контрольной суммы
        data_sum = sum(sysex_data[1:checksum_pos]) + sum(sysex_data[checksum_pos+1:-1])
        checksum = (128 - (data_sum % 128)) % 128
        
        return checksum
    
    def save_sysex_file(self, presets: List[Dict[str, float]], file_path: Union[str, Path], 
                       preset_names: Optional[List[str]] = None):
        """Сохранить пресеты в .syx файл"""
        
        file_path = Path(file_path)
        
        with open(file_path, 'wb') as f:
            for i, preset in enumerate(presets):
                preset_name = preset_names[i] if preset_names and i < len(preset_names) else f"Preset_{i+1}"
                sysex_data = self.encode_preset(preset, preset_name)
                f.write(sysex_data)

class SysExLibrary:
    """Библиотека для работы с различными синтезаторами"""
    
    def __init__(self):
        self.definitions = {}
        self.load_builtin_definitions()
    
    def load_builtin_definitions(self):
        """Загрузить встроенные определения синтезаторов"""
        
        # Access Virus C
        self.definitions[SysExFormat.ACCESS_VIRUS] = self.create_access_virus_definition()
        
        # Можно добавить другие синтезаторы
        # self.definitions[SysExFormat.ROLAND_JP8000] = self.create_roland_jp8000_definition()
    
    def create_access_virus_definition(self) -> SysExDefinition:
        """Создать определение для Access Virus C"""
        
        header = SysExHeader(
            manufacturer_id=[0x00, 0x20, 0x33],  # Access Music
            device_id=0x01,
            model_id=0x00
        )
        
        parameters = {
            # Oscillators
            'osc1_octave': ParameterDefinition('osc1_octave', 16, category='oscillator'),
            'osc1_semitone': ParameterDefinition('osc1_semitone', 17, category='oscillator'),
            'osc1_detune': ParameterDefinition('osc1_detune', 18, category='oscillator'),
            'osc1_shape': ParameterDefinition('osc1_shape', 20, category='oscillator'),
            'osc1_pw': ParameterDefinition('osc1_pw', 21, category='oscillator'),
            
            'osc2_octave': ParameterDefinition('osc2_octave', 22, category='oscillator'),
            'osc2_semitone': ParameterDefinition('osc2_semitone', 23, category='oscillator'),
            'osc2_detune': ParameterDefinition('osc2_detune', 24, category='oscillator'),
            'osc2_shape': ParameterDefinition('osc2_shape', 26, category='oscillator'),
            'osc2_pw': ParameterDefinition('osc2_pw', 27, category='oscillator'),
            
            'osc_mix': ParameterDefinition('osc_mix', 28, category='oscillator'),
            'sub_osc_level': ParameterDefinition('sub_osc_level', 29, category='oscillator'),
            'noise_level': ParameterDefinition('noise_level', 30, category='oscillator'),
            
            # Filter (критично для wobble)
            'filter_cutoff': ParameterDefinition('filter_cutoff', 40, category='filter', cc_number=74),
            'filter_resonance': ParameterDefinition('filter_resonance', 41, category='filter', cc_number=71),
            'filter_env_amount': ParameterDefinition('filter_env_amount', 42, category='filter', cc_number=72),
            'filter_type': ParameterDefinition('filter_type', 45, category='filter'),
            'filter_saturation': ParameterDefinition('filter_saturation', 46, category='filter'),
            
            # Envelopes
            'filter_env_attack': ParameterDefinition('filter_env_attack', 60, category='envelope'),
            'filter_env_decay': ParameterDefinition('filter_env_decay', 61, category='envelope'),
            'filter_env_sustain': ParameterDefinition('filter_env_sustain', 62, category='envelope'),
            'filter_env_release': ParameterDefinition('filter_env_release', 63, category='envelope'),
            
            'amp_env_attack': ParameterDefinition('amp_env_attack', 64, category='envelope'),
            'amp_env_decay': ParameterDefinition('amp_env_decay', 65, category='envelope'),
            'amp_env_sustain': ParameterDefinition('amp_env_sustain', 66, category='envelope'),
            'amp_env_release': ParameterDefinition('amp_env_release', 67, category='envelope'),
            
            # LFO
            'lfo1_rate': ParameterDefinition('lfo1_rate', 70, category='lfo', cc_number=76),
            'lfo1_shape': ParameterDefinition('lfo1_shape', 71, category='lfo'),
            'lfo1_amount': ParameterDefinition('lfo1_amount', 72, category='lfo', cc_number=77),
            'lfo1_sync': ParameterDefinition('lfo1_sync', 73, category='lfo'),
            
            # Effects
            'chorus_rate': ParameterDefinition('chorus_rate', 90, category='effects', cc_number=93),
            'delay_time': ParameterDefinition('delay_time', 92, category='effects', cc_number=94),
            'delay_feedback': ParameterDefinition('delay_feedback', 93, category='effects'),
            'distortion_amount': ParameterDefinition('distortion_amount', 95, category='effects', cc_number=80),
        }
        
        return SysExDefinition(
            name="Access Virus C",
            header=header,
            parameters=parameters,
            preset_name_offset=200,  # Примерное расположение
            preset_name_length=16,
            total_length=256
        )
    
    def get_decoder(self, synth_format: Union[SysExFormat, str]) -> SysExDecoder:
        """Получить декодер для синтезатора"""
        
        if isinstance(synth_format, str):
            synth_format = SysExFormat(synth_format)
        
        if synth_format not in self.definitions:
            raise ValueError(f"Неподдерживаемый формат синтезатора: {synth_format}")
        
        return SysExDecoder(self.definitions[synth_format])
    
    def get_encoder(self, synth_format: Union[SysExFormat, str]) -> SysExEncoder:
        """Получить кодировщик для синтезатора"""
        
        if isinstance(synth_format, str):
            synth_format = SysExFormat(synth_format)
        
        if synth_format not in self.definitions:
            raise ValueError(f"Неподдерживаемый формат синтезатора: {synth_format}")
        
        return SysExEncoder(self.definitions[synth_format])
    
    def load_custom_definition(self, config_path: Union[str, Path], 
                              format_name: str) -> SysExFormat:
        """Загрузить пользовательское определение синтезатора"""
        
        definition = SysExDefinition.from_config_file(config_path)
        custom_format = SysExFormat(format_name)
        self.definitions[custom_format] = definition
        
        return custom_format
    
    def list_supported_synthesizers(self) -> List[str]:
        """Получить список поддерживаемых синтезаторов"""
        
        return [fmt.value for fmt in self.definitions.keys()]

# Удобные функции для быстрого использования

def decode_sysex_file(file_path: Union[str, Path], 
                     synth_format: Union[SysExFormat, str] = SysExFormat.ACCESS_VIRUS) -> List[Dict[str, Any]]:
    """Быстро декодировать SysEx файл"""
    
    library = SysExLibrary()
    decoder = library.get_decoder(synth_format)
    return decoder.decode_file(file_path)

def encode_preset_to_sysex(parameters: Dict[str, float], 
                          preset_name: str = "Custom",
                          synth_format: Union[SysExFormat, str] = SysExFormat.ACCESS_VIRUS) -> bytes:
    """Быстро кодировать пресет в SysEx"""
    
    library = SysExLibrary()
    encoder = library.get_encoder(synth_format)
    return encoder.encode_preset(parameters, preset_name)

def create_config_template(synth_name: str, output_path: Union[str, Path]):
    """Создать шаблон конфигурации для нового синтезатора"""
    
    template = {
        "name": synth_name,
        "version": "1.0",
        "header": {
            "manufacturer_id": [0x00, 0x00, 0x00],  # Заменить на реальный ID
            "device_id": 0x01,
            "model_id": 0x00,
            "command": 0x10
        },
        "preset_name_offset": 100,
        "preset_name_length": 16,
        "checksum_offset": 200,
        "total_length": 256,
        "parameters": {
            "example_parameter": {
                "byte_offset": 10,
                "bit_mask": 255,
                "bit_shift": 0,
                "value_range": [0, 127],
                "category": "oscillator",
                "cc_number": 74,
                "data_type": "uint8",
                "description": "Example parameter description"
            }
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"✅ Шаблон конфигурации создан: {output_path}")

# Пример использования
if __name__ == "__main__":
    
    # Создать библиотеку
    library = SysExLibrary()
    
    print("🎹 SysEx Toolkit v1.0.0")
    print(f"Поддерживаемые синтезаторы: {library.list_supported_synthesizers()}")
    
    # Пример декодирования
    try:
        # Декодировать пресет Osirus
        presets = decode_sysex_file('osiris_preset.txt', SysExFormat.ACCESS_VIRUS)
        
        if presets:
            preset = presets[0]
            print(f"\n✅ Декодирован пресет: {preset['metadata'].get('preset_name', 'Unknown')}")
            print(f"   Параметров: {len(preset['parameters'])}")
            
            # Показать несколько параметров
            for param_name, param_data in list(preset['parameters'].items())[:5]:
                cc_info = f" (CC{param_data['cc_number']})" if param_data['cc_number'] else ""
                print(f"   {param_name}{cc_info}: {param_data['normalized_value']:.3f}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Создать шаблон конфигурации
    create_config_template("Custom Synthesizer