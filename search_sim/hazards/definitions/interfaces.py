from abc import abstractmethod
from search_sim.entities.interfaces import Entity
from search_sim.hazards.definitions.types import HazardType

class Hazard(Entity):
    @abstractmethod
    def get_type(self) -> HazardType:
        pass