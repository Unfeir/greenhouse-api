"""The HTTP surface.

The router is created here, in the same file as its routes, because the deriver
resolves a route's prefix from the router declared in that module and refuses a
route whose prefix it cannot see.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from fastapi import APIRouter, HTTPException

from src.models import ReadingPage, Sensor, SensorStats
from src.store import SENSORS, readings_for

router = APIRouter(prefix="/api/v1")


def _one_decimal(value: Decimal) -> str:
    """Half-up rounding to one decimal place, as a string."""
    return str(value.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


@router.get("/sensors")
def list_sensors() -> list[Sensor]:
    """Every sensor this greenhouse has."""
    return SENSORS


@router.get("/sensors/{sensor_id}/readings")
def sensor_readings(sensor_id: str, limit: int = 24) -> ReadingPage:
    """A window of one sensor's readings, newest first."""
    if not any(sensor.id == sensor_id for sensor in SENSORS):
        raise HTTPException(status_code=404, detail=f"no sensor {sensor_id}")
    readings = readings_for(sensor_id, count=limit)
    return ReadingPage(sensor_id=sensor_id, readings=readings, next_cursor=None)


@router.get("/sensors/{sensor_id}/stats")
def sensor_stats(sensor_id: str) -> SensorStats:
    """Mean, low and high temperature over one sensor's stored readings."""
    if not any(sensor.id == sensor_id for sensor in SENSORS):
        raise HTTPException(status_code=404, detail=f"no sensor {sensor_id}")

    readings = readings_for(sensor_id)
    if not readings:
        return SensorStats(
            sensor_id=sensor_id,
            mean_celsius=None,
            low_celsius=None,
            high_celsius=None,
            n_readings=0,
        )

    temperatures = [Decimal(str(reading.celsius)) for reading in readings]
    mean = sum(temperatures) / len(temperatures)
    return SensorStats(
        sensor_id=sensor_id,
        mean_celsius=_one_decimal(mean),
        low_celsius=_one_decimal(min(temperatures)),
        high_celsius=_one_decimal(max(temperatures)),
        n_readings=len(readings),
    )
