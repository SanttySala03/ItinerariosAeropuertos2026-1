from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models import Itinerary

class ItineraryPort(ABC):
    """
    Puerto que define el contrato para la persistencia
    de itinerarios. Siguiendo la arquitectura hexagonal,
    el dominio solo conoce este puerto, nunca la implementacion.
    """

    @abstractmethod
    def get_all(self) -> List[Itinerary]:
        pass

    @abstractmethod
    def get_by_id(self, itinerary_id: int) -> Optional[Itinerary]:
        pass

    @abstractmethod
    def create(self, title: str, user_name: str, legs: list) -> Itinerary:
        pass

    @abstractmethod
    def delete(self, itinerary_id: int) -> bool:
        pass