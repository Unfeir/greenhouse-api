"""What the service promises, asserted rather than described.

The suite an agent must keep green. Small on purpose: the interesting failure in
this scenario is a wrong *contract*, and a large suite would bury it under
unrelated red.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_sensors_are_listed_with_their_zone() -> None:
    body = client.get("/api/v1/sensors").json()

    assert [sensor["id"] for sensor in body] == ["s-1", "s-2", "s-3"]
    assert body[0]["zone"] == "propagation"


def test_readings_come_back_as_a_page() -> None:
    body = client.get("/api/v1/sensors/s-1/readings?limit=3").json()

    assert body["sensor_id"] == "s-1"
    assert len(body["readings"]) == 3
    assert body["next_cursor"] is None


def test_an_unknown_sensor_is_a_404_rather_than_an_empty_page() -> None:
    """An empty page and a missing sensor mean different things to a caller."""
    assert client.get("/api/v1/sensors/nope/readings").status_code == 404
