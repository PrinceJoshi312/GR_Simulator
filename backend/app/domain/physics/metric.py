from math import isfinite


def schwarzschild_metric(central_mass: float, g: float, r: float, c: float = 299792458.0) -> dict[str, float]:
    if central_mass <= 0 or g <= 0 or r <= 0:
        raise ValueError("central_mass, g, and r must be positive")
    if not all(isfinite(v) for v in [central_mass, g, r, c]):
        raise ValueError("metric inputs must be finite")

    rs = (2.0 * g * central_mass) / (c**2)
    f = 1.0 - (rs / r)
    if f <= 0:
        # Fallback for near-event-horizon to avoid singularity in integration
        f = 1e-10

    return {
        "r": float(r),
        "schwarzschild_radius": float(rs),
        "g_tt": float(-f),
        "g_rr": float(1.0 / f),
        "g_phiphi": float(r * r),
        "c": float(c),
    }


def kerr_metric(central_mass: float, g: float, r: float, a: float, c: float = 299792458.0) -> dict[str, float]:
    """
    Kerr metric in Boyer-Lindquist coordinates at the equatorial plane (theta = pi/2).
    'a' is the angular momentum parameter (J/Mc), with units of length.
    """
    if central_mass <= 0 or g <= 0 or r <= 0:
        raise ValueError("central_mass, g, and r must be positive")
    
    rs = (2.0 * g * central_mass) / (c**2)
    
    # Kerr parameter 'a' must be <= rs/2 for a black hole, 
    # but we allow larger for spinning stars (though the metric is only an approximation then).
    # a_max = rs / 2.0
    
    delta = r**2 - rs * r + a**2
    if delta <= 0:
        delta = 1e-10 # Avoid singularity
        
    g_tt = -(1.0 - rs / r)
    g_rr = r**2 / delta
    g_phiphi = r**2 + a**2 + (rs * a**2) / r
    g_tphi = -(rs * a) / r
    
    return {
        "r": float(r),
        "a": float(a),
        "schwarzschild_radius": float(rs),
        "g_tt": float(g_tt),
        "g_rr": float(g_rr),
        "g_phiphi": float(g_phiphi),
        "g_tphi": float(g_tphi),
        "c": float(c),
    }
