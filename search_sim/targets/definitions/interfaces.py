from abc import ABC, abstractmethod

class Target(ABC):
    @abstractmethod
    def get_id(self) -> str:
        pass

    @abstractmethod
    def get_location(self) -> tuple[float,float]:
        pass

    @abstractmethod
    def get_value(self) -> float:
        pass