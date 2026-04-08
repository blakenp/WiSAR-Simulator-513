from abc import abstractmethod
from search_sim.entities.interfaces import Entity
from search_sim.targets.definitions.schema import TargetState, TargetAction

class Target(Entity[TargetState]):
    @abstractmethod
    def get_value(self) -> float:
        pass

    @abstractmethod
    def get_desired_action(self, dt: float, environment) -> TargetAction:
        """The target's decision-making method, which outputs the next most desirable action to be taken."""
        pass