import io
import numpy as np
from app.domain.validation.exports import generate_metadata, generate_csv_export, generate_numpy_export

def test_csv_export_format():
    history = [
        {"t": 0.0, "x": 1.0, "y": 0.0, "vx": 0.0, "vy": 1.0, "r": 1.0, "proper_time": 0.0, "coordinate_time": 0.0},
        {"t": 1.0, "x": 1.1, "y": 0.1, "vx": 0.1, "vy": 1.1, "r": 1.1, "proper_time": 0.9, "coordinate_time": 1.0},
    ]
    metadata = {
        "run_id": "test-uuid",
        "g": 6.674e-11,
        "central_mass": 1.989e30,
        "rs": 2953.0,
        "c": 299792458.0,
        "seed": 42,
        "engine_version": "0.1.0",
        "timestamp": "2026-04-20T12:00:00Z"
    }
    
    csv_gen = generate_csv_export(history, metadata)
    csv_content = "".join(list(csv_gen))
    
    # Check metadata comments
    assert "# run_id: test-uuid" in csv_content
    assert "# rs: 2953.0" in csv_content
    
    # Check header
    assert "t,x,y,vx,vy,r,proper_time,coordinate_time" in csv_content
    
    # Check data rows
    assert "0.0,1.0,0.0,0.0,1.0,1.0,0.0,0.0" in csv_content
    assert "1.0,1.1,0.1,0.1,1.1,1.1,0.9,1.0" in csv_content

def test_numpy_export_format():
    history = [
        {"t": 0.0, "x": 1.0, "y": 0.0, "vx": 0.0, "vy": 1.0, "r": 1.0, "proper_time": 0.0, "coordinate_time": 0.0},
    ]
    metadata = {"run_id": "test-uuid"}
    
    buffer = generate_numpy_export(history, metadata)
    
    # Load it back
    loaded = np.load(buffer, allow_pickle=True)
    
    assert "telemetry" in loaded
    assert "metadata" in loaded
    
    telemetry = loaded["telemetry"]
    # It's a structured array, so we access by field name
    assert telemetry[0]["x"] == 1.0
    assert telemetry[0]["proper_time"] == 0.0
    
    # metadata is stored as an object array with one item (the dict)
    assert loaded["metadata"].item()["run_id"] == "test-uuid"
