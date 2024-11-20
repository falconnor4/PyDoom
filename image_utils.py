import struct
from typing import Tuple

def get_png_dimensions(filepath: str) -> Tuple[int, int]:
    """Get the dimensions of a PNG file.
    
    Args:
        filepath: Path to the PNG file
        
    Returns:
        Tuple of (width, height)
    """
    with open(filepath, 'rb') as f:
        data = f.read()
        
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Not a PNG file')
        
    w, h = struct.unpack('>LL', data[16:24])
    return int(w), int(h)
