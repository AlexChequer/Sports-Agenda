import os
import psycopg2
from fastapi import APIRouter, HTTPException

router = APIRouter()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

@router.post("/locks")
async def create_lock(court_id: int, slot_id: int, booking_id: int, ttl_seconds: int = 300):
    # aqui só devolve lock fake, se quiser pode criar tabela locks depois
    return {"lock_id": f"{court_id}-{slot_id}-{booking_id}", "expires_at": "in+ttl_seconds"}

@router.post("/locks/release")
async def release_lock(lock_id: str):
    return {"released": True}

@router.post("/mark-booked")
async def mark_booked(court_id: int, slot_id: int, booking_id: int):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE slots SET status='BOOKED' WHERE id=%s AND court_id=%s", (slot_id, court_id))
        conn.commit()
        cur.close()
        conn.close()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mark-released")
async def mark_released(court_id: int, slot_id: int, booking_id: int):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE slots SET status='AVAILABLE' WHERE id=%s AND court_id=%s", (slot_id, court_id))
        conn.commit()
        cur.close()
        conn.close()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
