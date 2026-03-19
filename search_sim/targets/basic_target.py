"""Basic stationary target class"""

from search_sim.entities.interfaces import Entity
from search_sim.targets.definitions.interfaces import Target
from search_sim.targets.definitions.schema import TargetState, TargetAction

class BasicTarget(Target, Entity[TargetState]):
    def __init__(self, state: TargetState):
        self._state = state

    def get_id(self) -> str:
        return self._state.id

    def get_location(self) -> tuple[float,float]:
        return self._state.x, self._state.y

    def get_value(self) -> float:
        return self._state.value
    
    def get_desired_action(self):
        return TargetAction(0,0)

    def update_state(self, new_state: TargetState) -> None:
        self._state = new_state