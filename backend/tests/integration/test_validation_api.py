from fastapi.testclient import TestClient
from app.main import app

def test_validate_insufficient_data() -> None:
    with TestClient(app) as client:
        # Create a run
        create_res = client.post("/runs", json={"scenario_id": "test", "seed": 123})
        run_id = create_res.json()["data"]["run_id"]
        
        # Immediate validation should return insufficient data
        validate_res = client.post(f"/runs/{run_id}/validate")
        assert validate_res.status_code == 200
        body = validate_res.json()
        assert body["data"]["status"] == "insufficient_data"
        assert body["data"]["results"] == []

def test_validate_with_mocked_history() -> None:
    # We can't easily run 100+ physics steps in a fast integration test 
    # unless we use a very large timestep or mock the engine's history.
    # For this test, we'll verify the endpoint logic.
    with TestClient(app) as client:
        create_res = client.post("/runs", json={"scenario_id": "test", "seed": 123})
        run_id = create_res.json()["data"]["run_id"]
        
        # Access the engine directly to inject mock history
        engine = app.state.sim_engine
        run = engine._runs[run_id]
        
        # Inject mock history for mercury
        # Need enough points for perihelion detection (local minima)
        run.telemetry_history = {
            "mercury": [
                {"x": 1.0e10, "y": 0.0, "r": 1.0e10 + (i-50)**2, "t": float(i)} 
                for i in range(110)
            ]
        }
        # This history has a clear minimum at i=50
        
        # We need at least 2 perihelia for precession calculation.
        # Let's add another dip.
        run.telemetry_history["mercury"] += [
            {"x": 1.0e10, "y": 0.0, "r": 1.0e10 + (i-150)**2, "t": float(i)}
            for i in range(110, 210)
        ]
        
        validate_res = client.post(f"/runs/{run_id}/validate")
        assert validate_res.status_code == 200
        body = validate_res.json()
        
        # Even with mock data, it should now attempt validation
        assert body["data"]["status"] == "complete"
        assert len(body["data"]["results"]) > 0
        
        # Check structure of first result
        res = body["data"]["results"][0]
        assert "test_name" in res
        assert "is_passed" in res
        assert "actual" in res
        assert "expected" in res
        assert "deviation" in res

def test_validate_missing_run() -> None:
    with TestClient(app) as client:
        validate_res = client.post("/runs/missing-id/validate")
        assert validate_res.status_code == 404
        assert validate_res.json()["error"]["code"] == "RUN_NOT_FOUND"
