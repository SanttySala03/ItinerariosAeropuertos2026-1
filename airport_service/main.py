from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import sqlite3

app = FastAPI(title="Airport Service", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
DB_PATH = os.path.join(os.path.dirname(__file__), "airports.db")

# ── Modelo de datos ───────────────────────────────────────────────
class AirportCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    city: str = Field(..., min_length=2, max_length=60)
    country: str = Field(..., min_length=2, max_length=60)
    iata_code: str = Field(..., min_length=3, max_length=3)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

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
@app.get("/airports", response_model=list[Airport])
def list_airports():
    conn = get_db()
    rows = conn.execute("SELECT * FROM airports").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/airports/{airport_id}", response_model=Airport)
def get_airport(airport_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM airports WHERE id = ?", (airport_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Aeropuerto no encontrado")
    return dict(row)

@app.post("/airports", response_model=Airport, status_code=201)
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
        raise HTTPException(status_code=400, detail=f"Ya existe un aeropuerto con código IATA '{data.iata_code.upper()}'")
    finally:
        conn.close()
    return {**data.model_dump(), "id": airport_id, "iata_code": data.iata_code.upper()}

@app.put("/airports/{airport_id}", response_model=Airport)
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

@app.delete("/airports/{airport_id}", status_code=204)
def delete_airport(airport_id: int):
    conn = get_db()
    result = conn.execute("DELETE FROM airports WHERE id = ?", (airport_id,))
    conn.commit()
    conn.close()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Aeropuerto no encontrado")