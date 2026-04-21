import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.health import router as health_router
from app.api.routers.runs import router as runs_router
from app.api.routers.reports import router as reports_router
from app.domain.simulation.engine import SimulationEngine


async def simulation_loop(engine: SimulationEngine):
    """Background loop to step the simulation and broadcast telemetry."""
    dt = 1 / 60
    while True:
        start_time = asyncio.get_event_loop().time()
        try:
            await engine.run_step_and_broadcast()
        except Exception as exc:
            # Prevent loop from crashing due to unexpected simulation errors
            print(f"Simulation loop error: {exc}")
        
        elapsed = asyncio.get_event_loop().time() - start_time
        await asyncio.sleep(max(0, dt - elapsed))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize engine and start background loop
    engine = SimulationEngine()
    app.state.sim_engine = engine
    loop_task = asyncio.create_task(simulation_loop(engine))
    yield
    # Shutdown: Stop the background loop
    loop_task.cancel()
    try:
        await loop_task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="GRsimulator API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(runs_router)
app.include_router(reports_router)
