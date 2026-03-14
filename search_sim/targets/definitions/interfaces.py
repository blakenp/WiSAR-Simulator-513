from abc import abstractmethod
from search_sim.entities.interfaces import Entity
from search_sim.targets.definitions.schema import TargetState

class Target(Entity[TargetState]):
    @abstractmethod
    def get_value(self) -> float:
        pass