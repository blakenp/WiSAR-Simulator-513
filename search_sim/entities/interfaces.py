from abc import ABC, abstractmethod

class Entity[TStateData](ABC):
    @abstractmethod
    def get_id(self) -> str:
        """Returns the unique identifier for this entity."""
        pass

    @abstractmethod
    def get_location(self) -> tuple[float,float]:
        """Returns the current (x,y) coordinates of the entity."""
        pass

    @abstractmethod
    def update_state(self, new_state: TStateData) -> None:
        """The 'Sync' method used by the Simulator Orchestrator."""
        pass