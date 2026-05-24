from dataclasses import dataclass, field
from typing import List

@dataclass
class Leg:
    """Tramo de vuelo — entidad del dominio"""
    id: int
    itinerary_id: int
    origin_iata: str
    destination_iata: str
    departure_datetime: str
    arrival_datetime: str

    def to_dict(self):
        return {
            "id": self.id,
            "itinerary_id": self.itinerary_id,
            "origin_iata": self.origin_iata,
            "destination_iata": self.destination_iata,
            "departure_datetime": self.departure_datetime,
            "arrival_datetime": self.arrival_datetime,
        }

@dataclass
class Itinerary:
    """Itinerario de viaje — entidad raiz del dominio"""
    id: int
    title: str
    user_name: str
    legs: List[Leg] = field(default_factory=list)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "user_name": self.user_name,
            "legs": [l.to_dict() for l in self.legs],
        }