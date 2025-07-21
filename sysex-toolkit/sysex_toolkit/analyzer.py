"""
SysEx Analyzer for unknown formats
"""

from typing import Dict, Any, List, Union
from pathlib import Path

class SysExAnalyzer:
    """Analyzer for unknown SysEx formats"""
    
    @staticmethod
    def analyze_unknown_sysex(file_path: Union[str, Path]) -> Dict[str, Any]:
        """Analyze unknown SysEx file"""
        
        with open(file_path, 'rb') as f:
            data = f.read()
        
        analysis = {
            'file_size': len(data),
            'sysex_messages': [],
            'manufacturer_analysis': {}
        }
        
        # Find all SysEx messages
        current_pos = 0
        message_count = 0
        
        while current_pos < len(data):
            start_pos = data.find(0xF0, current_pos)
            if start_pos == -1:
                break
            
            end_pos = data.find(0xF7, start_pos)
            if end_pos == -1:
                break
            
            message = data[start_pos:end_pos + 1]
            message_count += 1
            
            message_info = {
                'message_id': message_count,
                'start_offset': start_pos,
                'length': len(message),
                'manufacturer_id': list(message[1:4]) if len(message) > 3 else [],
                'hex_preview': message[:16].hex(' ') + ('...' if len(message) > 16 else ''),
            }
            
            analysis['sysex_messages'].append(message_info)
            current_pos = end_pos + 1
        
        return analysis
