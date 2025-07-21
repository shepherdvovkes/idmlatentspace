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

