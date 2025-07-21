#!/bin/bash

# SysEx Toolkit Package Creator
# Создает полную структуру пакета для установки через pip

set -e  # Остановить при ошибке

echo "🎹 SysEx Toolkit Package Creator"
echo "=================================="

# Проверить наличие исходного файла
PACKAGE_FILE="package_files.py"
if [ ! -f "$PACKAGE_FILE" ]; then
    echo "❌ Файл $PACKAGE_FILE не найден в текущем каталоге"
    echo "   Создайте файл package_files.py с содержимым артефакта"
    exit 1
fi

echo "✅ Найден файл $PACKAGE_FILE"

# Создать структуру папок
echo "📁 Создание структуры папок..."

mkdir -p sysex-toolkit
cd sysex-toolkit

mkdir -p sysex_toolkit/configs
mkdir -p examples
mkdir -p tests

echo "✅ Структура папок создана"

# Функция для извлечения секции из файла
extract_section() {
    local section_name="$1"
    local output_file="$2"
    local start_marker="# $section_name"
    local end_marker="# ================================================================================"
    
    echo "📝 Создание $output_file..."
    
    # Найти начало и конец секции
    local start_line=$(grep -n "^$start_marker" "../$PACKAGE_FILE" | head -1 | cut -d: -f1)
    local end_line=$(sed -n "${start_line},\$p" "../$PACKAGE_FILE" | grep -n "^$end_marker" | head -1 | cut -d: -f1)
    
    if [ -z "$start_line" ]; then
        echo "⚠️  Секция '$section_name' не найдена, создаю базовый файл"
        return 1
    fi
    
    if [ -z "$end_line" ]; then
        # Если нет разделителя, берем до конца файла
        sed -n "${start_line}p,\$p" "../$PACKAGE_FILE" | tail -n +2 > "$output_file"
    else
        # Вычислить абсолютный номер строки конца
        end_line=$((start_line + end_line - 2))
        sed -n "$((start_line + 1)),${end_line}p" "../$PACKAGE_FILE" > "$output_file"
    fi
    
    echo "✅ $output_file создан"
}

# Создать setup.py
extract_section "setup.py" "setup.py"

# Создать requirements.txt
extract_section "requirements.txt" "requirements.txt"

# Создать README.md
extract_section "README.md" "README.md"

# Создать LICENSE
extract_section "LICENSE" "LICENSE"

# Создать __init__.py
extract_section "sysex_toolkit/__init__.py" "sysex_toolkit/__init__.py"

# Создать utils.py
extract_section "sysex_toolkit/utils.py" "sysex_toolkit/utils.py"

# Создать cli.py
extract_section "sysex_toolkit/cli.py" "sysex_toolkit/cli.py"

# Создать example
extract_section "examples/basic_usage.py" "examples/basic_usage.py"

# Создать core.py из исходного sysex_toolkit.py
echo "📝 Создание sysex_toolkit/core.py..."
if [ -f "../sysex_toolkit.py" ]; then
    # Извлечь основные классы из sysex_toolkit.py
    cat > sysex_toolkit/core.py << 'EOF'
#!/usr/bin/env python3
"""
Core classes for SysEx Toolkit
Extracted from sysex_toolkit.py
"""

import json
import struct
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

EOF
    
    # Добавить содержимое исходного файла (без примеров и main)
    grep -v "if __name__ == \"__main__\":" "../sysex_toolkit.py" | \
    grep -A 10000 "class SysExFormat" >> sysex_toolkit/core.py
    
    echo "✅ sysex_toolkit/core.py создан из исходного файла"
else
    echo "⚠️  Файл sysex_toolkit.py не найден, создаю базовый core.py"
    cat > sysex_toolkit/core.py << 'EOF'
# Basic core.py - add your SysEx classes here
from enum import Enum

class SysExFormat(Enum):
    ACCESS_VIRUS = "access_virus"
    GENERIC = "generic"

# Add other classes from your sysex_toolkit.py here
EOF
fi

# Создать analyzer.py
echo "📝 Создание sysex_toolkit/analyzer.py..."
cat > sysex_toolkit/analyzer.py << 'EOF'
"""
SysEx Analyzer for unknown formats
"""

from typing import Dict, Any, List, Union
from pathlib import Path

