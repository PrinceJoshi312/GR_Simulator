from fastapi.testclient import TestClient

from app.main import app


def test_run_lifecycle_and_metadata() -> None:
    with TestClient(app) as client:
        create_res = client.post("/runs", json={"scenario_id": "default-schwarzschild", "seed": 123})
        assert create_res.status_code == 200
        create_body = create_res.json()
        assert create_body["error"] is None
        assert create_body["data"]["state"] == "running"
        assert create_body["data"]["seed"] == 123
        assert "engine_version" in create_body["data"]
        assert "app_version" in create_body["data"]
        run_id = create_body["data"]["run_id"]

        pause_res = client.post(f"/runs/{run_id}/pause")
        assert pause_res.status_code == 200
        assert pause_res.json()["data"]["state"] == "paused"
        resume_res = client.post(f"/runs/{run_id}/resume")
        assert resume_res.status_code == 200
        assert resume_res.json()["data"]["state"] == "running"

        reset_res = client.post(f"/runs/{run_id}/reset")
        assert reset_res.status_code == 200
        assert reset_res.json()["data"]["state"] == "idle"


def test_pause_and_reset_missing_run_return_error_envelope() -> None:
    with TestClient(app) as client:
        pause_res = client.post("/runs/missing-id/pause")
        assert pause_res.status_code == 404
        pause_body = pause_res.json()
        assert pause_body["data"] is None
        assert pause_body["error"]["code"] == "RUN_NOT_FOUND"
        assert "request_id" in pause_body["meta"]

        reset_res = client.post("/runs/missing-id/reset")
        assert reset_res.status_code == 404
        reset_body = reset_res.json()
        assert reset_body["data"] is None
        assert reset_body["error"]["code"] == "RUN_NOT_FOUND"


def test_catalog_custom_object_and_runtime_params() -> None:
    with TestClient(app) as client:
        create_res = client.post("/runs", json={"scenario_id": "default-schwarzschild", "seed": 7})
        run_id = create_res.json()["data"]["run_id"]

        catalog_res = client.post(f"/runs/{run_id}/objects/catalog/earth")
        assert catalog_res.status_code == 200
        assert len(catalog_res.json()["data"]["objects"]) >= 2

        custom_res = client.post(
            f"/runs/{run_id}/objects",
            json={"name": "probe", "mass": 1500.0, "x": 7.0e10, "y": 1.0e8, "vx": 0.0, "vy": 12000.0},
        )
        assert custom_res.status_code == 200
        names = [obj["name"] for obj in custom_res.json()["data"]["objects"]]
        assert "probe" in names

        params_res = client.post(
            f"/runs/{run_id}/params",
            json={"timestep": 5.0, "g": 6.6743e-11, "central_mass": 1.95e30},
        )
        assert params_res.status_code == 200
        assert params_res.json()["data"]["timestep"] == 5.0


def test_invalid_create_and_non_running_control_updates() -> None:
    with TestClient(app) as client:
        invalid_create = client.post("/runs", json={"scenario_id": "default-schwarzschild", "seed": 1, "g": -1.0, "central_mass": 1.0})
        assert invalid_create.status_code == 400
        assert invalid_create.json()["error"]["code"] == "INVALID_RUN_PARAMS"

        create_res = client.post("/runs", json={"scenario_id": "default-schwarzschild", "seed": 5})
        run_id = create_res.json()["data"]["run_id"]
        client.post(f"/runs/{run_id}/pause")
        paused_update = client.post(f"/runs/{run_id}/params", json={"timestep": 2.0, "g": 6.6743e-11, "central_mass": 1.9e30})
        assert paused_update.status_code == 404
