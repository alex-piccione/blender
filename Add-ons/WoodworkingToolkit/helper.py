def mm (millimeters_value: float):
    """Millimeters → meters (Blender internal units)."""
    return millimeters_value / 1000.0

def cm(centimeters_value: float) -> float:
    """Centimeters → meters."""
    return centimeters_value / 100.0