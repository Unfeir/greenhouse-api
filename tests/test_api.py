"""What the service promises, asserted rather than described.

The suite an agent must keep green. Small on purpose: the interesting failure in
this scenario is a wrong *contract*, and a large suite would bury it under
unrelated red.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

import src.api as api_module
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


def test_stats_summarise_a_sensors_full_reading_history() -> None:
    body = client.get("/api/v1/sensors/s-1/stats").json()

    assert body == {
        "sensor_id": "s-1",
        "mean_celsius": "20.5",
        "low_celsius": "18.0",
        "high_celsius": "23.0",
        "n_readings": 24,
    }


def test_stats_for_a_sensor_with_no_readings_are_all_null() -> None:
    original = api_module.readings_for
    api_module.readings_for = lambda sensor_id, count=24: []
    try:
        body = client.get("/api/v1/sensors/s-2/stats").json()
    finally:
        api_module.readings_for = original

    assert body == {
        "sensor_id": "s-2",
        "mean_celsius": None,
        "low_celsius": None,
        "high_celsius": None,
        "n_readings": 0,
    }


def test_stats_for_an_unknown_sensor_is_a_404() -> None:
    assert client.get("/api/v1/sensors/nope/stats").status_code == 404
