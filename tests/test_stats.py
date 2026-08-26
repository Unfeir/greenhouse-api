"""What the stats endpoint promises, asserted rather than described."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src import stats as stats_module
from src.models import Reading, Sensor

app = FastAPI()
app.include_router(stats_module.router)
client = TestClient(app)


def test_stats_are_computed_in_decimal_with_half_up_rounding(monkeypatch) -> None:
    """A mean of 18.25 is a half-up rounding boundary: it must serialise as 18.3."""
    sensor = Sensor(id="s-test", label="Test bench", zone="propagation")
    monkeypatch.setattr(stats_module, "SENSORS", [sensor])
    readings = [
        Reading(sensor_id="s-test", taken_at=datetime(2026, 8, 1, hour, tzinfo=UTC), celsius=celsius, humidity=50.0)
        for hour, celsius in enumerate([17.0, 18.0, 19.0, 19.0])
    ]
    monkeypatch.setattr(stats_module, "readings_for", lambda sensor_id, *, count=24: readings)

    body = client.get("/api/v1/sensors/s-test/stats").json()

    assert body == {
        "sensor_id": "s-test",
        "mean_celsius": "18.3",
        "low_celsius": "17.0",
        "high_celsius": "19.0",
        "n_readings": 4,
    }


def test_a_sensor_with_no_readings_reports_a_zero_count_and_null_temperatures(monkeypatch) -> None:
    sensor = Sensor(id="s-empty", label="Empty bench", zone="propagation")
    monkeypatch.setattr(stats_module, "SENSORS", [sensor])
    monkeypatch.setattr(stats_module, "readings_for", lambda sensor_id, *, count=24: [])

    response = client.get("/api/v1/sensors/s-empty/stats")
    body = response.json()

    assert response.status_code == 200
    assert body == {
        "sensor_id": "s-empty",
        "mean_celsius": None,
        "low_celsius": None,
        "high_celsius": None,
        "n_readings": 0,
    }


def test_an_unknown_sensor_is_a_404() -> None:
    assert client.get("/api/v1/sensors/nope/stats").status_code == 404
