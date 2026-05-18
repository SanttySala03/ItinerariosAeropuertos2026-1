from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import sqlite3
import os

app = FastAPI(
    title="Itinerary — Airport Service",
    version="1.0.0",
    description="""
## Microservicio de Aeropuertos

Gestiona el catálogo de aeropuertos disponibles en el sistema Itinerary.

### Funcionalidades
- Consultar todos los aeropuertos registrados
- Registrar nuevos aeropuertos con coordenadas geográficas
- Actualizar información de aeropuertos existentes
- Eliminar aeropuertos del catálogo

### Uso
Este servicio es consumido por el **Microservicio de Itinerarios** para validar
los códigos IATA antes de guardar un itinerario.
    """,
    contact={
        "name": "David Santiago Carrillo Salamanca",
        "url": "https://github.com/SanttySala03/ItinerariosAeropuertos2026-1",
    },
    license_info={
        "name": "Universidad Central — Ingeniería de Software II — 2026",
    },
    openapi_tags=[
        {
            "name": "airports",
            "description": "Operaciones CRUD sobre el catálogo de aeropuertos",
        }
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), "airports.db")

# ── Modelos ───────────────────────────────────────────────────────
class AirportCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, example="Aeropuerto Internacional El Dorado")
    city: str = Field(..., min_length=2, max_length=60, example="Bogotá")
    country: str = Field(..., min_length=2, max_length=60, example="Colombia")
    iata_code: str = Field(..., min_length=3, max_length=3, example="BOG")
    latitude: float = Field(..., ge=-90, le=90, example=4.7016)
    longitude: float = Field(..., ge=-180, le=180, example=-74.1469)

class Airport(AirportCreate):
    id: int

# ── Base de datos ─────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS airports (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT NOT NULL,
            city      TEXT NOT NULL,
            country   TEXT NOT NULL,
            iata_code TEXT NOT NULL UNIQUE,
            latitude  REAL NOT NULL,
            longitude REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ── Endpoints ─────────────────────────────────────────────────────
@app.get(
    "/airports",
    response_model=list[Airport],
    tags=["airports"],
    summary="Listar aeropuertos",
    description="Retorna la lista completa de aeropuertos registrados en el catálogo."
)
def list_airports():
    conn = get_db()
    rows = conn.execute("SELECT * FROM airports").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get(
    "/airports/{airport_id}",
    response_model=Airport,
    tags=["airports"],
    summary="Obtener aeropuerto",
    description="Obtiene un aeropuerto específico por su ID numérico. Retorna 404 si no existe."
)
def get_airport(airport_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM airports WHERE id = ?", (airport_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Aeropuerto no encontrado")
    return dict(row)


@app.post(
    "/airports",
    response_model=Airport,
    status_code=201,
    tags=["airports"],
    summary="Crear aeropuerto",
    description="Registra un nuevo aeropuerto en el catálogo. El código IATA debe ser único de 3 letras."
)
def create_airport(data: AirportCreate):
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO airports (name, city, country, iata_code, latitude, longitude) VALUES (?,?,?,?,?,?)",
            (data.name, data.city, data.country, data.iata_code.upper(), data.latitude, data.longitude)
        )
        conn.commit()
        airport_id = cur.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un aeropuerto con código IATA '{data.iata_code.upper()}'"
        )
    finally:
        conn.close()
    return {**data.model_dump(), "id": airport_id, "iata_code": data.iata_code.upper()}


@app.put(
    "/airports/{airport_id}",
    response_model=Airport,
    tags=["airports"],
    summary="Actualizar aeropuerto",
    description="Actualiza todos los datos de un aeropuerto existente. Retorna 404 si no existe."
)
def update_airport(airport_id: int, data: AirportCreate):
    conn = get_db()
    result = conn.execute(
        "UPDATE airports SET name=?, city=?, country=?, iata_code=?, latitude=?, longitude=? WHERE id=?",
        (data.name, data.city, data.country, data.iata_code.upper(), data.latitude, data.longitude, airport_id)
    )
    conn.commit()
    conn.close()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Aeropuerto no encontrado")
    return {**data.model_dump(), "id": airport_id, "iata_code": data.iata_code.upper()}


@app.delete(
    "/airports/{airport_id}",
    status_code=204,
    tags=["airports"],
    summary="Eliminar aeropuerto",
    description="Elimina un aeropuerto del catálogo por su ID. Retorna 404 si no existe."
)
def delete_airport(airport_id: int):
    conn = get_db()
    result = conn.execute("DELETE FROM airports WHERE id = ?", (airport_id,))
    conn.commit()
    conn.close()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Aeropuerto no encontrado")