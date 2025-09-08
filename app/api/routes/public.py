import os
import psycopg2
from fastapi import APIRouter, HTTPException

router = APIRouter()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

@router.get("/locations")
async def list_locations():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, name, address FROM locations")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [{"id": r[0], "name": r[1], "address": r[2]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/courts")
async def list_courts(location_id: int | None = None):
    try:
        conn = get_conn()
        cur = conn.cursor()
        if location_id:
            cur.execute("SELECT id, location_id, name, sport FROM courts WHERE location_id=%s", (location_id,))
        else:
            cur.execute("SELECT id, location_id, name, sport FROM courts")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [{"id": r[0], "location_id": r[1], "name": r[2], "sport": r[3]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/slots")
async def list_slots(court_id: int, date: str):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, court_id, date, start_time, end_time, status FROM slots WHERE court_id=%s AND date=%s",
            (court_id, date)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [
            {
                "id": r[0],
                "court_id": r[1],
                "date": str(r[2]),
                "start_time": str(r[3]),
                "end_time": str(r[4]),
                "status": r[5],
            }
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
