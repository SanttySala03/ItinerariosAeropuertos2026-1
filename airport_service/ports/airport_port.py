from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models import Airport

class AirportPort(ABC):
    @abstractmethod
    def get_all(self) -> List[Airport]:
        pass

    @abstractmethod
    def get_by_id(self, airport_id: int) -> Optional[Airport]:
        pass

    @abstractmethod
    def get_by_iata(self, iata_code: str) -> Optional[Airport]:
        pass
