import pytest
import numpy as np
from app.domain.simulation.engine import SimulationEngine

def test_solar_system_scenario_initialization():
    engine = SimulationEngine()
    run = engine.start_run(
        scenario_id="solar-system",
        seed=42,
        g=6.67430e-11,
        central_mass=1.98847e30
    )
    
    assert run.scenario_id == "solar-system"
    # Sun is central mass, planets are in objects. There are 8 planets in catalog.
    assert len(run.objects) == 8
    
    planet_names = [obj.name for obj in run.objects]
    assert "earth" in planet_names
    assert "jupiter" in planet_names
    assert "mercury" in planet_names

def test_solar_system_step():
    engine = SimulationEngine()
    run = engine.start_run(
        scenario_id="solar-system",
        seed=42,
        g=6.67430e-11,
        central_mass=1.98847e30
    )
    
    initial_earth_pos = next(obj.state.x for obj in run.objects if obj.name == "earth")
    
    # Step simulation (1 hour)
    engine.step_run(run.run_id, dt=3600.0)
    
    new_earth_pos = next(obj.state.x for obj in run.objects if obj.name == "earth")
    
    # Earth should have moved
    assert new_earth_pos != initial_earth_pos
