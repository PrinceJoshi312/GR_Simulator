import pytest

from app.domain.simulation.engine import ObjectState, SimulationEngine


def test_same_seed_preserved_in_run_metadata() -> None:
    engine = SimulationEngine()
    run_a = engine.start_run("default-schwarzschild", seed=999, g=6.6743e-11, central_mass=1.98847e30)
    run_b = engine.start_run("default-schwarzschild", seed=999, g=6.6743e-11, central_mass=1.98847e30)

    assert run_a.seed == run_b.seed == 999
    assert run_a.g == run_b.g
    assert run_a.central_mass == run_b.central_mass
    signature_a = f"{run_a.scenario_id}|{run_a.seed}|{run_a.g}|{run_a.central_mass}|{run_a.engine_version}|{run_a.app_version}"
    signature_b = f"{run_b.scenario_id}|{run_b.seed}|{run_b.g}|{run_b.central_mass}|{run_b.engine_version}|{run_b.app_version}"
    assert signature_a == signature_b


def test_deterministic_step_updates_and_clocks() -> None:
    engine = SimulationEngine()
    run_a = engine.start_run("default-schwarzschild", seed=42, g=6.6743e-11, central_mass=1.98847e30)
    run_b = engine.start_run("default-schwarzschild", seed=42, g=6.6743e-11, central_mass=1.98847e30)

    # Start from identical object state for deterministic check.
    run_b.object_state = ObjectState(
        x=run_a.object_state.x,
        y=run_a.object_state.y,
        vx=run_a.object_state.vx,
        vy=run_a.object_state.vy,
        proper_time=run_a.object_state.proper_time,
        coordinate_time=run_a.object_state.coordinate_time,
    )
    stepped_a = engine.step_run(run_a.run_id, dt=10.0)
    stepped_b = engine.step_run(run_b.run_id, dt=10.0)

    assert stepped_a is not None and stepped_a.object_state is not None
    assert stepped_b is not None and stepped_b.object_state is not None
    assert float(stepped_a.object_state.coordinate_time) > 0.0
    assert float(stepped_a.object_state.proper_time) > 0.0
    assert float(stepped_a.object_state.coordinate_time) == float(stepped_b.object_state.coordinate_time)
    assert float(stepped_a.object_state.proper_time) == float(stepped_b.object_state.proper_time)
    assert float(stepped_a.object_state.x) == float(stepped_b.object_state.x)
    assert float(stepped_a.object_state.y) == float(stepped_b.object_state.y)


def test_step_rejects_invalid_dt_and_origin_state() -> None:
    engine = SimulationEngine()
    run = engine.start_run("default-schwarzschild", seed=1, g=6.6743e-11, central_mass=1.98847e30)
    with pytest.raises(ValueError):
        engine.step_run(run.run_id, dt=0.0)

    run.object_state = ObjectState(x=0.0, y=0.0, vx=0.0, vy=0.0)
    if run.objects:
        run.objects[0].state = run.object_state
    with pytest.raises(ValueError):
        engine.step_run(run.run_id, dt=1.0)


def test_pause_resume_reset_preserve_deterministic_controls() -> None:
    engine = SimulationEngine()
    run = engine.start_run("default-schwarzschild", seed=11, g=6.6743e-11, central_mass=1.98847e30)
    before = engine.snapshot_run(run.run_id)
    assert before is not None

    paused = engine.pause_run(run.run_id)
    assert paused is not None and paused.state == "paused"
    assert engine.step_run(run.run_id, dt=1.0) is None

    resumed = engine.resume_run(run.run_id)
    assert resumed is not None and resumed.state == "running"
    stepped = engine.step_run(run.run_id, dt=1.0)
    assert stepped is not None

    engine.update_runtime_params(run.run_id, timestep=2.0, g=6.6743e-11, central_mass=1.9e30)
    reset = engine.reset_run(run.run_id)
    assert reset is not None and reset.state == "idle"
    after = engine.snapshot_run(run.run_id)
    assert after is not None
    assert before["objects"] == after["objects"]
    assert before["g"] == after["g"]
    assert before["central_mass"] == after["central_mass"]
    assert before["timestep"] == after["timestep"]


def test_parameter_update_remains_deterministic_for_same_inputs() -> None:
    engine = SimulationEngine()
    run_a = engine.start_run("default-schwarzschild", seed=77, g=6.6743e-11, central_mass=1.98847e30)
    run_b = engine.start_run("default-schwarzschild", seed=77, g=6.6743e-11, central_mass=1.98847e30)

    engine.update_runtime_params(run_a.run_id, timestep=3.0, g=6.6743e-11, central_mass=1.9e30)
    engine.update_runtime_params(run_b.run_id, timestep=3.0, g=6.6743e-11, central_mass=1.9e30)
    state_a = engine.step_run(run_a.run_id)
    state_b = engine.step_run(run_b.run_id)
    assert state_a is not None and state_b is not None
    snap_a = engine.snapshot_run(run_a.run_id)
    snap_b = engine.snapshot_run(run_b.run_id)
    assert snap_a is not None and snap_b is not None
    assert snap_a["objects"] == snap_b["objects"]
