import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

def test_list_itineraries_returns_200():
    response = client.get("/itineraries")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@patch("adapters.airport_validator.AirportValidatorAdapter.validate")
def test_create_itinerary_success(mock_validate):
    mock_validate.return_value = True
    payload = {
        "title": "Viaje de prueba",
        "user_name": "David Carrillo",
        "legs": [{"origin_iata": "BOG", "destination_iata": "MAD", "departure_datetime": "2026-06-01 10:00", "arrival_datetime": "2026-06-02 08:00"}]
    }
    response = client.post("/itineraries", json=payload)
    assert response.status_code == 201
    assert response.json()["title"] == "Viaje de prueba"
    assert response.json()["user_name"] == "David Carrillo"

@patch("adapters.airport_validator.AirportValidatorAdapter.validate")
def test_create_itinerary_invalid_iata(mock_validate):
    mock_validate.return_value = False
    payload = {
        "title": "Viaje invalido",
        "user_name": "David Carrillo",
        "legs": [{"origin_iata": "XXX", "destination_iata": "YYY", "departure_datetime": "2026-06-01 10:00", "arrival_datetime": "2026-06-02 08:00"}]
    }
    response = client.post("/itineraries", json=payload)
    assert response.status_code == 400

@patch("adapters.airport_validator.AirportValidatorAdapter.validate")
def test_create_itinerary_multiple_legs(mock_validate):
    mock_validate.return_value = True
    payload = {
        "title": "Viaje multi-tramo",
        "user_name": "David Carrillo",
        "legs": [
            {"origin_iata": "BOG", "destination_iata": "MAD", "departure_datetime": "2026-06-01 10:00", "arrival_datetime": "2026-06-02 08:00"},
            {"origin_iata": "MAD", "destination_iata": "LHR", "departure_datetime": "2026-06-03 09:00", "arrival_datetime": "2026-06-03 10:30"}
        ]
    }
    response = client.post("/itineraries", json=payload)
    assert response.status_code == 201
    assert len(response.json()["legs"]) == 2

def test_get_itinerary_not_found():
    response = client.get("/itineraries/99999")
    assert response.status_code == 404

def test_create_itinerary_empty_title():
    payload = {"title": "", "user_name": "David", "legs": []}
    response = client.post("/itineraries", json=payload)
    assert response.status_code in [400, 422]

@patch("adapters.airport_validator.AirportValidatorAdapter.validate")
def test_delete_itinerary(mock_validate):
    mock_validate.return_value = True
    payload = {
        "title": "Itinerario a eliminar",
        "user_name": "David Carrillo",
        "legs": [{"origin_iata": "BOG", "destination_iata": "MAD", "departure_datetime": "2026-06-01 10:00", "arrival_datetime": "2026-06-02 08:00"}]
    }
    create = client.post("/itineraries", json=payload)
    if create.status_code == 201:
        itin_id = create.json()["id"]
        response = client.delete(f"/itineraries/{itin_id}")
        assert response.status_code == 204