import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

client = TestClient(app)

# ── Pruebas de aeropuertos ────────────────────────────────────────────────────

def test_list_airports_returns_200():
    """GET /airports debe retornar 200"""
    response = client.get("/airports")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_airport_success():
    """POST /airports debe crear un aeropuerto y retornar 201"""
    payload = {
        "name": "Aeropuerto de Prueba",
        "city": "Ciudad de Prueba",
        "country": "Colombia",
        "iata_code": "TST",
        "latitude": 4.7016,
        "longitude": -74.1469
    }
    response = client.post("/airports", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["iata_code"] == "TST"
    assert data["city"] == "Ciudad de Prueba"
    assert "id" in data

def test_create_airport_duplicate_iata():
    """POST /airports con IATA duplicado debe retornar 400"""
    payload = {
        "name": "Aeropuerto Duplicado",
        "city": "Ciudad",
        "country": "Colombia",
        "iata_code": "TST",
        "latitude": 4.7016,
        "longitude": -74.1469
    }
    response = client.post("/airports", json=payload)
    assert response.status_code == 400

def test_get_airport_by_id():
    """GET /airports/{id} debe retornar el aeropuerto correcto"""
    # Primero crear uno
    payload = {
        "name": "Aeropuerto El Dorado",
        "city": "Bogotá",
        "country": "Colombia",
        "iata_code": "BOG",
        "latitude": 4.7016,
        "longitude": -74.1469
    }
    create = client.post("/airports", json=payload)
    if create.status_code == 201:
        airport_id = create.json()["id"]
        response = client.get(f"/airports/{airport_id}")
        assert response.status_code == 200
        assert response.json()["iata_code"] == "BOG"

def test_get_airport_not_found():
    """GET /airports/{id} con ID inexistente debe retornar 404"""
    response = client.get("/airports/99999")
    assert response.status_code == 404

def test_create_airport_invalid_latitude():
    """POST /airports con latitud inválida debe retornar 422"""
    payload = {
        "name": "Aeropuerto Inválido",
        "city": "Ciudad",
        "country": "Colombia",
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
        "country": "Colombia",
        "iata_code": "TMP",
        "latitude": 4.0,
        "longitude": -74.0
    }
    create = client.post("/airports", json=payload)
    if create.status_code == 201:
        airport_id = create.json()["id"]
        response = client.delete(f"/airports/{airport_id}")
        assert response.status_code == 204