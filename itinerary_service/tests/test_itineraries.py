import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

client = TestClient(app)

# ── Mock del servicio de aeropuertos ──────────────────────────────────────────
def mock_airport_valid(iata_code):
    airports = {
        "BOG": {"id": 1, "iata_code": "BOG", "city": "Bogotá", "name": "El Dorado", "country": "Colombia", "latitude": 4.7016, "longitude": -74.1469},
        "MAD": {"id": 2, "iata_code": "MAD", "city": "Madrid", "name": "Barajas", "country": "España", "latitude": 40.4719, "longitude": -3.5626},
        "LHR": {"id": 3, "iata_code": "LHR", "city": "Londres", "name": "Heathrow", "country": "UK", "latitude": 51.47, "longitude": -0.4543},
    }
    return airports.get(iata_code)

# ── Pruebas de itinerarios ────────────────────────────────────────────────────

def test_list_itineraries_returns_200():
    """GET /itineraries debe retornar 200 y una lista"""
    response = client.get("/itineraries")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@patch("main.validate_airport_iata")
def test_create_itinerary_success(mock_validate):
    """POST /itineraries debe crear itinerario con IATA válidos"""
    mock_validate.side_effect = mock_airport_valid
    payload = {
        "title": "Viaje de prueba",
        "legs": [
            {
                "origin_iata": "BOG",
                "destination_iata": "MAD",
                "departure_datetime": "2026-06-01 10:00",
                "arrival_datetime": "2026-06-02 08:00"
            }
        ]
    }
    response = client.post("/itineraries", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Viaje de prueba"
    assert len(data["legs"]) == 1

@patch("main.validate_airport_iata")
def test_create_itinerary_invalid_iata(mock_validate):
    """POST /itineraries con IATA inválido debe retornar 400"""
    mock_validate.return_value = None
    payload = {
        "title": "Viaje inválido",
        "legs": [
            {
                "origin_iata": "XXX",
                "destination_iata": "YYY",
                "departure_datetime": "2026-06-01 10:00",
                "arrival_datetime": "2026-06-02 08:00"
            }
        ]
    }
    response = client.post("/itineraries", json=payload)
    assert response.status_code == 400

@patch("main.validate_airport_iata")
def test_create_itinerary_multiple_legs(mock_validate):
    """POST /itineraries debe soportar múltiples tramos"""
    mock_validate.side_effect = mock_airport_valid
    payload = {
        "title": "Viaje multi-tramo",
        "legs": [
            {
                "origin_iata": "BOG",
                "destination_iata": "MAD",
                "departure_datetime": "2026-06-01 10:00",
                "arrival_datetime": "2026-06-02 08:00"
            },
            {
                "origin_iata": "MAD",
                "destination_iata": "LHR",
                "departure_datetime": "2026-06-03 09:00",
                "arrival_datetime": "2026-06-03 10:30"
            }
        ]
    }
    response = client.post("/itineraries", json=payload)
    assert response.status_code == 201
    assert len(response.json()["legs"]) == 2

def test_get_itinerary_not_found():
    """GET /itineraries/{id} con ID inexistente debe retornar 404"""
    response = client.get("/itineraries/99999")
    assert response.status_code == 404

def test_create_itinerary_empty_title():
    """POST /itineraries sin título debe retornar 422"""
    payload = {
        "title": "",
        "legs": []
    }
    response = client.post("/itineraries", json=payload)
    assert response.status_code in [400, 422]

@patch("main.validate_airport_iata")
def test_delete_itinerary(mock_validate):
    """DELETE /itineraries/{id} debe retornar 204"""
    mock_validate.side_effect = mock_airport_valid
    payload = {
        "title": "Itinerario a eliminar",
        "legs": [
            {
                "origin_iata": "BOG",
                "destination_iata": "MAD",
                "departure_datetime": "2026-06-01 10:00",
                "arrival_datetime": "2026-06-02 08:00"
            }
        ]
    }
    create = client.post("/itineraries", json=payload)
    if create.status_code == 201:
        itin_id = create.json()["id"]
        response = client.delete(f"/itineraries/{itin_id}")
        assert response.status_code == 204