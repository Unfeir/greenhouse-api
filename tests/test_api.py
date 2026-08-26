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


def test_stats_returns_the_documented_fields_as_one_decimal_strings() -> None:
    body = client.get("/api/v1/sensors/s-1/stats?limit=16").json()

    assert set(body.keys()) == {
        "sensor_id",
        "mean_celsius",
        "low_celsius",
        "high_celsius",
        "n_readings",
    }
    assert body["sensor_id"] == "s-1"
    assert body["low_celsius"] == "18.0"
    assert body["high_celsius"] == "23.0"
    assert body["n_readings"] == 16


def test_stats_mean_rounds_half_up_at_one_decimal_place() -> None:
    """The 16 deterministic readings for s-1 have an exact mean of 20.25."""
    body = client.get("/api/v1/sensors/s-1/stats?limit=16").json()

    assert body["mean_celsius"] == "20.3"
    for field in ("mean_celsius", "low_celsius", "high_celsius"):
        assert isinstance(body[field], str)
        decimal_places = body[field].split(".")[1]
        assert len(decimal_places) == 1


def test_stats_for_a_sensor_with_zero_readings_is_a_200_with_zeroed_figures() -> None:
    """A known sensor with no readings in the window is not the same as a missing one."""
    body = client.get("/api/v1/sensors/s-1/stats?limit=0").json()

    assert body == {
        "sensor_id": "s-1",
        "mean_celsius": "0.0",
        "low_celsius": "0.0",
        "high_celsius": "0.0",
        "n_readings": 0,
    }


def test_stats_for_an_unknown_sensor_is_a_404() -> None:
    response = client.get("/api/v1/sensors/nope/stats")

    assert response.status_code == 404
    assert response.json() == {"detail": "no sensor nope"}
