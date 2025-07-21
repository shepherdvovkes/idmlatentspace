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
