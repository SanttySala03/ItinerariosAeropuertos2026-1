from dataclasses import dataclass

@dataclass
class Airport:
    """Entidad del dominio — modelo interno independiente de cualquier fuente externa"""
    id: int
    name: str
    city: str
    department: str
    iata_code: str
    latitude: float
    longitude: float

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "department": self.department,
            "iata_code": self.iata_code,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }