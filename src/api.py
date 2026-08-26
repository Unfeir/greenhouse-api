"""The HTTP surface.

The router is created here, in the same file as its routes, because the deriver
resolves a route's prefix from the router declared in that module and refuses a
route whose prefix it cannot see.

``GET /sensors/{sensor_id}/stats`` behaviour:

- An unknown ``sensor_id`` is a 404, matching ``/sensors/{sensor_id}/readings``:
  the resource itself does not exist.
- A known sensor with zero readings in the requested window (e.g. ``limit=0``)
  is a 200 with ``n_readings`` 0 and the temperature figures all ``"0.0"``: the
  sensor exists, it simply has nothing to summarise yet. This is deliberately
  distinct from the 404 case, since an empty aggregate is not a missing sensor.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from fastapi import APIRouter, HTTPException

from src.models import ReadingPage, Sensor, SensorStats
from src.store import SENSORS, readings_for

router = APIRouter(prefix="/api/v1")

_ONE_DP = Decimal("0.1")


def _format_celsius(value: Decimal) -> str:
    """Render a Decimal as a one-decimal-place string, rounded half-up."""
    return str(value.quantize(_ONE_DP, rounding=ROUND_HALF_UP))


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
def sensor_stats(sensor_id: str, limit: int = 24) -> SensorStats:
    """Mean, low and high temperature over one sensor's window of readings.

    See the module docstring for the zero-readings and unknown-sensor cases.
    """
    if not any(sensor.id == sensor_id for sensor in SENSORS):
        raise HTTPException(status_code=404, detail=f"no sensor {sensor_id}")

    readings = readings_for(sensor_id, count=limit)
    if not readings:
        zero = _format_celsius(Decimal(0))
        return SensorStats(
            sensor_id=sensor_id,
            mean_celsius=zero,
            low_celsius=zero,
            high_celsius=zero,
            n_readings=0,
        )

    temperatures = [Decimal(str(reading.celsius)) for reading in readings]
    mean = sum(temperatures, Decimal(0)) / Decimal(len(temperatures))
    return SensorStats(
        sensor_id=sensor_id,
        mean_celsius=_format_celsius(mean),
        low_celsius=_format_celsius(min(temperatures)),
        high_celsius=_format_celsius(max(temperatures)),
        n_readings=len(temperatures),
    )
