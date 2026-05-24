import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from domain.models import Airport
from ports.airport_port import AirportPort
from adapters.api_colombia_adapter import ApiColombiaAdapter
from infrastructure.database import SQLiteAirportAdapter

client = TestClient(app)

# ── Pruebas de endpoints ───────────────────────────────────────────────────────

def test_list_airports_returns_200():
    """GET /airports debe retornar 200 y una lista"""
    response = client.get("/airports")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_airport_success():
    """POST /airports debe crear un aeropuerto y retornar 201"""
    payload = {
        "name": "Aeropuerto de Prueba",
        "city": "Ciudad de Prueba",
        "department": "Cundinamarca",
        "iata_code": "TST",
        "latitude": 4.7016,
        "longitude": -74.1469
    }
    response = client.post("/airports", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["iata_code"] == "TST"
    assert "id" in data

def test_create_airport_duplicate_iata():
    """POST /airports con IATA duplicado debe retornar 400"""
    payload = {
        "name": "Aeropuerto Duplicado",
        "city": "Ciudad",
        "department": "Cundinamarca",
        "iata_code": "TST",
        "latitude": 4.7016,
        "longitude": -74.1469
    }
    response = client.post("/airports", json=payload)
    assert response.status_code == 400

def test_get_airport_not_found():
    """GET /airports/{id} con ID inexistente debe retornar 404"""
    response = client.get("/airports/99999")
    assert response.status_code == 404

def test_get_airport_by_iata_not_found():
    """GET /airports/iata/{iata} con IATA inexistente debe retornar 404"""
    response = client.get("/airports/iata/ZZZ")
    assert response.status_code == 404

def test_create_airport_invalid_latitude():
    """POST /airports con latitud invalida debe retornar 422"""
    payload = {
        "name": "Aeropuerto Invalido",
        "city": "Ciudad",
        "department": "Cundinamarca",
        "iata_code": "INV",
        "latitude": 999,
        "longitude": -74.1469
    }
    response = client.post("/airports", json=payload)
    assert response.status_code == 422

def test_delete_airport():
    """DELETE /airports/{id} debe retornar 204"""
    payload = {
        "name": "Aeropuerto Temporal",
        "city": "Ciudad",
        "department": "Cundinamarca",
        "iata_code": "TMP",
        "latitude": 4.0,
        "longitude": -74.0
    }
    create = client.post("/airports", json=payload)
    if create.status_code == 201:
        airport_id = create.json()["id"]
        response = client.delete(f"/airports/{airport_id}")
        assert response.status_code == 204

# ── Pruebas del patron Adapter ─────────────────────────────────────────────────

def test_api_colombia_adapter_implements_port():
    """ApiColombiaAdapter debe implementar AirportPort"""
    adapter = ApiColombiaAdapter()
    assert isinstance(adapter, AirportPort)

def test_sqlite_adapter_implements_port():
    """SQLiteAirportAdapter debe implementar AirportPort"""
    adapter = SQLiteAirportAdapter()
    assert isinstance(adapter, AirportPort)