def equatorial_christoffel(metric: dict[str, float]) -> dict[str, float]:
    """
    Standard Schwarzschild Christoffel symbols in equatorial plane.
    """
    # If it's a Kerr metric, delegate
    if "g_tphi" in metric:
        return kerr_equatorial_christoffel(metric)
        
    r = float(metric["r"])
    rs = float(metric["schwarzschild_radius"])
    
    # f = 1 - rs/r. We use a small epsilon to avoid division by zero at horizon.
    f = 1.0 - (rs / r)
    if f <= 0:
        f = 1e-10

    return {
        "gamma_t_tr": rs / (2.0 * r * r * f),
        "gamma_r_tt": rs * f / (2.0 * r * r), # This is usually (rs*f)/(2r^2) in coordinate time acceleration
        "gamma_r_rr": -rs / (2.0 * r * r * f),
        "gamma_r_phiphi": -(r - rs),
        "gamma_phi_rphi": 1.0 / r,
    }

def kerr_equatorial_christoffel(metric: dict[str, float]) -> dict[str, float]:
    """
    Christoffel symbols for Kerr metric at theta = pi/2.
    Simplified version for equatorial motion.
    """
    r = float(metric["r"])
    rs = float(metric["schwarzschild_radius"])
    a = float(metric["a"])
    
    delta = r**2 - rs * r + a**2
    if delta <= 0:
        delta = 1e-10
        
    # We only need the ones relevant for equatorial motion (dr/dtau, dphi/dtau, dt/dtau)
    # These are derived from Gamma^rho_mu nu = 1/2 g^rho sigma (d_mu g_nu sigma + ...)
    
    # Pre-calculate some common terms
    r2 = r*r
    r3 = r2*r
    
    # Gamma^r_tt, Gamma^r_rr, Gamma^r_phiphi, Gamma^r_tphi
    # These govern the radial acceleration d^2r/dtau^2
    
    g_r_tt = (rs / (2.0 * r3)) * (r2 - a**2) * (delta / r2) # Simplified
    # Actually, for the simulator's _get_derivatives, we need them to be compatible.
    # The simulator currently assumes a specific form. Let's provide the key ones.
    
    return {
        "gamma_r_tt": (rs * delta * (r2 - a**2)) / (2.0 * r**6),
        "gamma_r_rr": (rs * a**2 - r * rs * r + a**2 * r) / (2.0 * r * delta), # Approximation
        "gamma_r_phiphi": - (delta / r**3) * (r**3 - a**2 * rs),
        "gamma_r_tphi": - (rs * a * delta) / r**4,
        "is_kerr": 1.0
    }
