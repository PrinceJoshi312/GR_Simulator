import pytest
import numpy as np
from app.domain.simulation.engine import SimulationEngine, Burn

def test_predict_trajectory_matches_real_step():
    engine = SimulationEngine()
    run = engine.start_run("prediction-test", seed=42, g=1.0, central_mass=100.0)
    run_id = run.run_id
    
    # 1. Add object
    engine.add_custom_object(run_id, "rocket", mass=1.0, x=10.0, y=0.0, vx=0.0, vy=3.0)
    
    # 2. Define a burn plan
    burn_plan = [
        Burn(start_t=1.0, duration=2.0, magnitude=10.0, angle_rad=0.0)
    ]
    
    # 3. Get prediction for 5 seconds
    lookahead = 5.0
    prediction = engine.predict_trajectory(run_id, "rocket", burn_plan, lookahead)
    
    predicted_final = prediction["final_state"]
    
    # 4. Now actually RUN the simulation for 5 seconds with the same burn
    # Default dt is 1.0
    for i in range(5): 
        snap = engine.snapshot_run(run_id)
        rocket_obj = next(obj for obj in snap["objects"] if obj["name"] == "rocket")
        current_t = float(rocket_obj["state"]["coordinate_time"])
        
        # Apply burn if in window (1.0 <= t < 3.0)
        # Prediction kernel checks burn.start_t <= current_t < (burn.start_t + burn.duration)
        if 1.0 <= current_t < 3.0:
            engine.update_object_thrust(run_id, "rocket", is_active=True, magnitude=10.0, angle_rad=0.0)
        else:
            engine.update_object_thrust(run_id, "rocket", is_active=False, magnitude=0.0, angle_rad=0.0)
            
        engine.step_run(run_id, force=True)
        
    actual_snap = engine.snapshot_run(run_id)
    actual_final = next(obj["state"] for obj in actual_snap["objects"] if obj["name"] == "rocket")
    
    # 5. Compare (should be identical since logic is shared)
    assert predicted_final["x"] == pytest.approx(actual_final["x"])
    assert predicted_final["y"] == pytest.approx(actual_final["y"])
    assert predicted_final["vx"] == pytest.approx(actual_final["vx"])
    assert predicted_final["vy"] == pytest.approx(actual_final["vy"])

def test_predict_trajectory_handles_invalid_object():
    engine = SimulationEngine()
    run = engine.start_run("err-test", seed=1, g=1.0, central_mass=1.0)
    
    res = engine.predict_trajectory(run.run_id, "non-existent", [], 10.0)
    assert "error" in res
    assert res["path"] == []
