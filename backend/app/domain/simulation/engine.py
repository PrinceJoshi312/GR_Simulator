import asyncio
import collections
from dataclasses import dataclass
from math import isfinite
from typing import Any
from uuid import uuid4

import numpy as np

from app.domain.physics.christoffel import equatorial_christoffel, kerr_equatorial_christoffel
from app.domain.physics.metric import schwarzschild_metric, kerr_metric
from app.domain.validation.benchmarks import run_mercury_precession_benchmark, validate_orbit_circularity
from app.domain.validation.checker import validate_object_state


@dataclass
class ObjectState:
    x: np.float64
    y: np.float64
    vx: np.float64
    vy: np.float64
    # Newtonian baseline for comparison
    nx: np.float64 = np.float64(0.0)
    ny: np.float64 = np.float64(0.0)
    nvx: np.float64 = np.float64(0.0)
    nvy: np.float64 = np.float64(0.0)
    proper_time: np.float64 = np.float64(0.0)
    coordinate_time: np.float64 = np.float64(0.0)

    def to_dict(self) -> dict:
        return {
            "x": float(self.x),
            "y": float(self.y),
            "vx": float(self.vx),
            "vy": float(self.vy),
            "nx": float(self.nx),
            "ny": float(self.ny),
            "nvx": float(self.nvx),
            "nvy": float(self.nvy),
            "proper_time": float(self.proper_time),
            "coordinate_time": float(self.coordinate_time),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ObjectState":
        return cls(
            x=np.float64(data["x"]),
            y=np.float64(data["y"]),
            vx=np.float64(data["vx"]),
            vy=np.float64(data["vy"]),
            nx=np.float64(data.get("nx", data["x"])),
            ny=np.float64(data.get("ny", data["y"])),
            nvx=np.float64(data.get("nvx", data["vx"])),
            nvy=np.float64(data.get("nvy", data["vy"])),
            proper_time=np.float64(data.get("proper_time", 0.0)),
            coordinate_time=np.float64(data.get("coordinate_time", 0.0)),
        )


@dataclass
class ThrustConfig:
    is_active: bool = False
    magnitude: float = 0.0  # Newtons
    angle_rad: float = 0.0  # Direction in xy plane
    mass_loss_rate: float = 0.0  # kg/s

    def to_dict(self) -> dict:
        return {
            "is_active": self.is_active,
            "magnitude": self.magnitude,
            "angle_rad": self.angle_rad,
            "mass_loss_rate": self.mass_loss_rate,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ThrustConfig":
        return cls(
            is_active=data.get("is_active", False),
            magnitude=data.get("magnitude", 0.0),
            angle_rad=data.get("angle_rad", 0.0),
            mass_loss_rate=data.get("mass_loss_rate", 0.0),
        )


@dataclass
class Burn:
    start_t: float
    duration: float
    magnitude: float
    angle_rad: float

    def to_dict(self) -> dict:
        return {
            "start_t": self.start_t,
            "duration": self.duration,
            "magnitude": self.magnitude,
            "angle_rad": self.angle_rad,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Burn":
        return cls(
            start_t=float(data["start_t"]),
            duration=float(data["duration"]),
            magnitude=float(data["magnitude"]),
            angle_rad=float(data["angle_rad"]),
        )


@dataclass
class SimulationObject:
    name: str
    mass: np.float64
    state: ObjectState
    thrust: ThrustConfig | None = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "mass": float(self.mass),
            "state": self.state.to_dict(),
            "thrust": self.thrust.to_dict() if self.thrust else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SimulationObject":
        return cls(
            name=data["name"],
            mass=np.float64(data["mass"]),
            state=ObjectState.from_dict(data["state"]),
            thrust=ThrustConfig.from_dict(data["thrust"]) if data.get("thrust") else None,
        )


@dataclass
class SimulationRun:
    run_id: str
    state: str
    scenario_id: str
    seed: int
    g: float
    central_mass: float
    angular_momentum: float = 0.0 # 'a' parameter for Kerr
    engine_version: str = "0.2.0"
    app_version: str = "0.2.0"
    object_state: ObjectState | None = None
    objects: list[SimulationObject] | None = None
    timestep: np.float64 = np.float64(3600.0)
    baseline_objects: list[SimulationObject] | None = None
    baseline_g: float = 0.0
    baseline_central_mass: float = 0.0
    baseline_timestep: np.float64 = np.float64(3600.0)
    telemetry_history: dict[str, collections.deque] = None

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "state": self.state,
            "scenario_id": self.scenario_id,
            "seed": self.seed,
            "g": self.g,
            "central_mass": self.central_mass,
            "angular_momentum": self.angular_momentum,
            "engine_version": self.engine_version,
            "app_version": self.app_version,
            "timestep": float(self.timestep),
            "object_state": self.object_state.to_dict() if self.object_state else None,
            "objects": [obj.to_dict() for obj in self.objects] if self.objects else [],
            "baseline_g": self.baseline_g,
            "baseline_central_mass": self.baseline_central_mass,
            "baseline_timestep": float(self.baseline_timestep),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SimulationRun":
        run = cls(
            run_id=data["run_id"],
            state=data["state"],
            scenario_id=data["scenario_id"],
            seed=data["seed"],
            g=data["g"],
            central_mass=data["central_mass"],
            angular_momentum=data.get("angular_momentum", 0.0),
            engine_version=data.get("engine_version", "0.2.0"),
            app_version=data.get("app_version", "0.2.0"),
            timestep=np.float64(data.get("timestep", 1.0)),
            baseline_g=data.get("baseline_g", data["g"]),
            baseline_central_mass=data.get("baseline_central_mass", data["central_mass"]),
            baseline_timestep=np.float64(data.get("baseline_timestep", 1.0)),
            telemetry_history={},
        )
        if data.get("object_state"):
            run.object_state = ObjectState.from_dict(data["object_state"])
        if data.get("objects"):
            run.objects = [SimulationObject.from_dict(obj) for obj in data["objects"]]
        return run


class SimulationEngine:
    def __init__(self) -> None:
        self._runs: dict[str, SimulationRun] = {}
        self._queues: dict[str, list[asyncio.Queue]] = {}
        self._catalog = {
            "mercury": {"mass": np.float64(3.3011e23), "x": np.float64(5.79e10), "y": np.float64(0.0), "vx": np.float64(0.0), "vy": np.float64(4.74e4)},
            "venus": {"mass": np.float64(4.867e24), "x": np.float64(1.082e11), "y": np.float64(0.0), "vx": np.float64(0.0), "vy": np.float64(3.50e4)},
            "earth": {"mass": np.float64(5.972e24), "x": np.float64(1.496e11), "y": np.float64(0.0), "vx": np.float64(0.0), "vy": np.float64(2.98e4)},
            "mars": {"mass": np.float64(6.39e23), "x": np.float64(2.279e11), "y": np.float64(0.0), "vx": np.float64(0.0), "vy": np.float64(2.41e4)},
            "jupiter": {"mass": np.float64(1.898e27), "x": np.float64(7.785e11), "y": np.float64(0.0), "vx": np.float64(0.0), "vy": np.float64(1.31e4)},
            "saturn": {"mass": np.float64(5.683e26), "x": np.float64(1.434e12), "y": np.float64(0.0), "vx": np.float64(0.0), "vy": np.float64(9.68e3)},
            "uranus": {"mass": np.float64(8.681e25), "x": np.float64(2.871e12), "y": np.float64(0.0), "vx": np.float64(0.0), "vy": np.float64(6.80e3)},
            "neptune": {"mass": np.float64(1.024e26), "x": np.float64(4.495e12), "y": np.float64(0.0), "vx": np.float64(0.0), "vy": np.float64(5.43e3)},
        }

    def _get_newtonian_derivatives(self, x: np.float64, y: np.float64, vx: np.float64, vy: np.float64, m_central: float, g: float, thrust: ThrustConfig | None = None, mass: np.float64 | None = None) -> tuple[np.float64, np.float64, np.float64, np.float64]:
        r_sq = x**2 + y**2
        r = np.sqrt(r_sq)
        if r <= 0:
            return np.float64(0.0), np.float64(0.0), np.float64(0.0), np.float64(0.0)
        
        accel = -(g * m_central) / r_sq
        ax = np.float64(accel * x / r)
        ay = np.float64(accel * y / r)

        if thrust and thrust.is_active and mass is not None:
            ax += np.float64((thrust.magnitude * np.cos(thrust.angle_rad)) / float(mass))
            ay += np.float64((thrust.magnitude * np.sin(thrust.angle_rad)) / float(mass))

        return vx, vy, ax, ay

    @staticmethod
    def _clone_object_state(state: ObjectState) -> ObjectState:
        return ObjectState(
            x=np.float64(state.x),
            y=np.float64(state.y),
            vx=np.float64(state.vx),
            vy=np.float64(state.vy),
            nx=np.float64(state.nx),
            ny=np.float64(state.ny),
            nvx=np.float64(state.nvx),
            nvy=np.float64(state.nvy),
            proper_time=np.float64(state.proper_time),
            coordinate_time=np.float64(state.coordinate_time),
        )

    def _get_derivatives(self, x: np.float64, y: np.float64, vx: np.float64, vy: np.float64, m_central: float, g: float, a: float = 0.0, thrust: ThrustConfig | None = None, mass: np.float64 | None = None, other_objects: list[SimulationObject] | None = None) -> tuple[np.float64, np.float64, np.float64, np.float64]:
        r = np.sqrt(x**2 + y**2)
        if r <= 0:
            return np.float64(0.0), np.float64(0.0), np.float64(0.0), np.float64(0.0)
        
        # Metric and Christoffel Symbols (Schwarzschild or Kerr)
        if a == 0:
            metric = schwarzschild_metric(central_mass=m_central, g=g, r=float(r))
            gamma = equatorial_christoffel(metric)
        else:
            metric = kerr_metric(central_mass=m_central, g=g, r=float(r), a=a)
            gamma = kerr_equatorial_christoffel(metric)

        # Velocities in coordinate space
        radial_velocity = (x * vx + y * vy) / r
        phi_dot = (x * vy - y * vx) / (r * r)
        
        # Geodesic Equation for radial component
        # d^2r/dtau^2 = -(Gamma^r_tt (dt/dtau)^2 + Gamma^r_rr (dr/dtau)^2 + Gamma^r_phi (dphi/dtau)^2 + 2 Gamma^r_tphi (dt/dtau)(dphi/dtau))
        # Note: We approximate coordinate acceleration for integration in coordinate time dt.
        
        dt_dtau = 1.0 # Approximation for coordinate-time integration
        
        ar_terms = (gamma["gamma_r_tt"] * dt_dtau * dt_dtau + 
                    gamma.get("gamma_r_rr", 0.0) * radial_velocity * radial_velocity + 
                    gamma["gamma_r_phiphi"] * phi_dot * phi_dot)
        
        if "gamma_r_tphi" in gamma:
            ar_terms += 2.0 * gamma["gamma_r_tphi"] * dt_dtau * phi_dot
            
        ar = np.float64(-ar_terms)
        
        ax = np.float64(ar * x / r)
        ay = np.float64(ar * y / r)

        # Apply external thrust if present
        if thrust and thrust.is_active and mass is not None:
            thrust_mag = float(thrust.magnitude)
            thrust_angle = float(thrust.angle_rad)
            max_a = 980.0 # 100g clipping
            ax_t = (thrust_mag * np.cos(thrust_angle)) / float(mass)
            ay_t = (thrust_mag * np.sin(thrust_angle)) / float(mass)
            a_mag = np.sqrt(ax_t**2 + ay_t**2)
            if a_mag > max_a:
                scale = max_a / a_mag
                ax_t *= scale
                ay_t *= scale
            ax += np.float64(ax_t)
            ay += np.float64(ay_t)

        # Add Newtonian contribution from other planets (multi-body interaction)
        if other_objects:
            for other in other_objects:
                dx = other.state.x - x
                dy = other.state.y - y
                r_other_sq = dx**2 + dy**2
                r_other = np.sqrt(r_other_sq)
                if r_other > 1e3: # Avoid singularity and extreme proximity bugs
                    accel = (g * other.mass) / r_other_sq
                    ax += np.float64(accel * dx / r_other)
                    ay += np.float64(accel * dy / r_other)

        return vx, vy, ax, ay

    @classmethod
    def _clone_sim_object(cls, obj: SimulationObject) -> SimulationObject:
        thrust = None
        if obj.thrust:
            thrust = ThrustConfig(
                is_active=obj.thrust.is_active,
                magnitude=obj.thrust.magnitude,
                angle_rad=obj.thrust.angle_rad,
                mass_loss_rate=obj.thrust.mass_loss_rate
            )
        return SimulationObject(
            name=obj.name, 
            mass=np.float64(obj.mass), 
            state=cls._clone_object_state(obj.state),
            thrust=thrust
        )
    def _serialize_run(self, run: SimulationRun) -> dict:
        def _state_to_dict(state: ObjectState) -> dict:
            return {
                "x": float(state.x),
                "y": float(state.y),
                "vx": float(state.vx),
                "vy": float(state.vy),
                "proper_time": float(state.proper_time),
                "coordinate_time": float(state.coordinate_time),
            }

        objects = run.objects or []
        return {
            "run_id": run.run_id,
            "state": run.state,
            "scenario_id": run.scenario_id,
            "seed": run.seed,
            "g": run.g,
            "central_mass": run.central_mass,
            "engine_version": run.engine_version,
            "app_version": run.app_version,
            "timestep": float(run.timestep),
            "objects": [
                {
                    "name": obj.name, 
                    "mass": float(obj.mass), 
                    "state": _state_to_dict(obj.state),
                    "thrust": obj.thrust.to_dict() if obj.thrust else None
                } for obj in objects
            ],
        }

    def start_run(self, scenario_id: str, seed: int, g: float, central_mass: float) -> SimulationRun:
        initial_objects = []
        angular_momentum = 0.0
        
        if scenario_id == "solar-system":
            for name, spec in self._catalog.items():
                initial_objects.append(
                    SimulationObject(
                        name=name,
                        mass=np.float64(spec["mass"]),
                        state=ObjectState(
                            x=np.float64(spec["x"]),
                            y=np.float64(spec["y"]),
                            vx=np.float64(spec["vx"]),
                            vy=np.float64(spec["vy"]),
                            nx=np.float64(spec["x"]),
                            ny=np.float64(spec["y"]),
                            nvx=np.float64(spec["vx"]),
                            nvy=np.float64(spec["vy"]),
                        ),
                    )
                )
        elif scenario_id == "black-hole":
            # High spin, extreme mass black hole
            central_mass = 1.988e31 # 10 Solar Masses
            angular_momentum = 0.95 * ((g * central_mass) / (299792458.0)) # Near-extremal Kerr
            initial_objects = [
                SimulationObject(
                    name="probe",
                    mass=np.float64(1000.0),
                    state=ObjectState(
                        x=np.float64(1.0e5), # Close orbit
                        y=np.float64(0.0),
                        vx=np.float64(0.0),
                        vy=np.float64(1.0e8), # Relativistic speed
                        nx=np.float64(1.0e5),
                        ny=np.float64(0.0),
                        nvx=np.float64(0.0),
                        nvy=np.float64(1.0e8),
                    ),
                )
            ]
        elif scenario_id == "mercury-only":
             spec = self._catalog["mercury"]
             initial_objects = [
                SimulationObject(
                    name="mercury",
                    mass=np.float64(spec["mass"]),
                    state=ObjectState(
                        x=np.float64(spec["x"]),
                        y=np.float64(spec["y"]),
                        vx=np.float64(spec["vx"]),
                        vy=np.float64(spec["vy"]),
                        nx=np.float64(spec["x"]),
                        ny=np.float64(spec["y"]),
                        nvx=np.float64(spec["vx"]),
                        nvy=np.float64(spec["vy"]),
                    ),
                )
             ]
        else:
            # Default to Mercury only if unknown scenario
            initial_objects = [
                SimulationObject(
                    name="mercury",
                    mass=np.float64(3.3011e23),
                    state=ObjectState(
                        x=np.float64(5.79e10),
                        y=np.float64(0.0),
                        vx=np.float64(0.0),
                        vy=np.float64(4.74e4),
                        nx=np.float64(5.79e10),
                        ny=np.float64(0.0),
                        nvx=np.float64(0.0),
                        nvy=np.float64(4.74e4),
                    ),
                )
            ]

        run = SimulationRun(
            run_id=str(uuid4()),
            state="running",
            scenario_id=scenario_id,
            seed=seed,
            g=g,
            central_mass=central_mass,
            angular_momentum=angular_momentum,
            object_state=self._clone_object_state(initial_objects[0].state),
            objects=[self._clone_sim_object(obj) for obj in initial_objects],
            baseline_objects=[self._clone_sim_object(obj) for obj in initial_objects],
            baseline_g=float(g),
            baseline_central_mass=float(central_mass),
            baseline_timestep=np.float64(3600.0),
            telemetry_history={},
        )
        run.timestep = np.float64(3600.0)
        self._runs[run.run_id] = run
        return run

    def snapshot_run(self, run_id: str) -> dict | None:
        run = self._runs.get(run_id)
        if run is None:
            return None
        # Ensure we capture the latest state even if updated in background loop
        return self._serialize_run(run)

    def save_run(self, run_id: str) -> dict | None:
        """Returns the full serializable state of a run."""
        run = self._runs.get(run_id)
        if run is None:
            return None
        return run.to_dict()

    def load_run(self, data: dict) -> SimulationRun:
        """Loads a run from serialized data. Validates version compatibility."""
        # Version validation (AC: 5)
        engine_version = data.get("engine_version", "0.0.0")
        if engine_version > "0.1.0": # Current version
            raise ValueError(f"Incompatible engine version: {engine_version}")
            
        run = SimulationRun.from_dict(data)
        # AC: 3 - generate a fresh run_id to avoid collisions
        run.run_id = str(uuid4())
        self._runs[run.run_id] = run
        return run

    def get_run_metadata(self, run_id: str) -> dict[str, Any] | None:
        """Returns metadata for a specific run without exposing internal state."""
        run = self._runs.get(run_id)
        if run is None:
            return None
        
        c = 299792458.0
        rs = (2.0 * run.g * run.central_mass) / (c**2)
        
        return {
            "run_id": run.run_id,
            "g": float(run.g),
            "central_mass": float(run.central_mass),
            "rs": float(rs),
            "c": float(c),
            "seed": int(run.seed),
            "engine_version": run.engine_version,
            "app_version": run.app_version
        }

    def get_telemetry_history(self, run_id: str, object_name: str) -> list[dict] | None:
        """Returns a snapshot of telemetry history for a specific object."""
        run = self._runs.get(run_id)
        if run and run.telemetry_history and object_name in run.telemetry_history:
            # list() conversion is thread-safe enough for collections.deque in CPython
            return list(run.telemetry_history[object_name])
        return None

    def add_catalog_object(self, run_id: str, object_name: str) -> SimulationRun | None:
        run = self._runs.get(run_id)
        spec = self._catalog.get(object_name.lower())
        if run is None or spec is None or run.state != "running":
            return None
        return self.add_custom_object(
            run_id=run_id,
            name=object_name.lower(),
            mass=float(spec["mass"]),
            x=float(spec["x"]),
            y=float(spec["y"]),
            vx=float(spec["vx"]),
            vy=float(spec["vy"]),
        )

    def add_custom_object(self, run_id: str, name: str, mass: float, x: float, y: float, vx: float, vy: float) -> SimulationRun | None:
        run = self._runs.get(run_id)
        if run is None or run.state != "running":
            return None
        if mass <= 0 or not all(isfinite(v) for v in [mass, x, y, vx, vy]):
            raise ValueError("invalid object parameters")
        if run.objects is None:
            run.objects = []
        run.objects.append(
            SimulationObject(
                name=name,
                mass=np.float64(mass),
                state=ObjectState(x=np.float64(x), y=np.float64(y), vx=np.float64(vx), vy=np.float64(vy)),
            )
        )
        return run

    def remove_object(self, run_id: str, name: str) -> SimulationRun | None:
        run = self._runs.get(run_id)
        if run is None or run.objects is None:
            return None
        
        # Filter out the object by name
        original_count = len(run.objects)
        run.objects = [obj for obj in run.objects if obj.name.lower() != name.lower()]
        
        if len(run.objects) == original_count:
            return None # Object not found
            
        if run.objects:
            run.object_state = run.objects[0].state
        else:
            run.object_state = None
            
        return run

    def update_runtime_params(self, run_id: str, timestep: float, g: float, central_mass: float, angular_momentum: float = 0.0) -> SimulationRun | None:
        run = self._runs.get(run_id)
        if run is None or run.state != "running":
            return None
        if not all(isfinite(v) for v in [timestep, g, central_mass, angular_momentum]):
            raise ValueError("runtime parameters must be finite")
        if timestep <= 0 or g <= 0 or central_mass <= 0:
            raise ValueError("invalid runtime parameters")
        run.timestep = np.float64(timestep)
        run.g = float(g)
        run.central_mass = float(central_mass)
        run.angular_momentum = float(angular_momentum)
        return run

    def update_object_thrust(self, run_id: str, object_name: str, is_active: bool, magnitude: float, angle_rad: float) -> bool:
        """Updates thrust configuration for a specific object."""
        run = self._runs.get(run_id)
        if not run or not run.objects:
            return False
            
        for obj in run.objects:
            if obj.name.lower() == object_name.lower():
                if not obj.thrust:
                    obj.thrust = ThrustConfig()
                
                obj.thrust.is_active = is_active
                obj.thrust.magnitude = float(magnitude)
                obj.thrust.angle_rad = float(angle_rad)
                return True
                
        return False

    def predict_trajectory(self, run_id: str, object_name: str, burn_plan: list[Burn], lookahead_duration: float) -> dict:
        """Runs a fast-forward simulation to predict a trajectory based on a burn plan."""
        run = self._runs.get(run_id)
        if not run or not run.objects:
            return {"path": [], "error": "run or objects not found"}
            
        target_obj = next((obj for obj in run.objects if obj.name.lower() == object_name.lower()), None)
        if not target_obj:
            return {"path": [], "error": f"object {object_name} not found"}
            
        # Clone initial state for prediction
        # We use current physics parameters from the run
        g = float(run.g)
        m_central = float(run.central_mass)
        dt = float(run.timestep)
        dt64 = np.float64(dt)
        
        # Clone object state and mass
        state = self._clone_object_state(target_obj.state)
        current_mass = float(target_obj.mass)
        
        path = []
        steps = int(lookahead_duration / dt)
        # Sample every 100 steps or at least 100 points total
        sample_rate = max(1, steps // 200)
        
        current_t = float(state.coordinate_time)
        end_t = current_t + lookahead_duration
        
        while current_t < end_t:
            # 1. Physics Kernel (Schwarzschild Geodesic via RK4)
            # RK4 implementation for high-fidelity prediction
            k1_x, k1_y, k1_vx, k1_vy = self._get_derivatives(state.x, state.y, state.vx, state.vy, m_central, g, None, np.float64(current_mass))
            
            k2_x, k2_y, k2_vx, k2_vy = self._get_derivatives(
                state.x + 0.5 * k1_x * dt64, state.y + 0.5 * k1_y * dt64,
                state.vx + 0.5 * k1_vx * dt64, state.vy + 0.5 * k1_vy * dt64,
                m_central, g, None, np.float64(current_mass)
            )
            
            k3_x, k3_y, k3_vx, k3_vy = self._get_derivatives(
                state.x + 0.5 * k2_x * dt64, state.y + 0.5 * k2_y * dt64,
                state.vx + 0.5 * k2_vx * dt64, state.vy + 0.5 * k2_vy * dt64,
                m_central, g, None, np.float64(current_mass)
            )
            
            k4_x, k4_y, k4_vx, k4_vy = self._get_derivatives(
                state.x + k3_x * dt64, state.y + k3_y * dt64,
                state.vx + k3_vx * dt64, state.vy + k3_vy * dt64,
                m_central, g, None, np.float64(current_mass)
            )

            state.x += (dt64 / 6.0) * (k1_x + 2.0 * k2_x + 2.0 * k3_x + k4_x)
            state.y += (dt64 / 6.0) * (k1_y + 2.0 * k2_y + 2.0 * k3_y + k4_y)
            state.vx += (dt64 / 6.0) * (k1_vx + 2.0 * k2_vx + 2.0 * k3_vx + k4_vx)
            state.vy += (dt64 / 6.0) * (k1_vy + 2.0 * k2_vy + 2.0 * k3_vy + k4_vy)
            
            # 2. Apply Burn Plan (Simplified for prediction)
            for burn in burn_plan:
                if burn.start_t <= current_t < (burn.start_t + burn.duration):
                    # We apply thrust directly to velocities for prediction speed
                    ax_thrust = (burn.magnitude * np.cos(burn.angle_rad)) / current_mass
                    ay_thrust = (burn.magnitude * np.sin(burn.angle_rad)) / current_mass
                    state.vx += np.float64(ax_thrust * dt)
                    state.vy += np.float64(ay_thrust * dt)
                    break 

            state.coordinate_time = np.float64(state.coordinate_time + dt64)
            current_t = float(state.coordinate_time)
            
            # 4. Record sample
            if int((current_t - float(target_obj.state.coordinate_time)) / dt) % sample_rate == 0:
                path.append([float(state.x), float(state.y)])

        return {
            "path": path,
            "final_state": state.to_dict(),
            "lookahead_duration": lookahead_duration,
            "steps_simulated": len(path) * sample_rate
        }

    def step_run(self, run_id: str, dt: float | None = None, force: bool = False) -> SimulationRun | None:
        run = self._runs.get(run_id)
        if run is None or (not force and run.state != "running"):
            return None
        dt_value = float(run.timestep if dt is None else dt)
        if not isfinite(dt_value) or dt_value <= 0:
            raise ValueError("dt must be finite and positive")

        dt64 = np.float64(dt_value)
        m_central = float(run.central_mass)
        g = float(run.g)
        a = float(run.angular_momentum)

        for obj in run.objects or []:
            state = obj.state
            others = [o for o in run.objects if o is not obj]
            
            # 1. GR Integration (RK4)
            k1_x, k1_y, k1_vx, k1_vy = self._get_derivatives(state.x, state.y, state.vx, state.vy, m_central, g, a, obj.thrust, obj.mass, others)
            k2_x, k2_y, k2_vx, k2_vy = self._get_derivatives(state.x + 0.5*k1_x*dt64, state.y + 0.5*k1_y*dt64, state.vx + 0.5*k1_vx*dt64, state.vy + 0.5*k1_vy*dt64, m_central, g, a, obj.thrust, obj.mass, others)
            k3_x, k3_y, k3_vx, k3_vy = self._get_derivatives(state.x + 0.5*k2_x*dt64, state.y + 0.5*k2_y*dt64, state.vx + 0.5*k2_vx*dt64, state.vy + 0.5*k2_vy*dt64, m_central, g, a, obj.thrust, obj.mass, others)
            k4_x, k4_y, k4_vx, k4_vy = self._get_derivatives(state.x + k3_x*dt64, state.y + k3_y*dt64, state.vx + k3_vx*dt64, state.vy + k3_vy*dt64, m_central, g, a, obj.thrust, obj.mass, others)

            state.x += (dt64 / 6.0) * (k1_x + 2.0 * k2_x + 2.0 * k3_x + k4_x)
            state.y += (dt64 / 6.0) * (k1_y + 2.0 * k2_y + 2.0 * k3_y + k4_y)
            state.vx += (dt64 / 6.0) * (k1_vx + 2.0 * k2_vx + 2.0 * k3_vx + k4_vx)
            state.vy += (dt64 / 6.0) * (k1_vy + 2.0 * k2_vy + 2.0 * k3_vy + k4_vy)

            # 2. Newtonian Integration (Classic RK4 for the 'Ghost' orbit)
            nk1_x, nk1_y, nk1_vx, nk1_vy = self._get_newtonian_derivatives(state.nx, state.ny, state.nvx, state.nvy, m_central, g, obj.thrust, obj.mass)
            nk2_x, nk2_y, nk2_vx, nk2_vy = self._get_newtonian_derivatives(state.nx + 0.5*nk1_x*dt64, state.ny + 0.5*nk1_y*dt64, state.nvx + 0.5*nk1_vx*dt64, state.nvy + 0.5*nk1_vy*dt64, m_central, g, obj.thrust, obj.mass)
            nk3_x, nk3_y, nk3_vx, nk3_vy = self._get_newtonian_derivatives(state.nx + 0.5*nk2_x*dt64, state.ny + 0.5*nk2_y*dt64, state.nvx + 0.5*nk2_vx*dt64, state.nvy + 0.5*nk2_vy*dt64, m_central, g, obj.thrust, obj.mass)
            nk4_x, nk4_y, nk4_vx, nk4_vy = self._get_newtonian_derivatives(state.nx + nk3_x*dt64, state.ny + nk3_y*dt64, state.nvx + nk3_vx*dt64, state.nvy + nk3_vy*dt64, m_central, g, obj.thrust, obj.mass)

            state.nx += (dt64 / 6.0) * (nk1_x + 2.0 * nk2_x + 2.0 * nk3_x + nk4_x)
            state.ny += (dt64 / 6.0) * (nk1_y + 2.0 * nk2_y + 2.0 * nk3_y + nk4_y)
            state.nvx += (dt64 / 6.0) * (nk1_vx + 2.0 * nk2_vx + 2.0 * nk3_vx + nk4_vx)
            state.nvy += (dt64 / 6.0) * (nk1_vy + 2.0 * nk2_vy + 2.0 * nk3_vy + nk4_vy)
            
            state.coordinate_time = np.float64(state.coordinate_time + dt64)
            
            # Proper time dilation calculation (Schwarzschild or Kerr metric)
            r_final = np.sqrt(state.x**2 + state.y**2)
            if a == 0:
                metric = schwarzschild_metric(central_mass=m_central, g=g, r=float(r_final))
            else:
                metric = kerr_metric(central_mass=m_central, g=g, r=float(r_final), a=a)
                
            c2 = np.float64(metric["c"] * metric["c"])
            speed_sq = np.float64(state.vx * state.vx + state.vy * state.vy)
            
            # For Kerr, proper time involves g_tt and g_tphi
            phi_dot = (state.x * state.vy - state.y * state.vx) / (r_final * r_final)
            lapse = -metric["g_tt"] - (speed_sq / c2)
            if "g_tphi" in metric:
                lapse -= 2.0 * metric["g_tphi"] * phi_dot / metric["c"]
                
            dilation = np.float64(np.sqrt(max(1e-12, lapse)))
            state.proper_time = np.float64(state.proper_time + (dt64 * dilation))

            # Mass loss (if configured)
            if obj.thrust and obj.thrust.is_active and obj.thrust.mass_loss_rate > 0:
                dm = np.float64(obj.thrust.mass_loss_rate * dt64)
                obj.mass = np.float64(max(1e-3, obj.mass - dm))

            # Record telemetry history
            if run.telemetry_history is None:
                run.telemetry_history = {}
            if obj.name not in run.telemetry_history:
                run.telemetry_history[obj.name] = collections.deque(maxlen=50000)
            
            history = run.telemetry_history[obj.name]
            history.append({       
                "t": float(state.coordinate_time),
                "x": float(state.x),
                "y": float(state.y),
                "vx": float(state.vx),
                "vy": float(state.vy),
                "r": float(r_final),     
                "proper_time": float(state.proper_time),
                "coordinate_time": float(state.coordinate_time),
                "proper_time_drift": float(state.coordinate_time - state.proper_time)
            })
        if run.objects:
            run.object_state = run.objects[0].state
        return run

    def pause_run(self, run_id: str) -> SimulationRun | None:
        run = self._runs.get(run_id)
        if run:
            run.state = "paused"
        return run

    def resume_run(self, run_id: str) -> SimulationRun | None:
        run = self._runs.get(run_id)
        if run:
            run.state = "running"
        return run

    def reset_run(self, run_id: str) -> SimulationRun | None:
        run = self._runs.get(run_id)
        if run:
            run.state = "idle"
            run.g = run.baseline_g
            run.central_mass = run.baseline_central_mass
            run.timestep = np.float64(run.baseline_timestep)
            run.telemetry_history = {}
            if run.baseline_objects is not None:
                run.objects = [self._clone_sim_object(obj) for obj in run.baseline_objects]
                run.object_state = self._clone_object_state(run.objects[0].state)
        return run

    def run_validation_suite(self, run_id: str) -> list[dict]:
        run = self._runs.get(run_id)
        if not run or "mercury" not in run.telemetry_history:
            return []

        # Take a snapshot to prevent race conditions during iteration
        history = list(run.telemetry_history["mercury"])
        if len(history) < 100:
            return []

        # 1. Identify perihelion points (local minima of r)
        radii = [h["r"] for h in history]
        perihelia_indices = []
        # Use a 5-point check for stability against numerical noise
        for i in range(2, len(radii) - 2):
            if radii[i] < radii[i-1] and radii[i] < radii[i-2] and \
               radii[i] < radii[i+1] and radii[i] < radii[i+2]:
                perihelia_indices.append(i)

        results = []
        
        # 2. Calculate precession if we have at least 2 orbits
        if len(perihelia_indices) >= 2:
            angles = [np.arctan2(history[i]["y"], history[i]["x"]) for i in perihelia_indices]
            # Normalize angles to [0, 2pi]
            angles = [(a + 2*np.pi) % (2*np.pi) for a in angles]
            
            # Calculate deltas (precession per rev)
            deltas = []
            for i in range(1, len(angles)):
                diff = angles[i] - angles[i-1]
                # Account for wrap-around
                if diff < -np.pi: diff += 2*np.pi
                if diff > np.pi: diff -= 2*np.pi
                deltas.append(abs(diff))
            
            avg_precession = float(np.mean(deltas)) if deltas else 0.0
            
            # Use semi-major axis from Mercury catalog if possible, 
            # otherwise estimate from min/max r in history
            r_max = max(radii)
            r_min = min(radii)
            denom = r_max + r_min
            
            if denom > 0:
                a_est = denom / 2.0
                e_est = (r_max - r_min) / denom
                
                bench_res = run_mercury_precession_benchmark(
                    actual_precession_rad_per_rev=avg_precession,
                    g=run.g,
                    m=run.central_mass,
                    a=a_est,
                    e=e_est
                )
                results.append(bench_res)

        # 3. Circularity check (if applicable, though Mercury is eccentric)
        # For now, just report the radius stability as a secondary metric
        stab_res = validate_orbit_circularity(radii, expected_radius=history[0]["r"])
        results.append(stab_res)

        return results

    async def subscribe(self, run_id: str) -> asyncio.Queue:
        if run_id not in self._queues:
            self._queues[run_id] = []
        queue = asyncio.Queue(maxsize=100)
        self._queues[run_id].append(queue)
        return queue

    def unsubscribe(self, run_id: str, queue: asyncio.Queue) -> None:
        if run_id in self._queues:
            try:
                self._queues[run_id].remove(queue)
                if not self._queues[run_id]:
                    del self._queues[run_id]
            except ValueError:
                pass

    async def run_step_and_broadcast(self) -> None:
        active_ids = [rid for rid, run in self._runs.items() if run.state == "running"]
        for rid in active_ids:
            self.step_run(rid)
            await self.broadcast_telemetry(rid)

    async def broadcast_telemetry(self, run_id: str) -> None:
        run = self._runs.get(run_id)
        if not run or run_id not in self._queues:
            return
        
        telemetry = self.snapshot_run(run_id)
        if not telemetry:
            return

        # Scientific constants for validation
        c = 299792458.0
        rs = (2.0 * run.g * run.central_mass) / (c**2)

        # Enhance telemetry with validation signals for every object
        for obj_data in telemetry.get("objects", []):
            st = obj_data["state"]
            obj_data["validation"] = validate_object_state(st["x"], st["y"], st["vx"], st["vy"], rs)

        for queue in self._queues[run_id]:
            try:
                if queue.full():
                    queue.get_nowait()
                queue.put_nowait(telemetry)
            except Exception:
                pass
