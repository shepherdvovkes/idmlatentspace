# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sysex-toolkit",
    version="1.0.0",
    author="SystematicLabs",
    author_email="ovcharov@systematiclabs.com",
    description="Universal SysEx decoder/encoder library for synthesizers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SystematicLabs/sysex-toolkit",
    project_urls={
        "Bug Tracker": "https://github.com/SystematicLabs/sysex-toolkit/issues",
        "Documentation": "https://github.com/SystematicLabs/sysex-toolkit/wiki",
    },
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'sysex_toolkit': ['configs/*.json', 'configs/*.yaml'],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Artistic Software",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": ["pytest>=6.0", "black>=21.0", "flake8>=3.8", "mypy>=0.812"],
        "examples": ["matplotlib>=3.3.0", "librosa>=0.8.0"],
        "ml": ["scikit-learn>=1.0.0", "tensorflow>=2.6.0"],
    },
    entry_points={
        "console_scripts": [
            "sysex-decode=sysex_toolkit.cli:decode_command",
            "sysex-encode=sysex_toolkit.cli:encode_command", 
            "sysex-analyze=sysex_toolkit.cli:analyze_command",
        ],
    },
    keywords="sysex, synthesizer, midi, audio, music production, access virus, roland",
)

# ================================================================================

# requirements.txt
numpy>=1.19.0
pyyaml>=5.4.0

# ================================================================================

# README.md
# SysEx Toolkit

Universal SysEx decoder/encoder library for synthesizers and music production.

## 🎹 Features

- **Universal SysEx Support**: Works with any synthesizer through configuration files
- **Built-in Definitions**: Access Virus C, Roland JP-8000, and more
- **ML Ready**: Normalized parameters for machine learning applications
- **Easy Integration**: Simple API for quick adoption
- **Extensible**: Add new synthesizers via JSON/YAML configs

## 🚀 Quick Start

### Installation

```bash
pip install sysex-toolkit
```

### Basic Usage

```python
from sysex_toolkit import decode_sysex_file, SysExFormat

# Decode a preset
presets = decode_sysex_file('my_preset.syx', SysExFormat.ACCESS_VIRUS)

# Access parameters
for preset in presets:
    print(f"Preset: {preset['metadata']['preset_name']}")
    
    # Filter parameters (great for wobble bass analysis)
    filter_params = {
        name: data for name, data in preset['parameters'].items() 
        if data['category'] == 'filter'
    }
    
    print(f"Filter cutoff: {filter_params['filter_cutoff']['normalized_value']:.3f}")
```

### Advanced Usage

```python
from sysex_toolkit import SysExLibrary, SysExFormat

# Create library
library = SysExLibrary()

# Get decoder for specific synthesizer
decoder = library.get_decoder(SysExFormat.ACCESS_VIRUS)

# Decode multiple presets
presets = decoder.decode_file('factory_presets.syx')

# Analyze for machine learning
ml_features = []
for preset in presets:
    # Extract normalized values for ML
    feature_vector = [
        param['normalized_value'] 
        for param in preset['parameters'].values()
    ]
    ml_features.append(feature_vector)
```

## 🎛️ Supported Synthesizers

- **Access Virus C** (Full support)
- **Roland JP-8000** (Basic support)
- **Custom synthesizers** via configuration files

## 🔧 CLI Tools

```bash
# Decode a SysEx file
sysex-decode my_preset.syx --synth access_virus

# Analyze unknown SysEx format
sysex-analyze unknown_synth.syx

# Batch process multiple files
sysex-batch /path/to/presets/ --synth access_virus
```

## 📊 Machine Learning Integration

Perfect for electronic music ML research:

```python
# Extract features for latent space
import numpy as np
from sysex_toolkit import decode_sysex_file

presets = decode_sysex_file('dubstep_presets.syx')

# Create feature matrix for VAE training
feature_matrix = []
for preset in presets:
    # Focus on filter parameters for wobble analysis
    wobble_features = []
    for param_name, param_data in preset['parameters'].items():
        if param_data['category'] in ['filter', 'lfo']:
            wobble_features.append(param_data['normalized_value'])
    
    feature_matrix.append(wobble_features)

feature_matrix = np.array(feature_matrix)
# Ready for β-VAE training!
```

## 🎵 Use Cases

- **Music Production**: Analyze and modify synthesizer presets
- **ML Research**: Extract features for generative models
- **Preset Management**: Organize and categorize sound libraries
- **Sound Design**: Understand parameter relationships
- **Academic Research**: Study electronic music characteristics

## 📚 Documentation

