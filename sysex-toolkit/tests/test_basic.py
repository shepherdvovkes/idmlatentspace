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
