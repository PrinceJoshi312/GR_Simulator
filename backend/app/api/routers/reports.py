import datetime
from typing import Any
from uuid import uuid4
from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse, StreamingResponse
from app.domain.simulation.engine import SimulationEngine
from app.domain.validation.reports import generate_accuracy_report
from app.domain.validation.exports import generate_metadata, generate_csv_export, generate_numpy_export

router = APIRouter(prefix="/reports", tags=["reports"])

def _success(data: dict, request_id: str | None = None) -> dict:
    return {"data": data, "meta": {"request_id": request_id or str(uuid4())}, "error": None}

def _error(code: str, message: str, context: dict | None = None, request_id: str | None = None) -> dict:
    return {
        "data": None,
        "meta": {"request_id": request_id or str(uuid4())},
        "error": {"code": code, "message": message, "context": context or {}, "hint": "Check request parameters"},
    }

@router.get("/{run_id}/accuracy")
def get_accuracy_report(run_id: str, request: Request) -> dict:
    engine: SimulationEngine = request.app.state.sim_engine
    metadata = engine.get_run_metadata(run_id)
    if metadata is None:
        return JSONResponse(
            status_code=404,
            content=_error(code="RUN_NOT_FOUND", message="run not found", context={"run_id": run_id}),
        )

    results = engine.run_validation_suite(run_id)
    report = generate_accuracy_report(run_id, results, metadata)
    return _success(data=report)

@router.get("/{run_id}/exports/csv")
def export_csv(run_id: str, request: Request, object_name: str = Query(..., alias="object_name")) -> Any:
    engine: SimulationEngine = request.app.state.sim_engine
    metadata = engine.get_run_metadata(run_id)
    if metadata is None:
        return JSONResponse(
            status_code=404,
            content=_error(code="RUN_NOT_FOUND", message="run not found", context={"run_id": run_id}),
        )

    history = engine.get_telemetry_history(run_id, object_name)
    if history is None:
        return JSONResponse(
            status_code=404,
            content=_error(code="OBJECT_TELEMETRY_NOT_FOUND", message=f"telemetry for {object_name} not found", context={"run_id": run_id, "object_name": object_name}),
        )

    filename = f"telemetry_{run_id}_{object_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        generate_csv_export(history, metadata),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}  
    )

@router.get("/{run_id}/exports/numpy")
def export_numpy(run_id: str, request: Request, object_name: str = Query(..., alias="object_name")) -> Any:
    engine: SimulationEngine = request.app.state.sim_engine
    metadata = engine.get_run_metadata(run_id)
    if metadata is None:
        return JSONResponse(
            status_code=404,
            content=_error(code="RUN_NOT_FOUND", message="run not found", context={"run_id": run_id}),
        )

    history = engine.get_telemetry_history(run_id, object_name)
    if history is None:
        return JSONResponse(
            status_code=404,
            content=_error(code="OBJECT_TELEMETRY_NOT_FOUND", message=f"telemetry for {object_name} not found", context={"run_id": run_id, "object_name": object_name}),
        )

    buffer = generate_numpy_export(history, metadata)
    filename = f"telemetry_{run_id}_{object_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.npz"

    return StreamingResponse(
        buffer,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"}  
    )

