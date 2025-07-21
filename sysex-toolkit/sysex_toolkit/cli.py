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

