import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.domain.simulation.engine import SimulationEngine

client = TestClient(app)

def test_save_load_determinism():
    with TestClient(app) as client:
        # 1. Start a run
        response = client.post("/runs", json={
            "scenario_id": "determinism-test",
            "seed": 42,
            "g": 6.67430e-11,
            "central_mass": 1.98847e30
        })
        assert response.status_code == 200
        run_data = response.json()["data"]
        run_id = run_data["run_id"]

        # PAUSE the run immediately to prevent the background loop from interfering
        client.post(f"/runs/{run_id}/pause")

        # 2. Step the simulation 10 times
        for _ in range(10):
            client.post(f"/runs/{run_id}/step")
        
        # Capture state after 10 steps
        mid_state_resp = client.post(f"/runs/{run_id}/step") # 11th step
        mid_state = mid_state_resp.json()["data"]

        # 3. Save the state
        save_response = client.get(f"/runs/{run_id}/save")
        assert save_response.status_code == 200
        saved_state = save_response.json()["data"]

        # 4. Load the state into a NEW run
        load_response = client.post("/runs/load", json=saved_state)
        assert load_response.status_code == 200
        loaded_run_data = load_response.json()["data"]
        new_run_id = loaded_run_data["run_id"]

        assert new_run_id != run_id
        
        # 5. Verify initial loaded state matches original mid_state
        orig_objects = mid_state["objects"]
        loaded_objects = loaded_run_data["objects"]
        
        assert len(orig_objects) == len(loaded_objects)
        for i in range(len(orig_objects)):
            assert orig_objects[i]["state"] == loaded_objects[i]["state"]

        # 6. Step BOTH runs 50 more times and compare
        for _ in range(50):
            client.post(f"/runs/{run_id}/step")
            client.post(f"/runs/{new_run_id}/step")
        
        final_orig = client.post(f"/runs/{run_id}/step").json()["data"]
        final_loaded = client.post(f"/runs/{new_run_id}/step").json()["data"]
        
        for i in range(len(final_orig["objects"])):
            # Bit-identical check
            assert final_orig["objects"][i]["state"] == final_loaded["objects"][i]["state"]
