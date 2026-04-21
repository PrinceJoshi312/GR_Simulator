# Review Role: Edge Case Hunter

## Instructions
You are an elite code reviewer performing an **Edge Case Review**. You receive the diff below and have read access to the project.

Your goal is to identify unhandled edge cases, boundary condition failures, race conditions, and error handling gaps in the provided changes.

Output your findings as a Markdown list.

## Diff to Review
```diff
diff --git a/backend/app/api/routers/runs.py b/backend/app/api/routers/runs.py
new file mode 100644
index 0000000..5751f94
--- /dev/null
+++ b/backend/app/api/routers/runs.py
@@ -0,0 +1,188 @@
+import asyncio
+import json
+from uuid import uuid4
+
+from fastapi import APIRouter, Request
+from fastapi.responses import JSONResponse
+from sse_starlette.sse import EventSourceResponse
+
+from app.contracts.runs import ObjectCreateRequest, RunCreateRequest, RuntimeParamsRequest     
+from app.domain.simulation.engine import SimulationEngine      
+
+router = APIRouter(prefix="/runs", tags=["runs"])
+
+
+def _success(data: dict, request_id: str | None = None) -> dict:
+    return {"data": data, "meta": {"request_id": request_id or str(uuid4())}, "error": None}   
+
+
+def _error(code: str, message: str, context: dict | None = None, request_id: str | None = None) -> dict:
+    return {
+        "data": None,
+        "meta": {"request_id": request_id or str(uuid4())},    
+        "error": {"code": code, "message": message, "context": context or {}, "hint": "Check request parameters"},
+    }
+
+
+@router.post("")
+def create_run(payload: RunCreateRequest, request: Request) -> dict:
+    engine: SimulationEngine = request.app.state.sim_engine    
+    try:
+        run = engine.start_run(
+            scenario_id=payload.scenario_id,
+            seed=payload.seed, 
+            g=payload.g,       
+            central_mass=payload.central_mass,
+        )
+    except ValueError as exc:
+        return JSONResponse(   
+            status_code=400,
+            content=_error(code="INVALID_RUN_PARAMS", message=str(exc), context={"scenario_id": payload.scenario_id}),
+        )
+    return _success(data=engine.snapshot_run(run.run_id) or {})
+
+
+@router.post("/{run_id}/pause")
+def pause_run(run_id: str, request: Request) -> dict:
+    engine: SimulationEngine = request.app.state.sim_engine    
+    run = engine.pause_run(run_id)
+    if run is None:
+        return JSONResponse(   
+            status_code=404,   
+            content=_error(code="RUN_NOT_FOUND", message="run not found", context={"run_id": run_id}),
+        )
+    return _success(data=engine.snapshot_run(run.run_id) or {})
+
+
+@router.post("/{run_id}/resume")
+def resume_run(run_id: str, request: Request) -> dict:
+    engine: SimulationEngine = request.app.state.sim_engine    
+    run = engine.resume_run(run_id)
+    if run is None:
+        return JSONResponse(
+            status_code=404,
+            content=_error(code="RUN_NOT_FOUND", message="run not found", context={"run_id": run_id}),
+        )
+    return _success(data=engine.snapshot_run(run.run_id) or {})
+
+
+@router.post("/{run_id}/reset")
+def reset_run(run_id: str, request: Request) -> dict:
+    engine: SimulationEngine = request.app.state.sim_engine    
+    run = engine.reset_run(run_id)
+    if run is None:
+        return JSONResponse(   
+            status_code=404,   
+            content=_error(code="RUN_NOT_FOUND", message="run not found", context={"run_id": run_id}),
+        )
+    return _success(data=engine.snapshot_run(run.run_id) or {})
+
+
+@router.get("/{run_id}/telemetry")
+async def run_telemetry(run_id: str, request: Request):        
+    engine: SimulationEngine = request.app.state.sim_engine    
+    # Check if run exists
+    if engine.snapshot_run(run_id) is None:
+        return JSONResponse(   
+            status_code=404,   
+            content=_error(code="RUN_NOT_FOUND", message="run not found", context={"run_id": run_id}),
+        )
+
+    queue = await engine.subscribe(run_id)
+
+    async def event_generator():
+        try:
+            while True:        
+                if await request.is_disconnected():
+                    break
+
+                try:
+                    # Wait for next telemetry update
+                    data = await asyncio.wait_for(queue.get(), timeout=1.0)
+                    yield {"event": "message", "data": json.dumps(data)}
+                except asyncio.TimeoutError:
+                    # Send heartbeat to keep connection alive  
+                    yield {"event": "ping", "data": "heartbeat"}
+        finally:
+            engine.unsubscribe(run_id, queue)
+
+    return EventSourceResponse(event_generator())
+
+
+@router.post("/{run_id}/objects/catalog/{object_name}")        
+def add_catalog_object(run_id: str, object_name: str, request: Request) -> dict:
+    engine: SimulationEngine = request.app.state.sim_engine    
+    run = engine.add_catalog_object(run_id, object_name)       
+    if run is None:
+        return JSONResponse(   
+            status_code=404,   
+            content=_error(code="RUN_OR_OBJECT_NOT_FOUND", message="run or catalog object not found", context={"run_id": run_id, "object_name": object_name}), 
+        )
+    return _success(data=engine.snapshot_run(run.run_id) or {})
+
+
+@router.post("/{run_id}/objects")
+def add_custom_object(run_id: str, payload: ObjectCreateRequest, request: Request) -> dict:    
+    engine: SimulationEngine = request.app.state.sim_engine    
+    try:
+        run = engine.add_custom_object(
+            run_id=run_id,     
+            name=payload.name,
+            mass=payload.mass,
+            x=payload.x,       
+            y=payload.y,       
+            vx=payload.vx,
+            vy=payload.vy,     
+        )
+    except ValueError as exc:  
+        return JSONResponse(   
+            status_code=400,   
+            content=_error(code="INVALID_OBJECT", message=str(exc), context={"run_id": run_id}),
+        )
+    if run is None:
+        return JSONResponse(   
+            status_code=404,   
+            content=_error(code="RUN_NOT_FOUND", message="run not found", context={"run_id": run_id}),
+        )
+    return _success(data=engine.snapshot_run(run.run_id) or {})
+
+
+@router.post("/{run_id}/params")
+def update_runtime_params(run_id: str, payload: RuntimeParamsRequest, request: Request) -> dict:
+    engine: SimulationEngine = request.app.state.sim_engine    
+    try:
+        run = engine.update_runtime_params(
+            run_id=run_id,     
+            timestep=payload.timestep,
+            g=payload.g,
+            central_mass=payload.central_mass,
+        )
+    except ValueError as exc:  
+        return JSONResponse(   
+            status_code=400,
+            content=_error(code="INVALID_PARAMS", message=str(exc), context={"run_id": run_id}),
+        )
+    if run is None:
+        return JSONResponse(   
+            status_code=404,   
+            content=_error(code="RUN_NOT_FOUND", message="run not found", context={"run_id": run_id}),
+        )
+    return _success(data=engine.snapshot_run(run.run_id) or {})
+
+
+@router.post("/{run_id}/validate")
+def validate_run(run_id: str, request: Request) -> dict:       
+    engine: SimulationEngine = request.app.state.sim_engine    
+    results = engine.run_validation_suite(run_id)
+    
+    # Check if run exists
+    if engine.snapshot_run(run_id) is None:
+        return JSONResponse(
+            status_code=404,
+            content=_error(code="RUN_NOT_FOUND", message="run not found", context={"run_id": run_id}),
+        )
+        
+    if not results:
+        return _success(data={"results": [], "status": "insufficient_data"})
+    
+    return _success(data={"results": results, "status": "complete"})
diff --git a/backend/app/domain/simulation/engine.py b/backend/app/domain/simulation/engine.py  
new file mode 100644
index 0000000..3e8a50d
--- /dev/null
+++ b/backend/app/domain/simulation/engine.py
@@ -0,0 +1,390 @@
+import asyncio
+from dataclasses import dataclass
+from math import isfinite      
+from uuid import uuid4
+
+import numpy as np
+
+from app.domain.physics.christoffel import equatorial_christoffel
+from app.domain.physics.metric import schwarzschild_metric     
+from app.domain.validation.benchmarks import run_mercury_precession_benchmark, validate_orbit_circularity
+from app.domain.validation.checker import validate_object_state
+
+
+@dataclass
+class ObjectState:
+    x: np.float64
+    y: np.float64
+    vx: np.float64
+    vy: np.float64
+    proper_time: np.float64 = np.float64(0.0)
+    coordinate_time: np.float64 = np.float64(0.0)
+
+
+@dataclass
+class SimulationObject:        
+    name: str
+    mass: np.float64
+    state: ObjectState
+
+
+@dataclass
+class SimulationRun:
+    run_id: str
+    state: str
+    scenario_id: str
+    seed: int
+    g: float
+    central_mass: float        
+    engine_version: str = "0.1.0"
+    app_version: str = "0.1.0" 
+    object_state: ObjectState | None = None
+    objects: list[SimulationObject] | None = None
+    timestep: np.float64 = np.float64(1.0)
+    baseline_objects: list[SimulationObject] | None = None     
+    baseline_g: float = 0.0    
+    baseline_central_mass: float = 0.0
+    baseline_timestep: np.float64 = np.float64(1.0)
+    telemetry_history: dict[str, list[dict]] = None
+
+
+class SimulationEngine:        
+    def __init__(self) -> None:
+        self._runs: dict[str, SimulationRun] = {}
+        self._queues: dict[str, list[asyncio.Queue]] = {}      
+        self._catalog = {      
+            "mercury": {"mass": np.float64(3.3011e23), "x": np.float64(5.79e10), "y": np.float64(0.0), "vx": np.float64(0.0), "vy": np.float64(4.74e4)},       
+            "earth": {"mass": np.float64(5.972e24), "x": np.float64(1.496e11), "y": np.float64(0.0), "vx": np.float64(0.0), "vy": np.float64(2.98e4)},
+        }
+
+    @staticmethod
+    def _clone_object_state(state: ObjectState) -> ObjectState:
+        return ObjectState(    
+            x=np.float64(state.x),
+            y=np.float64(state.y),
+            vx=np.float64(state.vx),
+            vy=np.float64(state.vy),
+            proper_time=np.float64(state.proper_time),
+            coordinate_time=np.float64(state.coordinate_time), 
+        )
+
+    @classmethod
+    def _clone_sim_object(cls, obj: SimulationObject) -> SimulationObject:
+        return SimulationObject(name=obj.name, mass=np.float64(obj.mass), state=cls._clone_object_state(obj.state))
+
+    def _serialize_run(self, run: SimulationRun) -> dict:      
+        def _state_to_dict(state: ObjectState) -> dict:        
+            return {
+                "x": float(state.x),
+                "y": float(state.y),
+                "vx": float(state.vx),
+                "vy": float(state.vy),
+                "proper_time": float(state.proper_time),       
+                "coordinate_time": float(state.coordinate_time),
+            }
+
+        objects = run.objects or []
+        return {
+            "run_id": run.run_id,
+            "state": run.state,
+            "scenario_id": run.scenario_id,
+            "seed": run.seed,  
+            "g": run.g,        
+            "central_mass": run.central_mass,
+            "engine_version": run.engine_version,
+            "app_version": run.app_version,
+            "timestep": float(run.timestep),
+            "objects": [{"name": obj.name, "mass": float(obj.mass), "state": _state_to_dict(obj.state)} for obj in objects],   
+        }
+
+    def start_run(self, scenario_id: str, seed: int, g: float, central_mass: float) -> SimulationRun:
+        metric = schwarzschild_metric(central_mass=central_mass, g=g, r=5.79e10)
+        _ = equatorial_christoffel(metric)
+        initial_objects = [    
+            SimulationObject(  
+                name="mercury",
+                mass=np.float64(3.3011e23),
+                state=ObjectState(
+                    x=np.float64(5.79e10),
+                    y=np.float64(0.0),
+                    vx=np.float64(0.0),
+                    vy=np.float64(4.74e4),
+                ),
+            )
+        ]
+        run = SimulationRun(   
+            run_id=str(uuid4()),
+            state="running",   
+            scenario_id=scenario_id,
+            seed=seed,
+            g=g,
+            central_mass=central_mass,
+            object_state=self._clone_object_state(initial_objects[0].state),
+            objects=[self._clone_sim_object(obj) for obj in initial_objects],
+            baseline_objects=[self._clone_sim_object(obj) for obj in initial_objects],
+            baseline_g=float(g),
+            baseline_central_mass=float(central_mass),
+            baseline_timestep=np.float64(1.0),
+            telemetry_history={},
+        )
+        self._runs[run.run_id] = run
+        return run
+
+    def snapshot_run(self, run_id: str) -> dict | None:        
+        run = self._runs.get(run_id)
+        if run is None:        
+            return None        
+        # Ensure we capture the latest state even if updated in background loop
+        return self._serialize_run(run)
+
+    def add_catalog_object(self, run_id: str, object_name: str) -> SimulationRun | None:       
+        run = self._runs.get(run_id)
+        spec = self._catalog.get(object_name.lower())
+        if run is None or spec is None or run.state != "running":
+            return None        
+        return self.add_custom_object(
+            run_id=run_id,     
+            name=object_name.lower(),
+            mass=float(spec["mass"]),
+            x=float(spec["x"]),
+            y=float(spec["y"]),
+            vx=float(spec["vx"]),
+            vy=float(spec["vy"]),
+        )
+
+    def add_custom_object(self, run_id: str, name: str, mass: float, x: float, y: float, vx: float, vy: float) -> SimulationRun | None:
+        run = self._runs.get(run_id)
+        if run is None or run.state != "running":
+            return None        
+        if mass <= 0 or not all(isfinite(v) for v in [mass, x, y, vx, vy]):
+            raise ValueError("invalid object parameters")      
+        if run.objects is None:
+            run.objects = []   
+        run.objects.append(    
+            SimulationObject(  
+                name=name,     
+                mass=np.float64(mass),
+                state=ObjectState(x=np.float64(x), y=np.float64(y), vx=np.float64(vx), vy=np.float64(vy)),
+            )
+        )
+        return run
+
+    def update_runtime_params(self, run_id: str, timestep: float, g: float, central_mass: float) -> SimulationRun | None:      
+        run = self._runs.get(run_id)
+        if run is None or run.state != "running":
+            return None        
+        if not all(isfinite(v) for v in [timestep, g, central_mass]):
+            raise ValueError("runtime parameters must be finite")
+        if timestep <= 0 or g <= 0 or central_mass <= 0:       
+            raise ValueError("invalid runtime parameters")     
+        run.timestep = np.float64(timestep)
+        run.g = float(g)       
+        run.central_mass = float(central_mass)
+        return run
+
+    def step_run(self, run_id: str, dt: float | None = None) -> SimulationRun | None:
+        run = self._runs.get(run_id)
+        if run is None or run.state != "running":
+            return None        
+        dt_value = float(run.timestep if dt is None else dt)   
+        if not isfinite(dt_value) or dt_value <= 0:
+            raise ValueError("dt must be finite and positive") 
+
+        dt64 = np.float64(dt_value)
+        for obj in run.objects or []:
+            state = obj.state  
+            r = np.float64(np.sqrt((state.x * state.x) + (state.y * state.y)))
+            if r <= np.float64(0.0):
+                raise ValueError("object radius must be greater than zero")
+            metric = schwarzschild_metric(central_mass=run.central_mass, g=run.g, r=float(r))  
+            gamma = equatorial_christoffel(metric)
+
+            vx = np.float64(state.vx)
+            vy = np.float64(state.vy)
+            radial_velocity = np.float64((state.x * vx + state.y * vy) / r)
+            phi_dot = np.float64((state.x * vy - state.y * vx) / (r * r))
+            ar = np.float64(   
+                -(
+                    gamma["gamma_r_tt"]
+                    + gamma["gamma_r_rr"] * radial_velocity * radial_velocity
+                    + gamma["gamma_r_phiphi"] * phi_dot * phi_dot
+                )
+            )
+            ax = np.float64(ar * state.x / r)
+            ay = np.float64(ar * state.y / r)
+
+            state.vx = np.float64(state.vx + ax * dt64)        
+            state.vy = np.float64(state.vy + ay * dt64)        
+            state.x = np.float64(state.x + state.vx * dt64)    
+            state.y = np.float64(state.y + state.vy * dt64)    
+            state.coordinate_time = np.float64(state.coordinate_time + dt64)
+            c2 = np.float64(metric["c"] * metric["c"])
+            speed_sq = np.float64(state.vx * state.vx + state.vy * state.vy)
+            lapse = np.float64(max(-metric["g_tt"] - (speed_sq / c2), 1e-12))
+            dilation = np.float64(np.sqrt(lapse))
+            state.proper_time = np.float64(state.proper_time + (dt64 * dilation))
+
+            # Record telemetry history
+            if run.telemetry_history is None:
+                run.telemetry_history = {}
+            if obj.name not in run.telemetry_history:
+                run.telemetry_history[obj.name] = []
+
+            history = run.telemetry_history[obj.name]
+            history.append({   
+                "x": float(state.x),
+                "y": float(state.y),
+                "r": float(r), 
+                "t": float(state.coordinate_time)
+            })
+
+            # Limit history to prevent memory leaks (AC: 5)    
+            if len(history) > 50000:
+                history.pop(0) 
+
+        if run.objects:        
+            run.object_state = run.objects[0].state
+        return run
+
+    def pause_run(self, run_id: str) -> SimulationRun | None:  
+        run = self._runs.get(run_id)
+        if run:
+            run.state = "paused"
+        return run
+
+    def resume_run(self, run_id: str) -> SimulationRun | None: 
+        run = self._runs.get(run_id)
+        if run:
+            run.state = "running"
+        return run
+
+    def reset_run(self, run_id: str) -> SimulationRun | None:  
+        run = self._runs.get(run_id)
+        if run:
+            run.state = "idle" 
+            run.g = run.baseline_g
+            run.central_mass = run.baseline_central_mass       
+            run.timestep = np.float64(run.baseline_timestep)   
+            run.telemetry_history = {}
+            if run.baseline_objects is not None:
+                run.objects = [self._clone_sim_object(obj) for obj in run.baseline_objects]    
+                run.object_state = self._clone_object_state(run.objects[0].state)
+        return run
+
+    def run_validation_suite(self, run_id: str) -> list[dict]: 
+        run = self._runs.get(run_id)
+        if not run or "mercury" not in run.telemetry_history:  
+            return []
+
+        history = run.telemetry_history["mercury"]
+        if len(history) < 100: 
+            return []
+
+        # 1. Identify perihelion points (local minima of r)    
+        radii = [h["r"] for h in history]
+        perihelia_indices = [] 
+        for i in range(1, len(radii) - 1):
+            if radii[i] < radii[i-1] and radii[i] < radii[i+1]:
+                perihelia_indices.append(i)
+
+        results = []
+        
+        # 2. Calculate precession if we have at least 2 orbits 
+        if len(perihelia_indices) >= 2:
+            angles = [np.arctan2(history[i]["y"], history[i]["x"]) for i in perihelia_indices] 
+            # Normalize angles to [0, 2pi]
+            angles = [(a + 2*np.pi) % (2*np.pi) for a in angles]
+
+            # Calculate deltas (precession per rev)
+            deltas = []        
+            for i in range(1, len(angles)):
+                diff = angles[i] - angles[i-1]
+                # Account for wrap-around
+                if diff < -np.pi: diff += 2*np.pi
+                if diff > np.pi: diff -= 2*np.pi
+                deltas.append(abs(diff))
+
+            avg_precession = float(np.mean(deltas)) if deltas else 0.0
+
+            # Use semi-major axis from Mercury catalog if possible, 
+            # otherwise estimate from min/max r in history     
+            a_est = (max(radii) + min(radii)) / 2.0
+            e_est = (max(radii) - min(radii)) / (max(radii) + min(radii))
+
+            bench_res = run_mercury_precession_benchmark(      
+                actual_precession_rad_per_rev=avg_precession,  
+                g=run.g,
+                m=run.central_mass,
+                a=a_est,
+                e=e_est
+            )
+            results.append({   
+                "test_name": bench_res.test_name,
+                "is_passed": bench_res.is_passed,
+                "actual": bench_res.actual_value,
+                "expected": bench_res.expected_value,
+                "deviation": bench_res.deviation,
+                "units": bench_res.units
+            })
+
+        # 3. Circularity check (if applicable, though Mercury is eccentric)
+        # For now, just report the radius stability as a secondary metric
+        stab_res = validate_orbit_circularity(radii, expected_radius=history[0]["r"])
+        results.append({
+            "test_name": stab_res.test_name,
+            "is_passed": stab_res.is_passed,
+            "actual": stab_res.actual_value,
+            "expected": stab_res.expected_value,
+            "deviation": stab_res.deviation,
+            "units": stab_res.units
+        })
+
+        return results
+
+    async def subscribe(self, run_id: str) -> asyncio.Queue:   
+        if run_id not in self._queues:
+            self._queues[run_id] = []
+        queue = asyncio.Queue(maxsize=100)
+        self._queues[run_id].append(queue)
+        return queue
+
+    def unsubscribe(self, run_id: str, queue: asyncio.Queue) -> None:
+        if run_id in self._queues:
+            try:
+                self._queues[run_id].remove(queue)
+                if not self._queues[run_id]:
+                    del self._queues[run_id]
+            except ValueError:
+                pass
+
+    async def run_step_and_broadcast(self) -> None:
+        active_ids = [rid for rid, run in self._runs.items() if run.state == "running"]        
+        for rid in active_ids:
+            self.step_run(rid)
+            await self.broadcast_telemetry(rid)
+
+    async def broadcast_telemetry(self, run_id: str) -> None:  
+        run = self._runs.get(run_id)
+        if not run or run_id not in self._queues:
+            return
+        
+        telemetry = self.snapshot_run(run_id)
+        if not telemetry:      
+            return
+
+        # Scientific constants for validation
+        c = 299792458.0
+        rs = (2.0 * run.g * run.central_mass) / (c**2)
+
+        # Enhance telemetry with validation signals for every object
+        for obj_data in telemetry.get("objects", []):
+            st = obj_data["state"]
+            obj_data["validation"] = validate_object_state(st["x"], st["y"], st["vx"], st["vy"], rs)
+
+        for queue in self._queues[run_id]:
+            try:
+                if queue.full():
+                    queue.get_nowait()
+                queue.put_nowait(telemetry)
+            except Exception:
+                pass
+diff --git a/backend/app/domain/validation/benchmarks.py b/backend/app/domain/validation/benchmarks.py
new file mode 100644
index 0000000..37da652
--- /dev/null
+++ b/backend/app/domain/validation/benchmarks.py
@@ -0,0 +1,75 @@
+import numpy as np
+from dataclasses import dataclass
+
+@dataclass
+class ValidationResult:        
+    test_name: str
+    pass_threshold: float      
+    actual_value: float        
+    expected_value: float      
+    is_passed: bool
+    deviation: float
+    units: str
+
+def calculate_theoretical_precession(g: float, m: float, a: float, e: float) -> float:
+    """
+    Calculates the Schwarzschild precession per revolution in radians.
+    Formula: delta_phi = (6 * pi * G * M) / (c^2 * a * (1 - e^2))
+    """
+    c = 299792458.0
+    numerator = 6.0 * np.pi * g * m
+    denominator = (c**2) * a * (1.0 - e**2)
+    return float(numerator / denominator)
+
+def run_mercury_precession_benchmark(
+    actual_precession_rad_per_rev: float,
+    g: float,
+    m: float,
+    a: float = 5.7909e10,      
+    e: float = 0.2056,
+    threshold: float = 0.05  # 5% default threshold for numerical integration
+) -> ValidationResult:
+    """
+    Compares simulated Mercury precession against the theoretical GR prediction.
+    """
+    expected = calculate_theoretical_precession(g, m, a, e)    
+    
+    # Calculate relative deviation
+    if expected == 0:
+        deviation = 0.0        
+    else:
+        deviation = abs(actual_precession_rad_per_rev - expected) / expected
+        
+    is_passed = bool(deviation <= threshold)
+    
+    return ValidationResult(   
+        test_name="Mercury Perihelion Precession",
+        pass_threshold=float(threshold),
+        actual_value=float(actual_precession_rad_per_rev),     
+        expected_value=float(expected),
+        is_passed=is_passed,   
+        deviation=float(deviation),
+        units="rad/rev"        
+    )
+
+def validate_orbit_circularity(
+    radii: list[float],        
+    expected_radius: float,    
+    threshold: float = 0.001   
+) -> ValidationResult:
+    """
+    Validates that a supposedly circular orbit maintains its radius.
+    """
+    avg_radius = np.mean(radii)
+    deviation = abs(avg_radius - expected_radius) / expected_radius
+    is_passed = bool(deviation <= threshold)
+    
+    return ValidationResult(   
+        test_name="Orbital Radius Stability",
+        pass_threshold=float(threshold),
+        actual_value=float(avg_radius),
+        expected_value=float(expected_radius),
+        is_passed=is_passed,   
+        deviation=float(deviation),
+        units="m"
+    )
+```
+