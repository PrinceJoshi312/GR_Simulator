import json
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

def test_telemetry_stream_endpoint_exists() -> None:
    with TestClient(app) as client:
        # 1. Create a run
        create_res = client.post("/runs", json={"scenario_id": "default-schwarzschild", "seed": 123})
        assert create_res.status_code == 200
        run_id = create_res.json()["data"]["run_id"]
        
        # 2. Verify the endpoint exists without starting the infinite stream
        # Using a mock for EventSourceResponse to prevent the test from hanging
        with patch("app.api.routers.runs.EventSourceResponse") as mock_sse:
            mock_sse.return_value = {"status_code": 200, "headers": {"content-type": "text/event-stream"}}
            response = client.get(f"/runs/{run_id}/telemetry")
            assert response.status_code == 200
            # If the endpoint exists and logic is correct, it reaches our mock
            assert mock_sse.called
