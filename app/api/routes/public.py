import os
import psycopg2
from fastapi import APIRouter, HTTPException, Body, Depends
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
from app.core.auth import verify_token

load_dotenv()
router = APIRouter()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

@router.get("/locations")
async def list_locations(payload=Depends(verify_token)):
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
async def list_courts(location_id: int | None = None, payload=Depends(verify_token)):
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
async def list_slots(court_id: int, date: str, payload=Depends(verify_token)):
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

class CourtCreate(BaseModel):
    name: str
    sport: str

class LocationWithCourtsCreate(BaseModel):
    name: str
    address: str
    courts: List[CourtCreate]

@router.post("/locations-with-courts")
async def create_location_with_courts(data: LocationWithCourtsCreate, payload=Depends(verify_token)):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO locations (name, address) VALUES (%s, %s) RETURNING id",
            (data.name, data.address)
        )
        location_id = cur.fetchone()[0]
        for court in data.courts:
            cur.execute(
                "INSERT INTO courts (location_id, name, sport) VALUES (%s, %s, %s)",
                (location_id, court.name, court.sport)
            )
        conn.commit()
        cur.close()
        conn.close()
        return {
            "location_id": location_id,
            "message": "Localização e quadras criadas com sucesso.",
            "courts_created": len(data.courts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class CourtOnlyCreate(BaseModel):
    location_id: int
    name: str
    sport: str

@router.post("/courts")
async def create_court(court: CourtOnlyCreate = Body(...), payload=Depends(verify_token)):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO courts (location_id, name, sport) VALUES (%s, %s, %s) RETURNING id",
            (court.location_id, court.name, court.sport)
        )
        court_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return {"court_id": court_id, "message": "Quadra criada com sucesso."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
