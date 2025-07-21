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