class SysExAnalyzer:
    """Analyzer for unknown SysEx formats"""
    
    @staticmethod
    def analyze_unknown_sysex(file_path: Union[str, Path]) -> Dict[str, Any]:
        """Analyze unknown SysEx file"""
        
        with open(file_path, 'rb') as f:
            data = f.read()
        
        analysis = {
            'file_size': len(data),
            'sysex_messages': [],
            'manufacturer_analysis': {}
        }
        
        # Find all SysEx messages
        current_pos = 0
        message_count = 0
        
        while current_pos < len(data):
            start_pos = data.find(0xF0, current_pos)
            if start_pos == -1:
                break
            
            end_pos = data.find(0xF7, start_pos)
            if end_pos == -1:
                break
            
            message = data[start_pos:end_pos + 1]
            message_count += 1
            
            message_info = {
                'message_id': message_count,
                'start_offset': start_pos,
                'length': len(message),
                'manufacturer_id': list(message[1:4]) if len(message) > 3 else [],
                'hex_preview': message[:16].hex(' ') + ('...' if len(message) > 16 else ''),
            }
            
            analysis['sysex_messages'].append(message_info)
            current_pos = end_pos + 1
        
        return analysis
EOF

# Создать batch.py
echo "📝 Создание sysex_toolkit/batch.py..."
cat > sysex_toolkit/batch.py << 'EOF'
"""
Batch processor for multiple SysEx files
"""

from typing import Dict, Any, List, Union
from pathlib import Path
import json

class SysExBatchProcessor:
    """Batch processor for multiple files"""
    
    def __init__(self, library):
        self.library = library
    
    def batch_decode(self, input_dir: Union[str, Path], 
                    synth_format,
                    output_format: str = 'json') -> Dict[str, Any]:
        """Batch decode files"""
        
        input_dir = Path(input_dir)
        decoder = self.library.get_decoder(synth_format)
        
        results = {
            'processed_files': [],
            'failed_files': [],
            'total_presets': 0
        }
        
        # Find SysEx files
        sysex_files = list(input_dir.glob('*.syx')) + list(input_dir.glob('*.json'))
        
        for file_path in sysex_files:
            try:
                presets = decoder.decode_file(file_path)
                
                if presets and output_format == 'json':
                    output_path = input_dir / f"{file_path.stem}_decoded.json"
                    with open(output_path, 'w') as f:
                        json.dump(presets, f, indent=2, default=str)
                
                results['processed_files'].append({
                    'input_file': str(file_path),
                    'preset_count': len(presets) if presets else 0
                })
                
                results['total_presets'] += len(presets) if presets else 0
                
            except Exception as e:
                results['failed_files'].append({
                    'file': str(file_path),
                    'error': str(e)
                })
        
        return results
EOF

# Создать конфигурацию Access Virus
echo "📝 Создание sysex_toolkit/configs/access_virus.json..."
cat > sysex_toolkit/configs/access_virus.json << 'EOF'
{
  "name": "Access Virus C",
  "version": "1.0",
  "header": {
    "manufacturer_id": [0, 32, 51],
    "device_id": 1,
    "model_id": 0
  },
  "preset_name_offset": 200,
  "preset_name_length": 16,
  "total_length": 256,
  "parameters": {
    "filter_cutoff": {
      "byte_offset": 40,
      "bit_mask": 255,
      "bit_shift": 0,
      "value_range": [0, 127],
      "category": "filter",
      "cc_number": 74,
      "data_type": "uint8",
      "description": "Filter cutoff frequency"
    },
    "filter_resonance": {
      "byte_offset": 41,
      "bit_mask": 255,
      "bit_shift": 0,
      "value_range": [0, 127],
      "category": "filter", 
      "cc_number": 71,
      "data_type": "uint8",
      "description": "Filter resonance"
    },
    "filter_env_amount": {
      "byte_offset": 42,
      "bit_mask": 255,
      "bit_shift": 0,
      "value_range": [0, 127],
      "category": "filter",
      "cc_number": 72,
      "data_type": "uint8",
      "description": "Filter envelope amount"
    },
    "lfo1_rate": {
      "byte_offset": 70,
      "bit_mask": 255,
      "bit_shift": 0,
      "value_range": [0, 127],
      "category": "lfo",
      "cc_number": 76,
      "data_type": "uint8",
      "description": "LFO 1 rate"
    },
    "lfo1_amount": {
      "byte_offset": 72,
      "bit_mask": 255,
      "bit_shift": 0,
      "value_range": [0, 127],
      "category": "lfo",
      "cc_number": 77,
      "data_type": "uint8",
      "description": "LFO 1 amount"
    }
  }
}
EOF

# Создать тесты
echo "📝 Создание tests/test_basic.py..."
cat > tests/test_basic.py << 'EOF'
"""
Basic tests for SysEx Toolkit
"""

