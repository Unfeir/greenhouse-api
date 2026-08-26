"""The shapes this service speaks in.

Every one of these is a `contract` as far as the context store is concerned, and
the ones an endpoint references are published to the **project** scope — which is
the only way the web client's repository can ever be told about them.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class Sensor(BaseModel):
    """One physical probe in a greenhouse."""

    id: str
    label: str
    zone: str


class Reading(BaseModel):
    """A single measurement, exactly as the probe reported it."""

    sensor_id: str
    taken_at: datetime
    celsius: float
    humidity: float


class ReadingPage(BaseModel):
    """A window of readings, with the cursor to ask for the next one."""

    sensor_id: str
    readings: list[Reading]
    next_cursor: str | None


class SensorStats(BaseModel):
    """Temperature summary statistics for one sensor over a window of readings."""

    sensor_id: str
    mean_celsius: str
    low_celsius: str
    high_celsius: str
    n_readings: int
