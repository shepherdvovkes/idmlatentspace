# Synthesizer Performance Analyzer & ML Research Platform

> **Comprehensive research platform for analyzing and generating high-dimensional latent spaces in electronic music production**

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Qt](https://img.shields.io/badge/GUI-PySide6-green)
![ML](https://img.shields.io/badge/ML-PyTorch%20%7C%20Transformer%20VAE-orange)
![Status](https://img.shields.io/badge/Status-Research%20Ready-brightgreen)
![SysEx](https://img.shields.io/badge/Package-sysex--toolkit-purple)

## Project Overview

This is a multi-component research platform specializing in analyzing timbral characteristics of electronic music using modern machine learning methods. The project implements methodologies described in research work on β-VAE with Transformer architectures for IDM and Dubstep music.

### Key Features

- ** MIDI+CC Analysis**: Processing MIDI notes with dense Control Change automation
- ** High-Dimensional VAE**: Implementation of 384-512D latent spaces for complex timbral encoding  
- ** Research Metrics**: CC Modulation Error, MR-STFT Loss, KL Divergence, Note Accuracy
- ** Interactive Visualization**: D3.js charts for latent space analysis and CC evolution
- ** Academic Ready**: Generation of publication-ready results and tables
- ** Complete Pipeline**: From Ableton export to trained models with one command
- ** Universal SysEx Support**: Work with any synthesizers through configuration files
- ** Built-in Definitions**: Access Virus C, Roland JP-8000 and others

##  Quick Start

### System Requirements

**Minimum:**
- RAM: 8GB (16GB recommended)
- Storage: 2GB free space
- Python: 3.8+
- OS: Windows 10+, macOS 10.15+, Linux

**Recommended:**
- GPU: NVIDIA RTX 3070+ with 8GB VRAM
- CPU: 8+ cores for parallel processing
- RAM: 32GB for large datasets
- SSD: For fast I/O during training

### Installation

```bash
# Clone the repository
git clone https://github.com/username/synthesizer-performance-analyzer.git
cd synthesizer-performance-analyzer

# Install dependencies
pip install -r requirements.txt
pip install sysex-toolkit

# Create directory for Ableton projects
mkdir AbletonProjects

# Copy your .mid files from Ableton Live export
cp /path/to/your/*.mid AbletonProjects/
```

### Usage

#### GUI version (recommended)
```bash
python main.py
```

#### Command line
```bash
# Run full analysis
python pipeline.py

# Quick test with reduced parameters
python pipeline.py --config quick_config.yaml

# Custom project directory
python pipeline.py --project-dir ./MyMIDIFiles --output results.json
```

#### SysEx analysis
```bash
# Decode SysEx file
sysex-decode my_preset.syx --synth access_virus

# Analyze unknown SysEx format
sysex-analyze unknown_synth.syx

# Batch process multiple files
sysex-batch /path/to/presets/ --synth access_virus
```

## 📁 Project Structure

```
synthesizer-performance-analyzer/
├── AbletonProjects/           # Your MIDI files
│   ├── dubstep_bass_01.mid
│   ├── idm_glitch_02.mid
│   └── ...
├── main.py                    # GUI application
├── pipeline.py                # Main analysis backend
├── gui.py                     # PySide6 interface
├── data_processor.py          # Data processing
├── model.py                   # Transformer VAE model
├── utils.py                   # Utilities and visualization
├── apa.py                     # Ableton project analyzer
├── audio_ml_analyzer.py       # ML audio analysis
├── preset_differential_analyzer.py # Preset analysis
├── sysex-toolkit/             # Universal SysEx library
│   ├── sysex_toolkit/
│   ├── examples/
│   └── tests/
├── Samples/                   # Audio samples
├── config.yaml                # Configuration parameters
├── README.md                  # This file
└── kubmlops-3.pdf             # Project description
```

## Ableton File Preparation

### Export Settings

1. **Solo synthesizer tracks** (basslines, leads with heavy automation)
2. **Standardize CC mapping**:
   ```
   CC1  → Filter Cutoff      CC6  → Envelope Decay
   CC2  → Filter Resonance   CC7  → Distortion/Drive  
   CC3  → LFO Rate          CC8  → Reverb Send
   CC4  → LFO Amount        CC9  → Delay Send
   CC5  → Envelope Attack   CC10 → Custom Parameter
   ```
3. **Export as MIDI** with 480 PPQ resolution
4. **4-bar segments** work best for analysis
5. **Dense automation** (>5 CC events per beat) produces better results

### File Naming Convention

```
genre_synth_project_segment_bpm_synthesizer.mid

Examples:
dubstep_bass_01_seg01_140_serum.mid
idm_glitch_02_seg01_170_massive.mid
```

## Understanding Results

### Quantitative Metrics

| Metric | Description | Range | Goal |
|---------|----------|----------|------|
| **CC-ME** | CC Modulation Error - timbral accuracy | 0.0-1.0 | Lower ↓ |
| **MR-STFT** | Multi-Resolution STFT Loss - audio quality | 0.0-1.0 | Lower ↓ |
| **D_KL** | KL Divergence - latent space regularity | 0.0+ | Lower ↓ |
| **Note Acc** | Note reconstruction accuracy | 0.0-1.0 | Higher ↑ |

### Expected Results

```json
{
  "quantitative": {
    "128": {"ccme": 0.245, "mrstft": 0.312, "dkl": 2.145, "noteAcc": 0.876},
    "256": {"ccme": 0.198, "mrstft": 0.267, "dkl": 1.987, "noteAcc": 0.891},
    "384": {"ccme": 0.142, "mrstft": 0.198, "dkl": 1.756, "noteAcc": 0.902},
    "512": {"ccme": 0.118, "mrstft": 0.156, "dkl": 1.623, "noteAcc": 0.915}
  }
}
```

**Key Insight**: High-dimensional latent spaces (384D, 512D) significantly outperform traditional low-dimensional approaches for generating complex timbres.

## Research Applications

### Academic Integration

Results can be directly used in LaTeX tables:

![table1](https://github.com/user-attachments/assets/497d304c-8837-44c3-b23f-f62b619174e9)


### Hypothesis Validation

- **High-dimensional superiority**: 384D+ models show significantly lower CC-ME
- **Timbral complexity capture**: Complex CC automation requires >256D latent spaces  
- **Genre-specific encoding**: IDM vs Dubstep patterns emerge in latent space
- **Architecture efficiency**: Transformer + β-VAE handles sequential CC data well

## Visualizations

### Web Interface Capabilities

1. **Dataset Quality Overview** - Table with file statistics and quality scores
2. **Latent Space Visualization** - PCA projection of learned representations
3. **CC Evolution Plots** - Time series of parameter automation
4. **Architecture Comparisons** - Bar charts comparing model performance
5. **Real-time Processing** - Progress monitoring with detailed logs

### Generated Charts

- **Training Curves** (loss vs epochs)
- **Latent Space Structure** (PCA, t-SNE)
- **CC Parameter Usage Analysis**
- **Performance Comparison** across dimensions

## Advanced Usage

![f2](https://github.com/user-attachments/assets/0d77d63c-0377-4286-9740-0dfadd725941)

### Custom Metrics

```python
from pipeline import AnalysisWorker
import yaml

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Run analysis with custom parameters
worker = AnalysisWorker(config, queue=None)
results = worker.run()

# Access specific metrics
cc_me_384d = results[384]['metrics']['CC-ME']
print(f"384D CC-ME Score: {cc_me_384d:.4f}")
```

### SysEx Preset Analysis

```python
from sysex_toolkit import decode_sysex_file, SysExFormat

# Decode preset
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

### Machine Learning Integration

Perfect for ML research in electronic music:

```python
# Feature extraction for latent space
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

## Configuration

### Basic Configuration (`config.yaml`)

```yaml
data_source:
  midi_path: "./AbletonProjects"
  cache_path: "./cache/processed_data.pkl"

experiment:
  latent_dims: [128, 256, 384, 512]
  results_path: "./results"

model_training:
  epochs: 50
  learning_rate: 0.0001
  batch_size: 16
```

### Quick Test Configuration

For rapid prototyping use `quick_config.yaml` with reduced parameters:
- 2 latent dimensions (128D, 384D)
- 20 epochs
- Smaller model architecture

## Supported Synthesizers (SysEx Toolkit)

- **Access Virus C** (Full support)
- **Roland JP-8000** (Basic support)
- **Custom synthesizers** via configuration files

## Use Cases

- **Music Production**: Analysis and modification of synthesizer presets
- **ML Research**: Feature extraction for generative models
- **Preset Management**: Organization and categorization of sound libraries
- **Sound Design**: Understanding parameter relationships
- **Academic Research**: Studying electronic music characteristics

## Dataset Requirements

| Metric | Minimum | Recommended |
|---------|---------|---------------|
| Files | 10 | 50+ |
| CC Events/segment | 50 | 200+ |
| Sequence length | 200 tokens | 500+ tokens |
| Quality score | 70% | 90%+ |

## Troubleshooting

### Common Issues

**"MIDI files not found"**
```bash
ls -la AbletonProjects/*.mid  # Check file existence
chmod 644 AbletonProjects/*   # Fix file permissions
```

**"Insufficient CC automation"**
- Ensure CC controllers are automated in Ableton
- Verify export includes automation tracks
- Check CC mapping consistency

**"CUDA out of memory"**
```yaml
model_training:
  batch_size: 8     # Reduce batch size
  model_dim: 256    # Use smaller model
```

**Low quality scores**
- Review CC mapping consistency between files
- Ensure 4-bar segments are musically coherent  
- Check for tempo variations between exports

## Citation

If you use this tool in your research, please cite:

```bibtex
@article{synthesizer_performance_2024,
  title={Generating High-Fidelity Synthesizer Performances for Complex Electronic Music via Structured High-Dimensional Latent Spaces},
  author={Ovcharov, Vladimir},
  journal={Journal of AI Music Research},
  year={2024}
}

@software{sysex_toolkit_2025,
  title={SysEx Toolkit: Universal SysEx Library for Music Production},
  author={Ovcharov, Vladimir},
  year={2025},
  url={https://pypi.org/project/sysex-toolkit/}
}
```

## Contributing

We welcome contributions! Please see our contribution guidelines:

1. **Fork** the repository
2. **Create** a feature branch
3. **Add** tests for new functionality  
4. **Submit** a pull request with detailed description

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Code formatting
black *.py
flake8 *.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Ableton Live** for MIDI export capabilities
- **PyTorch** team for the deep learning framework
- **PySide6** for modern GUI framework
- **D3.js** community for visualization tools
- **Music Information Retrieval** research community

## Support

- **Email**: vladimir@highfunk.uk
- **Issues**: [GitHub Issues]([https://github.com/shepherdvovkes/idmlatentspace/issues])
- **Discussions**: [GitHub Discussions](https://github.com/shepherdvovkes/idmlatentspace/discussions)
- **Documentation**: [Wiki](https://github.com/shepherdvovkes/idmlatentspace/wiki)

---

**Ready to revolutionize electronic music generation with high-dimensional latent spaces!**

*Built with ❤️ for the music AI research community*
