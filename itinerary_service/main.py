import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

from domain.models import Itinerary, Leg
from ports.itinerary_port import ItineraryPort
from adapters.airport_validator import AirportValidatorAdapter
from infrastructure.database import SQLiteItineraryAdapter

app = FastAPI(
    title="Itinerary - Itinerary Service",
    version="2.0.0",
    description="Microservicio de Itinerarios con arquitectura hexagonal y patron Adapter",
    openapi_tags=[{"name": "itineraries", "description": "CRUD de itinerarios con validacion de aeropuertos"}]
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

db = SQLiteItineraryAdapter()
db.init_db()
validator = AirportValidatorAdapter()

class LegCreate(BaseModel):
    origin_iata: str = Field(..., min_length=3, max_length=3)
    destination_iata: str = Field(..., min_length=3, max_length=3)
    departure_datetime: str
    arrival_datetime: str

class ItineraryCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    user_name: str = Field(..., min_length=2, max_length=60)
    legs: List[LegCreate] = Field(..., min_length=1)

class LegResponse(BaseModel):
    id: int
    itinerary_id: int
    origin_iata: str
    destination_iata: str
    departure_datetime: str
    arrival_datetime: str

class ItineraryResponse(BaseModel):
    id: int
    title: str
    user_name: str
    legs: List[LegResponse]

@app.get("/itineraries", response_model=List[ItineraryResponse], tags=["itineraries"], summary="Listar itinerarios")
def list_itineraries():
    return [i.to_dict() for i in db.get_all()]

@app.get("/itineraries/{itinerary_id}", response_model=ItineraryResponse, tags=["itineraries"], summary="Obtener itinerario")
def get_itinerary(itinerary_id: int):
    itinerary = db.get_by_id(itinerary_id)
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerario no encontrado")
    return itinerary.to_dict()

@app.post("/itineraries", response_model=ItineraryResponse, status_code=201, tags=["itineraries"], summary="Crear itinerario")
def create_itinerary(data: ItineraryCreate):
    try:
        for leg in data.legs:
            if not validator.validate(leg.origin_iata):
                raise HTTPException(status_code=400, detail=f"IATA '{leg.origin_iata.upper()}' no existe")
            if not validator.validate(leg.destination_iata):
                raise HTTPException(status_code=400, detail=f"IATA '{leg.destination_iata.upper()}' no existe")
    except HTTPException:
        raise
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    itinerary = db.create(title=data.title, user_name=data.user_name, legs=[l.model_dump() for l in data.legs])
    return itinerary.to_dict()

@app.delete("/itineraries/{itinerary_id}", status_code=204, tags=["itineraries"], summary="Eliminar itinerario")
def delete_itinerary(itinerary_id: int):
    if not db.delete(itinerary_id):
        raise HTTPException(status_code=404, detail="Itinerario no encontrado")