Visit our [wiki](https://github.com/SystematicLabs/sysex-toolkit/wiki) for detailed documentation.

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines.

## 📄 License

MIT License - see LICENSE file for details.

## 🎯 Citation

If you use this library in research, please cite:

```bibtex
@software{sysex_toolkit_2025,
  title={SysEx Toolkit: Universal SysEx Library for Music Production},
  author={Ovcharov, Vladimir},
  year={2025},
  url={https://github.com/SystematicLabs/sysex-toolkit}
}
```

# ================================================================================

# sysex_toolkit/__init__.py
"""
SysEx Toolkit - Universal SysEx decoder/encoder library
"""

__version__ = "1.0.0"
__author__ = "SystematicLabs"
__email__ = "ovcharov@systematiclabs.com"

# Import main classes and functions
from .core import (
    SysExDecoder,
    SysExEncoder, 
    SysExLibrary,
    SysExFormat,
    ParameterDefinition,
    SysExDefinition,
    SysExHeader
)

from .utils import (
    decode_sysex_file,
    encode_preset_to_sysex,
    create_config_template
)

from .analyzer import SysExAnalyzer
from .batch import SysExBatchProcessor

# Convenience imports
__all__ = [
    # Core classes
    'SysExDecoder',
    'SysExEncoder',
    'SysExLibrary', 
    'SysExFormat',
    'ParameterDefinition',
    'SysExDefinition',
    'SysExHeader',
    
    # Utility functions
    'decode_sysex_file',
    'encode_preset_to_sysex',
    'create_config_template',
    
    # Analysis tools
    'SysExAnalyzer',
    'SysExBatchProcessor',
    
    # Version info
    '__version__',
    '__author__',
    '__email__'
]

# ================================================================================

# sysex_toolkit/core.py
# Поместите сюда основные классы из sysex_toolkit.py:
# - SysExFormat (enum)
# - ParameterDefinition (dataclass) 
# - SysExHeader (dataclass)
# - SysExDefinition (dataclass)
# - SysExDecoder (class)
# - SysExEncoder (class)
# - SysExLibrary (class)

# ================================================================================

# sysex_toolkit/utils.py
"""
Utility functions for quick access
"""

from .core import SysExLibrary, SysExFormat
from typing import Union, List, Dict, Any
from pathlib import Path

def decode_sysex_file(file_path: Union[str, Path], 
                     synth_format: Union[SysExFormat, str] = SysExFormat.ACCESS_VIRUS) -> List[Dict[str, Any]]:
    """Quick decode SysEx file"""
    library = SysExLibrary()
    decoder = library.get_decoder(synth_format)
    return decoder.decode_file(file_path)

def encode_preset_to_sysex(parameters: Dict[str, float], 
                          preset_name: str = "Custom",
                          synth_format: Union[SysExFormat, str] = SysExFormat.ACCESS_VIRUS) -> bytes:
    """Quick encode preset to SysEx"""
    library = SysExLibrary()
    encoder = library.get_encoder(synth_format)
    return encoder.encode_preset(parameters, preset_name)

def create_config_template(synth_name: str, output_path: Union[str, Path]):
    """Create configuration template for new synthesizer"""
    import json
    
    template = {
        "name": synth_name,
        "version": "1.0", 
        "header": {
            "manufacturer_id": [0x00, 0x00, 0x00],
            "device_id": 0x01,
            "model_id": 0x00
        },
        "preset_name_offset": 100,
        "preset_name_length": 16,
        "total_length": 256,
        "parameters": {
            "example_param": {
                "byte_offset": 10,
                "bit_mask": 255,
                "value_range": [0, 127],
                "category": "oscillator",
                "cc_number": 74,
                "description": "Example parameter"
            }
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(template, f, indent=2)

# ================================================================================

# sysex_toolkit/analyzer.py
# Поместите сюда SysExAnalyzer класс

# ================================================================================

# sysex_toolkit/batch.py  
# Поместите сюда SysExBatchProcessor класс

# ================================================================================

# sysex_toolkit/cli.py
"""
CLI interface for SysEx Toolkit
"""

import argparse
import json
from pathlib import Path
from .utils import decode_sysex_file
from .analyzer import SysExAnalyzer
from .batch import SysExBatchProcessor
from .core import SysExLibrary

def decode_command():
    """CLI decode command"""
    parser = argparse.ArgumentParser(description="Decode SysEx file")
    parser.add_argument('input', help='Input file (.syx or .json)')
    parser.add_argument('--synth', default='access_virus', help='Synthesizer type')
    parser.add_argument('--output', help='Output file')
    
    args = parser.parse_args()
    
    try:
        presets = decode_sysex_file(args.input, args.synth)
        output_path = args.output or f"{Path(args.input).stem}_decoded.json"
        
        with open(output_path, 'w') as f:
            json.dump(presets, f, indent=2, default=str)
        
        print(f"✅ Decoded {len(presets)} presets → {output_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def analyze_command():
    """CLI analyze command"""
    parser = argparse.ArgumentParser(description="Analyze unknown SysEx")
    parser.add_argument('input', help='Input file')
    parser.add_argument('--output', help='Output file')
    
    args = parser.parse_args()
    
    try:
        analysis = SysExAnalyzer.analyze_unknown_sysex(args.input)
        output_path = args.output or f"{Path(args.input).stem}_analysis.json"
        
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        print(f"✅ Analysis saved → {output_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

# ================================================================================

# LICENSE
MIT License

Copyright (c) 2025 SystematicLabs

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

# ================================================================================

# examples/basic_usage.py
"""
Basic usage examples for SysEx Toolkit
"""

from sysex_toolkit import decode_sysex_file, SysExFormat, SysExLibrary

def main():
    print("🎹 SysEx Toolkit Examples")
    
    # Example 1: Quick decode
    try:
        presets = decode_sysex_file('osiris_preset.txt', SysExFormat.ACCESS_VIRUS)
        
        for preset in presets:
            print(f"\nPreset: {preset['metadata']['preset_name']}")
            
            # Show filter parameters (important for Dubstep)
            filter_params = {
                name: data for name, data in preset['parameters'].items()
                if data['category'] == 'filter'
            }
            
            for param_name, param_data in filter_params.items():
                cc_info = f" (CC{param_data['cc_number']})" if param_data['cc_number'] else ""
                print(f"  {param_name}{cc_info}: {param_data['normalized_value']:.3f}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: ML feature extraction
    try:
        # Extract features for machine learning
        ml_features = []
        
        for preset in presets:
            # Create feature vector from normalized values
            feature_vector = [
                param_data['normalized_value']
                for param_data in preset['parameters'].values()
            ]
            ml_features.append(feature_vector)
        
        print(f"\n🤖 ML Features extracted: {len(ml_features)} presets × {len(ml_features[0])} features")
        
    except Exception as e:
        print(f"ML Error: {e}")

if __name__ == "__main__":
    main()