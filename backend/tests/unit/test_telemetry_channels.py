import numpy as np
import pytest
from app.domain.simulation.engine import SimulationEngine

def test_telemetry_history_contains_required_channels():
    engine = SimulationEngine()
    # Realistic G and Sun-like mass
    G = 6.67430e-11
    M = 1.98847e30
    run = engine.start_run(scenario_id="test", seed=42, g=G, central_mass=M)
    
    # Run a few steps
    for _ in range(5):
        engine.step_run(run.run_id)
    
    run_snapshot = engine._runs[run.run_id]
    assert "mercury" in run_snapshot.telemetry_history
    history = run_snapshot.telemetry_history["mercury"]
    assert len(history) > 0
    
    last_entry = history[-1]
    
    # Required channels for AC2 and AC3
    required_channels = ["x", "y", "vx", "vy", "r", "t", "proper_time", "coordinate_time", "proper_time_drift"]

    for channel in required_channels:
        assert channel in last_entry, f"Missing telemetry channel: {channel}"
        assert isinstance(last_entry[channel], float)

