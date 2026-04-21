import pytest
from app.domain.simulation.engine import SimulationEngine, Burn

def test_trajectory_prediction_with_burn_sequence():
    engine = SimulationEngine()
    run = engine.start_run("prediction-test", seed=1, g=1.0, central_mass=100.0)
    run_id = run.run_id
    
    # Add a rocket
    engine.add_custom_object(run_id, "rocket", mass=1.0, x=10.0, y=0.0, vx=0.0, vy=3.0)
    
    # Define a burn sequence: 2 burns
    burn_plan = [
        Burn(start_t=0.0, duration=1.0, magnitude=10.0, angle_rad=0.0),
        Burn(start_t=2.0, duration=1.0, magnitude=20.0, angle_rad=1.57) # 90 degrees
    ]
    
    prediction = engine.predict_trajectory(
        run_id=run_id,
        object_name="rocket",
        burn_plan=burn_plan,
        lookahead_duration=5.0
    )
    
    assert "path" in prediction
    assert len(prediction["path"]) > 0
    assert "final_state" in prediction
    assert prediction["lookahead_duration"] == 5.0
    
    # Verify no state change in live run
    snap = engine.snapshot_run(run_id)
    rocket = next(obj for obj in snap["objects"] if obj["name"] == "rocket")
    assert rocket["state"]["coordinate_time"] == 0.0

def test_prediction_invalid_object():
    engine = SimulationEngine()
    run = engine.start_run("error-test", seed=1, g=1.0, central_mass=1.0)
    
    prediction = engine.predict_trajectory(
        run_id=run.run_id,
        object_name="nonexistent",
        burn_plan=[],
        lookahead_duration=1.0
    )
    
    assert "error" in prediction
