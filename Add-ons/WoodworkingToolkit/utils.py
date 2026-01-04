def mm(millimeters_value: float) -> float:
    """Millimeters → meters (Blender internal units)."""
    return millimeters_value / 1000.0

def cm(centimeters_value: float) -> float:
    """Centimeters → meters."""
    return centimeters_value / 100.0

__all__ = ['mm', 'cm']  # Export list for "from utils import *"