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
