import asyncio
import json
from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse

from app.contracts.runs import ObjectCreateRequest, RunCreateRequest, RuntimeParamsRequest, Burn, BurnSequence
from app.domain.simulation.engine import SimulationEngine

router = APIRouter(prefix="/runs", tags=["runs"])


def _success(data: dict, request_id: str | None = None) -> dict:
    return {"data": data, "meta": {"request_id": request_id or str(uuid4())}, "error": None}


def _error(code: str, message: str, context: dict | None = None, request_id: str | None = None) -> dict:
    return {
        "data": None,
        "meta": {"request_id": request_id or str(uuid4())},
        "error": {"code": code, "message": message, "context": context or {}, "hint": "Check request parameters"},
    }


@router.post("")
def create_run(payload: RunCreateRequest, request: Request) -> dict:
    engine: SimulationEngine = request.app.state.sim_engine
    try:
        run = engine.start_run(
            scenario_id=payload.scenario_id,
            seed=payload.seed,
            g=payload.g,
            central_mass=payload.central_mass,
        )
        # Update angular momentum if provided
        if payload.angular_momentum != 0:
            engine.update_runtime_params(
                run.run_id, 
                timestep=float(run.timestep), 
                g=run.g, 
                central_mass=run.central_mass, 
                angular_momentum=payload.angular_momentum
            )
    except ValueError as exc:
        return JSONResponse(
            status_code=400,
            content=_error(code="INVALID_RUN_PARAMS", message=str(exc), context={"scenario_id": payload.scenario_id}),
        )
    return _success(data=engine.snapshot_run(run.run_id) or {})


@router.get("/{run_id}")
def get_run(run_id: str, request: Request) -> dict:
    engine: SimulationEngine = request.app.state.sim_engine
    snapshot = engine.snapshot_run(run_id)
    if snapshot is None:
        return JSONResponse(
            status_code=404,
            content=_error(code="RUN_NOT_FOUND", message="run not found", context={"run_id": run_id}),
        )
    return _success(data=snapshot)


@router.post("/{run_id}/pause")
def pause_run(run_id: str, request: Request) -> dict:
    engine: SimulationEngine = request.app.state.sim_engine
    run = engine.pause_run(run_id)
    if run is None:
        return JSONResponse(
            status_code=404,
            content=_error(code="RUN_NOT_FOUND", message="run not found", context={"run_id": run_id}),
        )
    return _success(data=engine.snapshot_run(run.run_id) or {})


@router.post("/{run_id}/resume")
def resume_run(run_id: str, request: Request) -> dict:
    engine: SimulationEngine = request.app.state.sim_engine
    run = engine.resume_run(run_id)
    if run is None:
        return JSONResponse(
            status_code=404,
            content=_error(code="RUN_NOT_FOUND", message="run not found", context={"run_id": run_id}),
        )
    return _success(data=engine.snapshot_run(run.run_id) or {})


@router.post("/{run_id}/reset")
def reset_run(run_id: str, request: Request) -> dict:
    engine: SimulationEngine = request.app.state.sim_engine
    run = engine.reset_run(run_id)
    if run is None:
        return JSONResponse(
            status_code=404,
            content=_error(code="RUN_NOT_FOUND", message="run not found", context={"run_id": run_id}),
        )
    return _success(data=engine.snapshot_run(run.run_id) or {})


@router.post("/{run_id}/step")
def step_run(run_id: str, request: Request) -> dict:
    engine: SimulationEngine = request.app.state.sim_engine
    run = engine.step_run(run_id, force=True)
    if run is None:
        return JSONResponse(
            status_code=404,
            content=_error(code="RUN_NOT_FOUND", message="run not found", context={"run_id": run_id}),
        )
    return _success(data=engine.snapshot_run(run.run_id) or {})


@router.get("/{run_id}/save")
def save_run(run_id: str, request: Request) -> dict:
    engine: SimulationEngine = request.app.state.sim_engine
    state = engine.save_run(run_id)
    if state is None:
        return JSONResponse(
            status_code=404,
            content=_error(code="RUN_NOT_FOUND", message="run not found", context={"run_id": run_id}),
        )
    return _success(data=state)


@router.post("/load")
def load_run(payload: dict, request: Request) -> dict:
    engine: SimulationEngine = request.app.state.sim_engine
    try:
        run = engine.load_run(payload)
    except ValueError as exc:
        return JSONResponse(
            status_code=400,
            content=_error(code="INCOMPATIBLE_STATE", message=str(exc)),
        )
    except KeyError as exc:
        return JSONResponse(
            status_code=400,
            content=_error(code="INVALID_STATE_SCHEMA", message=f"missing field: {str(exc)}"),
        )
    return _success(data=engine.snapshot_run(run.run_id) or {})


@router.post("/{run_id}/objects/{name}/thrust")
def update_thrust(run_id: str, name: str, payload: dict, request: Request) -> dict:
    engine: SimulationEngine = request.app.state.sim_engine
    success = engine.update_object_thrust(
        run_id=run_id,
        object_name=name,
        is_active=payload.get("is_active", False),
        magnitude=payload.get("magnitude", 0.0),
        angle_rad=payload.get("angle_rad", 0.0)
    )
    if not success:
        return JSONResponse(
            status_code=404,
            content=_error(code="OBJECT_NOT_FOUND", message="object not found in run", context={"run_id": run_id, "object_name": name}),
        )
    return _success(data=engine.snapshot_run(run_id) or {})


