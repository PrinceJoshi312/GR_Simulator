import pytest

from app.domain.physics.christoffel import equatorial_christoffel
from app.domain.physics.metric import schwarzschild_metric


def test_schwarzschild_metric_components_are_finite() -> None:
    metric = schwarzschild_metric(central_mass=1.98847e30, g=6.6743e-11, r=5.79e10)
    assert metric["g_tt"] < 0.0
    assert metric["g_rr"] > 1.0
    assert metric["g_phiphi"] > 0.0


def test_equatorial_christoffel_returns_expected_keys() -> None:
    metric = schwarzschild_metric(central_mass=1.98847e30, g=6.6743e-11, r=5.79e10)
    gamma = equatorial_christoffel(metric)
    for key in ["gamma_t_tr", "gamma_r_tt", "gamma_r_rr", "gamma_r_phiphi", "gamma_phi_rphi"]:
        assert key in gamma
    assert gamma["gamma_r_tt"] == pytest.approx(gamma["gamma_t_tr"])


def test_equatorial_christoffel_rejects_invalid_radius_metric() -> None:
    with pytest.raises(ValueError):
        equatorial_christoffel({"r": 0.0, "schwarzschild_radius": 10.0})
