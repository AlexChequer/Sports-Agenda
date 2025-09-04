from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import itertools


router = APIRouter()


LOCKS: dict[int, dict] = {}
_lock_seq = itertools.count(1)


@router.post("/locks")
async def create_lock(court_id: int, slot_id: int, booking_id: int, ttl_seconds: int = 300):
    lock_id = next(_lock_seq)
    expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
    LOCKS[lock_id] = {
        "court_id": court_id,
        "slot_id": slot_id,
        "booking_id": booking_id,
        "expires_at": expires_at.isoformat(),
    }
    return {"lock_id": lock_id, "expires_at": expires_at.isoformat()}


@router.post("/locks/release")
async def release_lock(lock_id: int):
    if lock_id in LOCKS:
        del LOCKS[lock_id]
        return {"released": True}
    raise HTTPException(404, "lock not found")


@router.post("/mark-booked")
async def mark_booked(court_id: int, slot_id: int, booking_id: int):
    # Em uma app real, você marcaria o slot como BOOKED no banco.
    return {"ok": True}


@router.post("/mark-released")
async def mark_released(court_id: int, slot_id: int, booking_id: int):
    return {"ok": True}