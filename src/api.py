"""The HTTP surface.

The router is created here, in the same file as its routes, because the deriver
resolves a route's prefix from the router declared in that module and refuses a
route whose prefix it cannot see.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.models import ReadingPage, Sensor
from src.store import SENSORS, readings_for

router = APIRouter(prefix="/api/v1")


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
