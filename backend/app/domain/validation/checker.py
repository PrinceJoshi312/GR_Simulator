import numpy as np
from math import isfinite

def validate_object_state(x: float, y: float, vx: float, vy: float, rs: float) -> dict:
    """Basic validation checks for an object's relativistic state."""
    r = np.sqrt(x**2 + y**2)
    is_finite = all(isfinite(v) for v in [x, y, vx, vy])
    is_outside_rs = r > rs
    
    # Simple 'stable' heuristic for now
    is_stable = is_finite and is_outside_rs
    
    return {
        "is_stable": bool(is_stable),
        "is_finite": bool(is_finite),
        "is_outside_rs": bool(is_outside_rs),
        "r": float(r),
        "rs": float(rs),
        "error_estimate": 0.0,
    }
