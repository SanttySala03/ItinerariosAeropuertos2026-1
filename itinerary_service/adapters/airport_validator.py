import urllib.request
import json
from typing import Optional

AIRPORT_SERVICE_URL = "http://127.0.0.1:8001"

class AirportValidatorAdapter:
    """
    Adapter que valida codigos IATA consultando
    el Microservicio de Aeropuertos via HTTP.

    Patron Adapter:
    - Adaptee: API REST del Airport Service
    - Target:  logica de validacion del dominio
    - Adapter: esta clase (AirportValidatorAdapter)
    """

    def validate(self, iata_code: str) -> bool:
        """
        Retorna True si el codigo IATA existe en el
        Microservicio de Aeropuertos, False si no.
        Lanza ConnectionError si el servicio no esta disponible.
        """
        try:
            url = f"{AIRPORT_SERVICE_URL}/airports/iata/{iata_code.upper()}"
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status == 200
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False
            raise ConnectionError(f"Error en Airport Service: {e.code}")
        except Exception as e:
            raise ConnectionError(f"No se pudo conectar con Airport Service: {e}")