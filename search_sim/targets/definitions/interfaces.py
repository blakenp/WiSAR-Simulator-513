from abc import abstractmethod
from search_sim.entities.interfaces import Entity

class Target(Entity):
    @abstractmethod
    def get_value(self) -> float:
        pass