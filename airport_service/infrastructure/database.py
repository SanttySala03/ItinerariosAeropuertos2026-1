import sqlite3
import os
from typing import List, Optional
from domain.models import Airport
from ports.airport_port import AirportPort

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "airports.db")

class SQLiteAirportAdapter(AirportPort):
    """
    Adapter alternativo que usa SQLite como fuente de datos.
    Implementa el mismo puerto AirportPort, permitiendo
    intercambiar la fuente externa por una base de datos local
    sin cambiar nada en la capa de dominio ni en la API.
    """

    def _get_conn(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS airports (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name      TEXT NOT NULL,
                city      TEXT NOT NULL,
                department TEXT NOT NULL DEFAULT '',
                country   TEXT NOT NULL DEFAULT 'Colombia',
                iata_code TEXT NOT NULL UNIQUE,
                latitude  REAL NOT NULL,
                longitude REAL NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def _map(self, row) -> Airport:
        return Airport(
            id=row["id"],
            name=row["name"],
            city=row["city"],
            department=row.get("department", ""),
            iata_code=row["iata_code"],
            latitude=row["latitude"],
            longitude=row["longitude"],
        )

    def get_all(self) -> List[Airport]:
        conn = self._get_conn()
        rows = conn.execute("SELECT * FROM airports").fetchall()
        conn.close()
        return [self._map(r) for r in rows]

    def get_by_id(self, airport_id: int) -> Optional[Airport]:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM airports WHERE id = ?", (airport_id,)
        ).fetchone()
        conn.close()
        return self._map(row) if row else None

    def get_by_iata(self, iata_code: str) -> Optional[Airport]:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM airports WHERE iata_code = ?", (iata_code.upper(),)
        ).fetchone()
        conn.close()
        return self._map(row) if row else None

    def create(self, data: dict) -> Airport:
        conn = self._get_conn()
        try:
            cur = conn.execute(
                "INSERT INTO airports (name, city, department, iata_code, latitude, longitude) VALUES (?,?,?,?,?,?)",
                (data["name"], data["city"], data.get("department",""), data["iata_code"].upper(), data["latitude"], data["longitude"])
            )
            conn.commit()
            airport_id = cur.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError(f"Ya existe un aeropuerto con IATA '{data['iata_code'].upper()}'")
        finally:
            conn.close()
        return Airport(
            id=airport_id,
            name=data["name"],
            city=data["city"],
            department=data.get("department", ""),
            iata_code=data["iata_code"].upper(),
            latitude=data["latitude"],
            longitude=data["longitude"],
        )

    def update(self, airport_id: int, data: dict) -> Optional[Airport]:
        conn = self._get_conn()
        result = conn.execute(
            "UPDATE airports SET name=?, city=?, department=?, iata_code=?, latitude=?, longitude=? WHERE id=?",
            (data["name"], data["city"], data.get("department",""), data["iata_code"].upper(), data["latitude"], data["longitude"], airport_id)
        )
        conn.commit()
        conn.close()
        if result.rowcount == 0:
            return None
        return Airport(id=airport_id, name=data["name"], city=data["city"], department=data.get("department",""), iata_code=data["iata_code"].upper(), latitude=data["latitude"], longitude=data["longitude"])

    def delete(self, airport_id: int) -> bool:
        conn = self._get_conn()
        result = conn.execute("DELETE FROM airports WHERE id = ?", (airport_id,))
        conn.commit()
        conn.close()
        return result.rowcount > 0