import pytest
from sysex_toolkit import SysExLibrary, SysExFormat

def test_library_creation():
    """Test library can be created"""
    library = SysExLibrary()
    assert library is not None

def test_supported_formats():
    """Test supported formats"""
    library = SysExLibrary()
    formats = library.list_supported_synthesizers()
    assert 'access_virus' in formats

def test_decoder_creation():
    """Test decoder creation"""
    library = SysExLibrary()
    decoder = library.get_decoder(SysExFormat.ACCESS_VIRUS)
    assert decoder is not None
EOF

# Создать MANIFEST.in
echo "📝 Создание MANIFEST.in..."
cat > MANIFEST.in << 'EOF'
include README.md
include LICENSE
include requirements.txt
recursive-include sysex_toolkit/configs *.json *.yaml
recursive-include examples *.py
recursive-include tests *.py
EOF

# Создать pyproject.toml
echo "📝 Создание pyproject.toml..."
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "sysex-toolkit"
dynamic = ["version"]
description = "Universal SysEx decoder/encoder library for synthesizers"
readme = "README.md"
license = {file = "LICENSE"}
authors = [
    {name = "SystematicLabs", email = "ovcharov@systematiclabs.com"},
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Multimedia :: Sound/Audio",
]
requires-python = ">=3.8"
dependencies = [
    "numpy>=1.19.0",
    "pyyaml>=5.4.0",
]

[project.optional-dependencies]
dev = ["pytest>=6.0", "black>=21.0", "flake8>=3.8"]
examples = ["matplotlib>=3.3.0", "librosa>=0.8.0"]
ml = ["scikit-learn>=1.0.0"]

[project.scripts]
sysex-decode = "sysex_toolkit.cli:decode_command"
sysex-analyze = "sysex_toolkit.cli:analyze_command"

[project.urls]
Homepage = "https://github.com/SystematicLabs/sysex-toolkit"
Repository = "https://github.com/SystematicLabs/sysex-toolkit"
Documentation = "https://github.com/SystematicLabs/sysex-toolkit/wiki"
EOF

# Создать установочный скрипт
echo "📝 Создание install.sh..."
cat > install.sh << 'EOF'
#!/bin/bash

echo "🚀 Installing SysEx Toolkit..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
if [[ $(echo "$python_version < 3.8" | bc -l) == 1 ]]; then
    echo "❌ Python 3.8+ required, found Python $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"

# Install in development mode
echo "📦 Installing package in development mode..."
pip install -e .

# Install optional dependencies
echo "🔧 Installing optional dependencies..."
pip install -e ".[dev,examples]"

echo "✅ Installation complete!"
echo ""
echo "🎹 Quick test:"
echo "python -c \"from sysex_toolkit import SysExLibrary; print('SysEx Toolkit ready!')\""
echo ""
echo "📚 Examples:"
echo "python examples/basic_usage.py"
echo ""
echo "🔧 CLI tools:"
echo "sysex-decode --help"
echo "sysex-analyze --help"
EOF

chmod +x install.sh

# Создать скрипт для билда
echo "📝 Создание build.sh..."
cat > build.sh << 'EOF'
#!/bin/bash

echo "🔨 Building SysEx Toolkit package..."

# Install build dependencies
pip install build twine

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build package
python -m build

echo "✅ Package built successfully!"
echo ""
echo "📦 Files created:"
ls -la dist/
echo ""
echo "🚀 To install locally:"
echo "pip install dist/*.whl"
echo ""
echo "📤 To upload to PyPI:"
echo "twine upload dist/*"
EOF

chmod +x build.sh

# Создать .gitignore
echo "📝 Создание .gitignore..."
cat > .gitignore << 'EOF'
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
*.syx
*.json.bak
test_presets/
EOF

echo ""
echo "🎉 ГОТОВО! Структура пакета SysEx Toolkit создана"
echo "======================================================"
echo ""
echo "📁 Созданная структура:"
tree . 2>/dev/null || find . -type f | head -20
echo ""
echo "🚀 Следующие шаги:"
echo "1. Перейдите в папку: cd sysex-toolkit"
echo "2. Установите пакет: ./install.sh"
echo "3. Запустите тесты: python -m pytest tests/"
echo "4. Попробуйте CLI: sysex-decode --help"
echo "5. Создайте пакет: ./build.sh"
echo ""
echo "📚 Документация создана в README.md"
echo "🔧 Примеры в examples/basic_usage.py"
echo "⚙️  Конфигурации в sysex_toolkit/configs/"
echo ""
echo "✅ Пакет готов к использованию и публикации!"