@router.post("/{run_id}/predict")
def predict_trajectory(run_id: str, payload: BurnSequence, request: Request) -> dict:
    engine: SimulationEngine = request.app.state.sim_engine

    burn_plan = [Burn(start_t=b.start_t, duration=b.duration, magnitude=b.magnitude, angle_rad=b.angle_rad) for b in payload.burns]

    prediction = engine.predict_trajectory(
        run_id=run_id,
        object_name=payload.object_name,
        burn_plan=burn_plan,
        lookahead_duration=payload.lookahead_duration
    )

    if "error" in prediction:
        return JSONResponse(
            status_code=404,
            content=_error(code="PREDICTION_FAILED", message=prediction["error"]),
        )

    return _success(data=prediction)

@router.get("/{run_id}/telemetry")
async def run_telemetry(run_id: str, request: Request):
    engine: SimulationEngine = request.app.state.sim_engine
    # Check if run exists
    if engine.snapshot_run(run_id) is None:
        return JSONResponse(
            status_code=404,
            content=_error(code="RUN_NOT_FOUND", message="run not found", context={"run_id": run_id}),
        )

    queue = await engine.subscribe(run_id)

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break

                try:
                    # Wait for next telemetry update
                    data = await asyncio.wait_for(queue.get(), timeout=1.0)
                    yield {"event": "message", "data": json.dumps(data)}
                except asyncio.TimeoutError:
                    # Send heartbeat to keep connection alive
                    yield {"event": "ping", "data": "heartbeat"}
        finally:
            engine.unsubscribe(run_id, queue)

    return EventSourceResponse(event_generator())


@router.post("/{run_id}/objects/catalog/{object_name}")
def add_catalog_object(run_id: str, object_name: str, request: Request) -> dict:
    engine: SimulationEngine = request.app.state.sim_engine
    run = engine.add_catalog_object(run_id, object_name)
    if run is None:
        return JSONResponse(
            status_code=404,
            content=_error(code="RUN_OR_OBJECT_NOT_FOUND", message="run or catalog object not found", context={"run_id": run_id, "object_name": object_name}),
        )
    return _success(data=engine.snapshot_run(run.run_id) or {})


@router.delete("/{run_id}/objects/{name}")
def remove_object(run_id: str, name: str, request: Request) -> dict:
    engine: SimulationEngine = request.app.state.sim_engine
    run = engine.remove_object(run_id, name)
    if run is None:
        return JSONResponse(
            status_code=404,
            content=_error(code="OBJECT_NOT_FOUND", message="object not found in run", context={"run_id": run_id, "object_name": name}),
        )
    return _success(data=engine.snapshot_run(run.run_id) or {})


@router.post("/{run_id}/objects")
def add_custom_object(run_id: str, payload: ObjectCreateRequest, request: Request) -> dict:
    engine: SimulationEngine = request.app.state.sim_engine
    try:
        run = engine.add_custom_object(
            run_id=run_id,
            name=payload.name,
            mass=payload.mass,
            x=payload.x,
            y=payload.y,
            vx=payload.vx,
            vy=payload.vy,
        )
    except ValueError as exc:
        return JSONResponse(
            status_code=400,
            content=_error(code="INVALID_OBJECT", message=str(exc), context={"run_id": run_id}),
        )
    if run is None:
        return JSONResponse(
            status_code=404,
            content=_error(code="RUN_NOT_FOUND", message="run not found", context={"run_id": run_id}),
        )
    return _success(data=engine.snapshot_run(run.run_id) or {})


@router.post("/{run_id}/params")
def update_runtime_params(run_id: str, payload: RuntimeParamsRequest, request: Request) -> dict:
    engine: SimulationEngine = request.app.state.sim_engine
    try:
        run = engine.update_runtime_params(
            run_id=run_id,
            timestep=payload.timestep,
            g=payload.g,
            central_mass=payload.central_mass,
            angular_momentum=payload.angular_momentum,
        )
    except ValueError as exc:
        return JSONResponse(
            status_code=400,
            content=_error(code="INVALID_PARAMS", message=str(exc), context={"run_id": run_id}),
        )
    if run is None:
        return JSONResponse(
            status_code=404,
            content=_error(code="RUN_NOT_FOUND", message="run not found", context={"run_id": run_id}),
        )
    return _success(data=engine.snapshot_run(run.run_id) or {})


@router.post("/{run_id}/validate")
def validate_run(run_id: str, request: Request) -> dict:
    engine: SimulationEngine = request.app.state.sim_engine
    results = engine.run_validation_suite(run_id)
    
    # Check if run exists
    if engine.snapshot_run(run_id) is None:
        return JSONResponse(
            status_code=404,
            content=_error(code="RUN_NOT_FOUND", message="run not found", context={"run_id": run_id}),
        )
        
    if not results:
        return _success(data={"results": [], "status": "insufficient_data"})
    
    # Serialize ValidationResult objects
    serialized_results = []
    for r in results:
        serialized_results.append({
            "test_name": r.test_name,
            "is_passed": r.is_passed,
            "actual": float(r.actual_value),
            "expected": float(r.expected_value),
            "deviation": float(r.deviation),
            "units": r.units
        })
    
    return _success(data={"results": serialized_results, "status": "complete"})
