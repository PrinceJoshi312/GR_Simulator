from pydantic import BaseModel
from typing import List


class RunCreateRequest(BaseModel):
    scenario_id: str = "default-schwarzschild"
    seed: int = 42
    g: float = 6.6743e-11
    central_mass: float = 1.98847e30
    angular_momentum: float = 0.0


class ObjectCreateRequest(BaseModel):
    name: str
    mass: float
    x: float
    y: float
    vx: float
    vy: float


class RuntimeParamsRequest(BaseModel):
    timestep: float
    g: float
    central_mass: float
    angular_momentum: float = 0.0


class Burn(BaseModel):
    start_t: float
    duration: float
    magnitude: float
    angle_rad: float


class BurnSequence(BaseModel):
    object_name: str
    lookahead_duration: float
    burns: List[Burn]


class RunLifecycleResponse(BaseModel):
    run_id: str
    state: str
    scenario_id: str
    seed: int
    g: float
    central_mass: float
    angular_momentum: float = 0.0
    engine_version: str = "0.2.0"  
    app_version: str = "0.2.0"     

