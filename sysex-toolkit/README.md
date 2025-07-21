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

