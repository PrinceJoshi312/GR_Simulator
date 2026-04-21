import pytest
import numpy as np
from app.domain.simulation.engine import SimulationEngine, SimulationObject, ObjectState, ThrustConfig

def test_thrust_causes_deviation_from_geodesic():
    engine = SimulationEngine()
    # High G and M for strong relativistic effects, but here we just need a baseline
    run = engine.start_run("thrust-test", seed=42, g=1.0, central_mass=100.0)
    run_id = run.run_id
    
    # 1. Start with a rocket at a stable distance
    # Initial state for a circular-ish orbit or just some starting point
    x0, y0 = 10.0, 0.0
    vx0, vy0 = 0.0, 3.0
    
    engine.add_custom_object(run_id, "rocket", mass=1.0, x=x0, y=y0, vx=vx0, vy=vy0)
    engine.add_custom_object(run_id, "asteroid", mass=1.0, x=x0, y=y0, vx=vx0, vy=vy0) # Identical initial state
    
    # 2. Activate thrust on rocket only
    # Thrust in positive x direction (outward radially)
    engine.update_object_thrust(run_id, "rocket", is_active=True, magnitude=50.0, angle_rad=0.0)
    
    # 3. Step simulation
    for _ in range(50):
        engine.step_run(run_id, dt=0.01, force=True)
        
    snap = engine.snapshot_run(run_id)
    objects = {obj["name"]: obj for obj in snap["objects"]}
    
    rocket = objects["rocket"]
    asteroid = objects["asteroid"]
    
    # Rocket should be pushed further in x than asteroid
    assert rocket["state"]["x"] > asteroid["state"]["x"]
    # Rocket should have higher vx
    assert rocket["state"]["vx"] > asteroid["state"]["vx"]
    
    # Asteroid should remain on a standard geodesic (same as earth/mercury logic)
    # asteroid should not have thrust
    assert asteroid["thrust"] is None or not asteroid["thrust"]["is_active"]

def test_thrust_safety_clipping():
    engine = SimulationEngine()
    run = engine.start_run("safety-test", seed=1, g=1.0, central_mass=1.0)
    
    # Tiny mass, massive thrust
    engine.add_custom_object(run_id=run.run_id, name="light-rocket", mass=1e-6, x=10.0, y=0.0, vx=0.0, vy=1.0)
    
    # 1e20 Newtons on 1e-6 kg = 1e26 m/s^2. Safety clipping should cap this.
    engine.update_object_thrust(run.run_id, "light-rocket", is_active=True, magnitude=1e20, angle_rad=0.0)
    
    # Should not crash or produce NaN
    engine.step_run(run.run_id, dt=0.01, force=True)
    snap = engine.snapshot_run(run.run_id)
    state = snap["objects"][0]["state"]
    
    assert np.isfinite(state["x"])
    assert np.isfinite(state["vx"])

def test_mass_loss_during_burn():
    engine = SimulationEngine()
    run = engine.start_run("fuel-test", seed=1, g=1.0, central_mass=1.0)
    
    initial_mass = 100.0
    engine.add_custom_object(run_id=run.run_id, name="rocket", mass=initial_mass, x=10.0, y=0.0, vx=0.0, vy=1.0)
    
    # Configure mass loss rate: 10 kg per second
    for obj in run.objects:
        if obj.name == "rocket":
            obj.thrust = ThrustConfig(is_active=True, magnitude=100.0, angle_rad=0.0, mass_loss_rate=10.0)
            
    # Step 5 seconds (5 steps of 1s)
    for _ in range(5):
        engine.step_run(run.run_id, dt=1.0, force=True)
        
    snap = engine.snapshot_run(run.run_id)
    objects = {obj["name"]: obj for obj in snap["objects"]}
    final_mass = objects["rocket"]["mass"]
    
    # Should be roughly 50kg (100 - 5*10)
    assert final_mass == pytest.approx(50.0)
