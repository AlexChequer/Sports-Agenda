import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import FastAPI

# importa os três routers
from app.api.routes.health import router as health_router
from app.api.routes.internal import router as internal_router
from app.api.routes.public import router as public_router

# cria um app só para os testes
app = FastAPI()
app.include_router(health_router)
app.include_router(internal_router)
app.include_router(public_router) 


client = TestClient(app)

# ---------- TESTES SIMPLES ----------
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"} 

def test_create_lock():
    response = client.post("/locks", params={"court_id": 1, "slot_id": 2, "booking_id": 3})
    assert response.status_code == 200
    data = response.json()
    assert data["lock_id"] == "1-2-3"

def test_release_lock():
    response = client.post("/locks/release", params={"lock_id": "1-2-3"})
    assert response.status_code == 200
    assert response.json() == {"released": True}

# ---------- MOCKANDO DB ----------
@patch("app.slots.get_conn")
def test_mark_booked(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.return_value.cursor.return_value = mock_cursor

    response = client.post("/mark-booked", params={"court_id": 1, "slot_id": 2, "booking_id": 3})
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    mock_cursor.execute.assert_called_once()

@patch("app.slots.get_conn")
def test_mark_released(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.return_value.cursor.return_value = mock_cursor

    response = client.post("/mark-released", params={"court_id": 1, "slot_id": 2, "booking_id": 3})
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    mock_cursor.execute.assert_called_once()

@patch("app.locations.get_conn")
def test_list_locations(mock_conn):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [(1, "Loc A", "Addr A"), (2, "Loc B", "Addr B")]
    mock_conn.return_value.cursor.return_value = mock_cursor

    response = client.get("/locations")
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "Loc A", "address": "Addr A"},
        {"id": 2, "name": "Loc B", "address": "Addr B"},
    ]

@patch("app.locations.get_conn")
def test_list_courts(mock_conn):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [(1, 10, "Court A", "Tennis")]
    mock_conn.return_value.cursor.return_value = mock_cursor

    response = client.get("/courts", params={"location_id": 10})
    assert response.status_code == 200
    assert response.json() == [{"id": 1, "location_id": 10, "name": "Court A", "sport": "Tennis"}]

@patch("app.slots.get_conn")
def test_list_slots(mock_conn):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        (1, 10, "2025-09-08", "09:00", "10:00", "AVAILABLE")
    ]
    mock_conn.return_value.cursor.return_value = mock_cursor

    response = client.get("/slots", params={"court_id": 10, "date": "2025-09-08"})
    assert response.status_code == 200
    data = response.json()
    assert data[0]["status"] == "AVAILABLE"
    assert data[0]["court_id"] == 10
