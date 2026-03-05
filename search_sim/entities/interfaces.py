from abc import ABC, abstractmethod

class Entity(ABC):
    @abstractmethod
    def get_id(self) -> str:
        pass

    @abstractmethod
    def get_location(self) -> tuple[float,float]:
        pass

    # what other shared methods are there?