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
