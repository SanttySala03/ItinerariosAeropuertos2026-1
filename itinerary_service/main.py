from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import sqlite3
import httpx

app = FastAPI(title="Itinerary Service", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
DB_PATH = os.path.join(os.path.dirname(__file__), "itineraries.db")
AIRPORT_SERVICE_URL = "http://127.0.0.1:8001"

# ── Modelos de datos ──────────────────────────────────────────────
class LegCreate(BaseModel):
    origin_iata: str = Field(..., min_length=3, max_length=3)
    destination_iata: str = Field(..., min_length=3, max_length=3)
    departure_datetime: str = Field(..., description="Formato: YYYY-MM-DD HH:MM")
    arrival_datetime: str = Field(..., description="Formato: YYYY-MM-DD HH:MM")

class Leg(LegCreate):
    id: int
    itinerary_id: int

class ItineraryCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    legs: list[LegCreate] = Field(..., min_length=1)

class Itinerary(BaseModel):
    id: int
    title: str
    legs: list[Leg]

# ── Base de datos ─────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS itineraries (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS legs (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            itinerary_id       INTEGER NOT NULL,
            origin_iata        TEXT NOT NULL,
            destination_iata   TEXT NOT NULL,
            departure_datetime TEXT NOT NULL,
            arrival_datetime   TEXT NOT NULL,
            FOREIGN KEY (itinerary_id) REFERENCES itineraries(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ── Validación con microservicio de aeropuertos ───────────────────
def validate_iata(iata_code: str):
    try:
        import urllib.request
        import json as json_lib
        with urllib.request.urlopen(f"{AIRPORT_SERVICE_URL}/airports", timeout=5) as r:
            airports = json_lib.loads(r.read())
        codes = [a["iata_code"] for a in airports]
        if iata_code.upper() not in codes:
            raise HTTPException(
                status_code=400,
                detail=f"El código IATA '{iata_code.upper()}' no existe en el sistema"
            )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=503,
            detail="No se puede conectar con el servicio de aeropuertos"
        )

# ── Endpoints ─────────────────────────────────────────────────────
@app.get("/itineraries", response_model=list[Itinerary])
def list_itineraries():
    conn = get_db()
    itineraries = conn.execute("SELECT * FROM itineraries").fetchall()
    result = []
    for itin in itineraries:
        legs = conn.execute(
            "SELECT * FROM legs WHERE itinerary_id = ?", (itin["id"],)
        ).fetchall()
        result.append({"id": itin["id"], "title": itin["title"], "legs": [dict(l) for l in legs]})
    conn.close()
    return result

@app.get("/itineraries/{itinerary_id}", response_model=Itinerary)
def get_itinerary(itinerary_id: int):
    conn = get_db()
    itin = conn.execute("SELECT * FROM itineraries WHERE id = ?", (itinerary_id,)).fetchone()
    if not itin:
        raise HTTPException(status_code=404, detail="Itinerario no encontrado")
    legs = conn.execute(
        "SELECT * FROM legs WHERE itinerary_id = ?", (itinerary_id,)
    ).fetchall()
    conn.close()
    return {"id": itin["id"], "title": itin["title"], "legs": [dict(l) for l in legs]}

@app.post("/itineraries", response_model=Itinerary, status_code=201)
def create_itinerary(data: ItineraryCreate):
    for leg in data.legs:
        validate_iata(leg.origin_iata)
        validate_iata(leg.destination_iata)

    conn = get_db()
    cur = conn.execute("INSERT INTO itineraries (title) VALUES (?)", (data.title,))
    itinerary_id = cur.lastrowid

    legs_result = []
    for leg in data.legs:
        cur = conn.execute(
            "INSERT INTO legs (itinerary_id, origin_iata, destination_iata, departure_datetime, arrival_datetime) VALUES (?,?,?,?,?)",
            (itinerary_id, leg.origin_iata.upper(), leg.destination_iata.upper(), leg.departure_datetime, leg.arrival_datetime)
        )
        legs_result.append({
            "id": cur.lastrowid,
            "itinerary_id": itinerary_id,
            **leg.model_dump(),
            "origin_iata": leg.origin_iata.upper(),
            "destination_iata": leg.destination_iata.upper()
        })

    conn.commit()
    conn.close()
    return {"id": itinerary_id, "title": data.title, "legs": legs_result}

@app.put("/itineraries/{itinerary_id}", response_model=Itinerary)
def update_itinerary(itinerary_id: int, data: ItineraryCreate):
    for leg in data.legs:
        validate_iata(leg.origin_iata)
        validate_iata(leg.destination_iata)

    conn = get_db()
    result = conn.execute(
        "UPDATE itineraries SET title = ? WHERE id = ?", (data.title, itinerary_id)
    )
    if result.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Itinerario no encontrado")

    conn.execute("DELETE FROM legs WHERE itinerary_id = ?", (itinerary_id,))

    legs_result = []
    for leg in data.legs:
        cur = conn.execute(
            "INSERT INTO legs (itinerary_id, origin_iata, destination_iata, departure_datetime, arrival_datetime) VALUES (?,?,?,?,?)",
            (itinerary_id, leg.origin_iata.upper(), leg.destination_iata.upper(), leg.departure_datetime, leg.arrival_datetime)
        )
        legs_result.append({
            "id": cur.lastrowid,
            "itinerary_id": itinerary_id,
            **leg.model_dump(),
            "origin_iata": leg.origin_iata.upper(),
            "destination_iata": leg.destination_iata.upper()
        })

    conn.commit()
    conn.close()
    return {"id": itinerary_id, "title": data.title, "legs": legs_result}

@app.delete("/itineraries/{itinerary_id}", status_code=204)
def delete_itinerary(itinerary_id: int):
    conn = get_db()
    result = conn.execute("DELETE FROM itineraries WHERE id = ?", (itinerary_id,))
    conn.commit()
    conn.close()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Itinerario no encontrado")