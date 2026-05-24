import urllib.request
import json
from typing import List, Optional
from domain.models import Airport
from ports.airport_port import AirportPort

API_COLOMBIA_URL = "https://api-colombia.com/api/v1/Airport"

class ApiColombiaAdapter(AirportPort):
    """
    Adapter que traduce la respuesta de la API publica API Colombia
    al modelo de dominio interno Airport.

    Patron Adapter:
    - Adaptee: API Colombia (fuente externa)
    - Target:  AirportPort (interfaz interna del dominio)
    - Adapter: esta clase (ApiColombiaAdapter)

    El frontend y el Microservicio de Itinerarios solo conocen
    el modelo Airport del dominio, nunca la estructura JSON de
    la API Colombia.
    """

    def _fetch(self, url: str):
        try:
            req = urllib.request.Request(
                url,
                headers={"Accept": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            raise ConnectionError(f"No se pudo conectar con API Colombia: {e}")

    def _map(self, data: dict) -> Optional[Airport]:
        """Traduce el JSON de API Colombia al modelo de dominio Airport"""
        if not data:
            return None

        # API Colombia usa 'oaci' para el codigo IATA en algunos registros
        iata = (
            data.get("iataCode") or
            data.get("iata") or
            data.get("oaci") or
            ""
        ).strip().upper()

        # Coordenadas pueden venir en distintos campos segun la version
        lat = data.get("latitude") or data.get("lat") or 0.0
        lng = data.get("longitude") or data.get("lng") or data.get("lon") or 0.0

        city = ""
        if isinstance(data.get("city"), dict):
            city = data["city"].get("name", "")
        elif isinstance(data.get("city"), str):
            city = data["city"]

        department = ""
        if isinstance(data.get("department"), dict):
            department = data["department"].get("name", "")
        elif isinstance(data.get("department"), str):
            department = data["department"]

        return Airport(
            id=data.get("id", 0),
            name=data.get("name", ""),
            city=city,
            department=department,
            iata_code=iata,
            latitude=float(lat),
            longitude=float(lng),
        )

    def get_all(self) -> List[Airport]:
        data = self._fetch(API_COLOMBIA_URL)
        airports = []
        for item in data:
            airport = self._map(item)
            if airport and airport.iata_code:
                airports.append(airport)
        return airports

    def get_by_id(self, airport_id: int) -> Optional[Airport]:
        try:
            data = self._fetch(f"{API_COLOMBIA_URL}/{airport_id}")
            return self._map(data)
        except Exception:
            return None

    def get_by_iata(self, iata_code: str) -> Optional[Airport]:
        airports = self.get_all()
        for airport in airports:
            if airport.iata_code == iata_code.upper():
                return airport
        return None