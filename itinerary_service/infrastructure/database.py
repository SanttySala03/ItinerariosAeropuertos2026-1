import sqlite3
import os
from typing import List, Optional
from domain.models import Itinerary, Leg
from ports.itinerary_port import ItineraryPort

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "itineraries.db")

class SQLiteItineraryAdapter(ItineraryPort):
    """
    Adapter de persistencia que implementa el puerto
    ItineraryPort usando SQLite como base de datos.
    """

    def _get_conn(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db(self):
        conn = self._get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS itineraries (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                title     TEXT NOT NULL,
                user_name TEXT NOT NULL DEFAULT ''
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

    def _map_leg(self, row) -> Leg:
        return Leg(
            id=row["id"],
            itinerary_id=row["itinerary_id"],
            origin_iata=row["origin_iata"],
            destination_iata=row["destination_iata"],
            departure_datetime=row["departure_datetime"],
            arrival_datetime=row["arrival_datetime"],
        )

    def _map_itinerary(self, row, legs: List[Leg]) -> Itinerary:
        return Itinerary(
            id=row["id"],
            title=row["title"],
            user_name=row["user_name"] if "user_name" in row.keys() else "",
            legs=legs,
        )

    def get_all(self) -> List[Itinerary]:
        conn = self._get_conn()
        rows = conn.execute("SELECT * FROM itineraries").fetchall()
        result = []
        for row in rows:
            legs_rows = conn.execute(
                "SELECT * FROM legs WHERE itinerary_id = ?", (row["id"],)
            ).fetchall()
            legs = [self._map_leg(l) for l in legs_rows]
            result.append(self._map_itinerary(row, legs))
        conn.close()
        return result

    def get_by_id(self, itinerary_id: int) -> Optional[Itinerary]:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM itineraries WHERE id = ?", (itinerary_id,)
        ).fetchone()
        if not row:
            conn.close()
            return None
        legs_rows = conn.execute(
            "SELECT * FROM legs WHERE itinerary_id = ?", (itinerary_id,)
        ).fetchall()
        legs = [self._map_leg(l) for l in legs_rows]
        conn.close()
        return self._map_itinerary(row, legs)

    def create(self, title: str, user_name: str, legs: list) -> Itinerary:
        conn = self._get_conn()
        cur = conn.execute(
            "INSERT INTO itineraries (title, user_name) VALUES (?, ?)",
            (title, user_name)
        )
        itinerary_id = cur.lastrowid
        created_legs = []
        for leg in legs:
            cur = conn.execute(
                "INSERT INTO legs (itinerary_id, origin_iata, destination_iata, departure_datetime, arrival_datetime) VALUES (?,?,?,?,?)",
                (itinerary_id, leg["origin_iata"].upper(), leg["destination_iata"].upper(), leg["departure_datetime"], leg["arrival_datetime"])
            )
            created_legs.append(Leg(
                id=cur.lastrowid,
                itinerary_id=itinerary_id,
                origin_iata=leg["origin_iata"].upper(),
                destination_iata=leg["destination_iata"].upper(),
                departure_datetime=leg["departure_datetime"],
                arrival_datetime=leg["arrival_datetime"],
            ))
        conn.commit()
        conn.close()
        return Itinerary(id=itinerary_id, title=title, user_name=user_name, legs=created_legs)

    def delete(self, itinerary_id: int) -> bool:
        conn = self._get_conn()
        result = conn.execute(
            "DELETE FROM itineraries WHERE id = ?", (itinerary_id,)
        )
        conn.commit()
        conn.close()
        return result.rowcount > 0