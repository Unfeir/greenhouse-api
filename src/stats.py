"""Per-sensor temperature statistics.

Its own `APIRouter`, in this module, per house rule: a route whose router lives
elsewhere cannot have its prefix resolved. Aggregates are computed in `Decimal`
and serialised as one-decimal strings, never floats, per house rule.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.store import SENSORS, readings_for

router = APIRouter(prefix="/api/v1")

_ONE_DP = Decimal("0.1")


class SensorStats(BaseModel):
    """Temperature aggregates for a single sensor's readings."""

    sensor_id: str
    mean_celsius: str | None
    low_celsius: str | None
    high_celsius: str | None
    n_readings: int


def _one_decimal(value: Decimal) -> str:
    return str(value.quantize(_ONE_DP, rounding=ROUND_HALF_UP))


@router.get("/sensors/{sensor_id}/stats")
def sensor_stats(sensor_id: str, limit: int = 24) -> SensorStats:
    """Mean, low and high temperature across one sensor's readings."""
    if not any(sensor.id == sensor_id for sensor in SENSORS):
        raise HTTPException(status_code=404, detail=f"no sensor {sensor_id}")

    readings = readings_for(sensor_id, count=limit)
    if not readings:
        return SensorStats(
            sensor_id=sensor_id,
            mean_celsius=None,
            low_celsius=None,
            high_celsius=None,
            n_readings=0,
        )

    temperatures = [Decimal(str(reading.celsius)) for reading in readings]
    mean = sum(temperatures, Decimal(0)) / Decimal(len(temperatures))

    return SensorStats(
        sensor_id=sensor_id,
        mean_celsius=_one_decimal(mean),
        low_celsius=_one_decimal(min(temperatures)),
        high_celsius=_one_decimal(max(temperatures)),
        n_readings=len(temperatures),
    )
