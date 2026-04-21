import io
import csv
import json
import datetime
from typing import Any, Generator, Iterable
import numpy as np

def generate_metadata(run_id: str, g: float, central_mass: float, seed: int, engine_version: str) -> dict[str, Any]:
    """Generates a standard metadata dictionary for exports."""
    c = 299792458.0
    rs = (2.0 * g * central_mass) / (c**2)
    
    return {
        "run_id": run_id,
        "g": float(g),
        "central_mass": float(central_mass),
        "rs": float(rs),
        "c": float(c),
        "seed": int(seed),
        "engine_version": engine_version,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

def generate_csv_export(history: Iterable[dict], metadata: dict[str, Any]) -> Generator[str, None, None]:
    """Generates a CSV export with metadata comments as a stream of strings."""
    # Write metadata as comments
    for key, value in metadata.items():
        yield f"# {key}: {value}\n"
    
    # Write CSV header
    columns = ["t", "x", "y", "vx", "vy", "r", "proper_time", "coordinate_time"]
    yield ",".join(columns) + "\n"
    
    # Write rows
    for entry in history:
        row = [str(float(entry.get(col, 0.0))) for col in columns]
        yield ",".join(row) + "\n"

def generate_numpy_export(history: Iterable[dict], metadata: dict[str, Any]) -> io.BytesIO:
    """Generates a compressed NumPy (.npz) export in-memory."""
    columns = ["t", "x", "y", "vx", "vy", "r", "proper_time", "coordinate_time"]
    
    # Convert iterable of dicts to a structured numpy array for efficiency
    dtype = [(col, np.float64) for col in columns]
    
    # Use a generator expression instead of a list of tuples to save memory
    data_gen = (tuple(float(entry.get(col, 0.0)) for col in columns) for entry in history)
    
    # np.fromiter only works for 1D arrays of simple types. 
    # For structured arrays from generators, np.array is more flexible.
    data_array = np.fromiter(data_gen, dtype=dtype)
    
    buffer = io.BytesIO()
    np.savez_compressed(buffer, telemetry=data_array, metadata=metadata)
    buffer.seek(0)
    return buffer
