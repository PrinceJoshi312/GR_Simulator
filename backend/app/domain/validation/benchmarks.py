import numpy as np
from dataclasses import dataclass

@dataclass
class ValidationResult:
    test_name: str
    pass_threshold: float
    actual_value: float
    expected_value: float
    is_passed: bool
    deviation: float
    units: str

def calculate_theoretical_precession(g: float, m: float, a: float, e: float) -> float:
    """
    Calculates the Schwarzschild precession per revolution in radians.
    Formula: delta_phi = (6 * pi * G * M) / (c^2 * a * (1 - e^2))
    """
    c = 299792458.0
    numerator = 6.0 * np.pi * g * m
    denominator = (c**2) * a * (1.0 - e**2)
    return float(numerator / denominator)

def run_mercury_precession_benchmark(
    actual_precession_rad_per_rev: float,
    g: float,
    m: float,
    a: float = 5.7909e10,
    e: float = 0.2056,
    threshold: float = 0.05  # 5% default threshold for numerical integration
) -> ValidationResult:
    """
    Compares simulated Mercury precession against the theoretical GR prediction.
    """
    expected = calculate_theoretical_precession(g, m, a, e)
    
    # Calculate relative deviation
    if expected == 0:
        deviation = 0.0
    else:
        deviation = abs(actual_precession_rad_per_rev - expected) / expected
        
    is_passed = bool(deviation <= threshold)
    
    return ValidationResult(
        test_name="Mercury Perihelion Precession",
        pass_threshold=float(threshold),
        actual_value=float(actual_precession_rad_per_rev),
        expected_value=float(expected),
        is_passed=is_passed,
        deviation=float(deviation),
        units="rad/rev"
    )

def validate_orbit_circularity(
    radii: list[float], 
    expected_radius: float, 
    threshold: float = 0.001
) -> ValidationResult:
    """
    Validates that a supposedly circular orbit maintains its radius.
    """
    avg_radius = np.mean(radii)
    deviation = abs(avg_radius - expected_radius) / expected_radius
    is_passed = bool(deviation <= threshold)
    
    return ValidationResult(
        test_name="Orbital Radius Stability",
        pass_threshold=float(threshold),
        actual_value=float(avg_radius),
        expected_value=float(expected_radius),
        is_passed=is_passed,
        deviation=float(deviation),
        units="m"
    )
