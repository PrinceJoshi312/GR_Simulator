import pytest
import numpy as np
from app.domain.validation.benchmarks import calculate_theoretical_precession, run_mercury_precession_benchmark

def test_calculate_theoretical_precession_mercury():
    # Mercury parameters (approximate)
    G = 6.67430e-11
    M = 1.98847e30
    a = 5.7909e10
    e = 0.2056
    
    # Expected: 5.0187e-7 radians per revolution
    # This value is from standard GR references for Mercury's precession per orbit
    expected_rad_per_rev = 5.0187e-7
    
    actual = calculate_theoretical_precession(G, M, a, e)
    
    # Allow small numerical variation
    assert pytest.approx(actual, rel=1e-4) == expected_rad_per_rev

def test_run_mercury_precession_benchmark_pass():
    G = 6.67430e-11
    M = 1.98847e30
    a = 5.7909e10
    e = 0.2056
    
    expected = calculate_theoretical_precession(G, M, a, e)
    actual = expected * 1.02 # 2% deviation
    
    result = run_mercury_precession_benchmark(actual, G, M, a, e, threshold=0.05)
    
    assert result.is_passed is True
    assert result.deviation < 0.05
    assert result.actual_value == actual
    assert result.expected_value == expected

def test_run_mercury_precession_benchmark_fail():
    G = 6.67430e-11
    M = 1.98847e30
    a = 5.7909e10
    e = 0.2056
    
    expected = calculate_theoretical_precession(G, M, a, e)
    actual = expected * 1.10 # 10% deviation
    
    result = run_mercury_precession_benchmark(actual, G, M, a, e, threshold=0.05)
    
    assert result.is_passed is False
    assert result.deviation > 0.05
