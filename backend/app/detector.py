from typing import Dict

# Simple detector for ghost buses
def is_ghost(bus: Dict) -> bool:
    """
    Decide if a bus is a 'ghost'.
    For now, we mark it as ghost if:
    - speed is 0 (not moving), OR
    - timestamp is too old
    """
    import time

    # If bus hasn't updated for >120 seconds → ghost
    if time.time() - bus.get("timestamp", 0) > 120:
        return True

    # If bus is not moving
    if bus.get("speed", 1) == 0:
        return True

    return False
