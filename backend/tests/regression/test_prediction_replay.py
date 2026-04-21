import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_prediction_matches_actual_execution():
    with TestClient(app) as client:
        # 1. Start a run
        resp = client.post("/runs", json={
            "scenario_id": "replay-test",
            "seed": 123,
            "g": 1.0,
            "central_mass": 1000.0
        })
        run_id = resp.json()["data"]["run_id"]
        
        # 2. Add a rocket
        client.post(f"/runs/{run_id}/objects", json={
            "name": "rocket",
            "mass": 10.0,
            "x": 20.0,
            "y": 0.0,
            "vx": 0.0,
            "vy": 5.0
        })
        
        # Pause to have perfect control
        client.post(f"/runs/{run_id}/pause")
        
        # 3. Define a burn plan
        burn_plan = [
            {"start_t": 1.0, "duration": 2.0, "magnitude": 50.0, "angle_rad": 0.5}
        ]
        
        # 4. Get PREDICTION for 10 seconds
        pred_resp = client.post(f"/runs/{run_id}/predict", json={
            "object_name": "rocket",
            "burns": burn_plan,
            "lookahead_duration": 10.0
        })
        assert pred_resp.status_code == 200, f"Prediction failed: {pred_resp.json()}"
        prediction = pred_resp.json()["data"]
        predicted_final = prediction["final_state"]
        
        # 5. Now ACTUALLY EXECUTE the plan in the real simulation
        # Manual steps for perfect alignment
        for _ in range(10): # 10 seconds at 1.0s dt
            snap = client.get(f"/runs/{run_id}").json()["data"]
            # Find rocket index
            rocket = next(obj for obj in snap["objects"] if obj["name"] == "rocket")
            t = rocket["state"]["coordinate_time"]
            
            # Apply burn if in window
            if 1.0 <= t < 3.0:
                client.post(f"/runs/{run_id}/objects/rocket/thrust", json={
                    "is_active": True,
                    "magnitude": 50.0,
                    "angle_rad": 0.5
                })
            else:
                client.post(f"/runs/{run_id}/objects/rocket/thrust", json={
                    "is_active": False,
                    "magnitude": 0.0,
                    "angle_rad": 0.0
                })
            
            client.post(f"/runs/{run_id}/step")
            
        # 6. Compare actual final state with predicted final state
        final_snap = client.get(f"/runs/{run_id}").json()["data"]
        actual_rocket = next(obj for obj in final_snap["objects"] if obj["name"] == "rocket")
        actual_final = actual_rocket["state"]
        
        # High precision check (0.01% tolerance allowed in NFR4, but here should be bit-identical-ish)
        assert actual_final["x"] == pytest.approx(predicted_final["x"])
        assert actual_final["y"] == pytest.approx(predicted_final["y"])
        assert actual_final["vx"] == pytest.approx(predicted_final["vx"])
        assert actual_final["vy"] == pytest.approx(predicted_final["vy"])
