from fastapi import APIRouter
from datetime import date


router = APIRouter()


# Mock simples em memória
LOCATIONS = [
{"id": 1, "name": "Centro A", "address": "Rua 1"},
]
COURTS = [
{"id": 1, "location_id": 1, "name": "Quadra 1", "sport": "futebol"},
]
SLOTS = [
{"id": 1, "court_id": 1, "date": str(date.today()), "start_time": "10:00", "end_time": "11:00", "status": "AVAILABLE"},
]

@router.get("/locations")
async def list_locations():
    return LOCATIONS


@router.get("/courts")
async def list_courts(location_id: int | None = None):
    if location_id:
        return [c for c in COURTS if c["location_id"] == location_id]
    return COURTS


@router.get("/slots")
async def list_slots(court_id: int, date: str):
    return [s for s in SLOTS if s["court_id"] == court_id and s["date"] == date]