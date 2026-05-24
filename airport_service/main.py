import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

from domain.models import Airport
from ports.airport_port import AirportPort
from adapters.api_colombia_adapter import ApiColombiaAdapter
from infrastructure.database import SQLiteAirportAdapter

app = FastAPI(
    title="Itinerary — Airport Service",
    version="2.0.0",
    description="""
## Microservicio de Aeropuertos

Implementa arquitectura hexagonal con el patron Adapter.

### Patron Adapter
- **Puerto (interfaz):** `AirportPort` — contrato del dominio
- **Adapter externo:** `ApiColombiaAdapter` — consume API Colombia
- **Adapter interno:** `SQLiteAirportAdapter` — persistencia local
- El frontend y el Microservicio de Itinerarios solo conocen
  el modelo `Airport` del dominio, nunca la estructura de API Colombia.

### Arquitectura Hexagonal
- **Dominio:** `domain/models.py` — entidad Airport
- **Puertos:** `ports/airport_port.py` — interfaz AirportPort
- **Adaptadores:** `adapters/` y `infrastructure/` — implementaciones
- **API:** `main.py` — capa de entrada REST
    """,
    contact={
        "name": "David Santiago Carrillo Salamanca",
        "url": "https://github.com/SanttySala03/ItinerariosAeropuertos2026-1",
    },
    license_info={
        "name": "Universidad Central - Ingenieria de Software II - 2026",
    },
    openapi_tags=[
        {
            "name": "airports",
            "description": "Operaciones sobre el catalogo de aeropuertos colombianos",
        },
        {
            "name": "sync",
            "description": "Sincronizacion con API Colombia",
        }
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Inyeccion de dependencias ──────────────────────────────────────────────────
# El puerto acepta cualquier adapter — aqui se decide cual usar
db_adapter = SQLiteAirportAdapter()
db_adapter._init_db()

api_colombia = ApiColombiaAdapter()

# ── Modelos Pydantic (capa de entrada) ────────────────────────────────────────
class AirportCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100,
                      json_schema_extra={"example": "Aeropuerto Internacional El Dorado"})
    city: str = Field(..., min_length=2, max_length=60,
                      json_schema_extra={"example": "Bogota"})
    department: str = Field(default="", max_length=60,
                            json_schema_extra={"example": "Cundinamarca"})
    iata_code: str = Field(..., min_length=3, max_length=3,
                           json_schema_extra={"example": "BOG"})
    latitude: float = Field(..., ge=-90, le=90,
                            json_schema_extra={"example": 4.7016})
    longitude: float = Field(..., ge=-180, le=180,
                             json_schema_extra={"example": -74.1469})

class AirportResponse(BaseModel):
    id: int
    name: str
    city: str
    department: str
    iata_code: str
    latitude: float
    longitude: float

# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get(
    "/airports",
    response_model=List[AirportResponse],
    tags=["airports"],
    summary="Listar aeropuertos",
    description="Retorna todos los aeropuertos del catalogo local (SQLite)."
)
def list_airports():
    airports = db_adapter.get_all()
    return [a.to_dict() for a in airports]


@app.get(
    "/airports/{airport_id}",
    response_model=AirportResponse,
    tags=["airports"],
    summary="Obtener aeropuerto por ID",
    description="Obtiene un aeropuerto especifico por su ID. Retorna 404 si no existe."
)
def get_airport(airport_id: int):
    airport = db_adapter.get_by_id(airport_id)
    if not airport:
        raise HTTPException(status_code=404, detail="Aeropuerto no encontrado")
    return airport.to_dict()


@app.get(
    "/airports/iata/{iata_code}",
    response_model=AirportResponse,
    tags=["airports"],
    summary="Obtener aeropuerto por IATA",
    description="Obtiene un aeropuerto por su codigo IATA de 3 letras."
)
def get_airport_by_iata(iata_code: str):
    airport = db_adapter.get_by_iata(iata_code)
    if not airport:
        raise HTTPException(
            status_code=404,
            detail=f"No existe aeropuerto con IATA '{iata_code.upper()}'"
        )
    return airport.to_dict()


@app.post(
    "/airports",
    response_model=AirportResponse,
    status_code=201,
    tags=["airports"],
    summary="Crear aeropuerto",
    description="Registra un nuevo aeropuerto en el catalogo local."
)
def create_airport(data: AirportCreate):
    try:
        airport = db_adapter.create(data.model_dump())
        return airport.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put(
    "/airports/{airport_id}",
    response_model=AirportResponse,
    tags=["airports"],
    summary="Actualizar aeropuerto",
    description="Actualiza los datos de un aeropuerto existente."
)
def update_airport(airport_id: int, data: AirportCreate):
    airport = db_adapter.update(airport_id, data.model_dump())
    if not airport:
        raise HTTPException(status_code=404, detail="Aeropuerto no encontrado")
    return airport.to_dict()


@app.delete(
    "/airports/{airport_id}",
    status_code=204,
    tags=["airports"],
    summary="Eliminar aeropuerto",
    description="Elimina un aeropuerto del catalogo local."
)
def delete_airport(airport_id: int):
    deleted = db_adapter.delete(airport_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Aeropuerto no encontrado")


@app.post(
    "/airports/sync",
    tags=["sync"],
    summary="Sincronizar con API Colombia",
    description="""
Consume la API publica API Colombia mediante el **Adapter** `ApiColombiaAdapter`,
traduce los datos al modelo de dominio interno `Airport` y los persiste en SQLite.

Este endpoint demuestra formalmente el patron Adapter:
- La API Colombia actua como **Adaptee** (fuente externa)
- `AirportPort` es el **Target** (interfaz interna)
- `ApiColombiaAdapter` es el **Adapter** (traductor)
    """
)
def sync_from_api_colombia():
    try:
        airports = api_colombia.get_all()
        imported = 0
        skipped = 0
        for airport in airports:
            if not airport.iata_code:
                skipped += 1
                continue
            existing = db_adapter.get_by_iata(airport.iata_code)
            if existing:
                skipped += 1
                continue
            try:
                db_adapter.create(airport.to_dict())
                imported += 1
            except Exception:
                skipped += 1
        return {
            "message": "Sincronizacion completada",
            "imported": imported,
            "skipped": skipped,
            "total_in_api": len(airports)
        }
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))