"""An in-memory stand-in for the database.

Deliberately trivial. What this repository exists to exercise is whether an
agent, told about a contract it cannot see, writes code that matches it — not
whether anybody can wire up Postgres.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from src.models import Reading, Sensor

SENSORS: list[Sensor] = [
    Sensor(id="s-1", label="North bench", zone="propagation"),
    Sensor(id="s-2", label="South bench", zone="propagation"),
    Sensor(id="s-3", label="Roof vent", zone="canopy"),
]

_START = datetime(2026, 8, 1, tzinfo=UTC)

_STORED_READING_COUNTS: dict[str, int] = {"s-1": 24, "s-2": 1, "s-3": 0}


def readings_for(sensor_id: str, *, count: int = 24) -> list[Reading]:
    """A deterministic series, so tests can assert on numbers."""
    return [
        Reading(
            sensor_id=sensor_id,
            taken_at=_START + timedelta(hours=hour),
            celsius=18.0 + (hour % 6),
            humidity=55.0 + (hour % 4),
        )
        for hour in range(count)
    ]


def all_readings_for(sensor_id: str) -> list[Reading]:
    """Every reading stored for a sensor, not just a requested page of them."""
    return readings_for(sensor_id, count=_STORED_READING_COUNTS.get(sensor_id, 0))
