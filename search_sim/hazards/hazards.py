"""Running water hazard class for e.g. a river or creek"""

from search_sim.hazards.definitions.interfaces import Hazard
from search_sim.entities.interfaces import Entity
from search_sim.hazards.definitions.schema import HazardType, HazardState

class RunningWater(Hazard, Entity[HazardState]):
    def __init__(self, state: HazardState):
        self._state = state

    def get_id(self) -> str:
        return self._state.id

    def get_location(self) -> tuple[float,float]:
        return self._state.x, self._state.y

    def get_type(self) -> HazardType:
        return self._state.type

    def update_state(self, new_state):
        self._state = new_state
    
"""Standing water hazard class for e.g. a pond or lake"""

"""Separate from running water just in case I guess"""

class StandingWater(Hazard, Entity[HazardState]):
    def __init__(self, state: HazardState):
        self._state = state

    def get_id(self) -> str:
        return self._state.id

    def get_location(self) -> tuple[float,float]:
        return self._state.x, self._state.y

    def get_type(self) -> HazardType:
        return self._state.type

    def update_state(self, new_state):
        self._state = new_state
    
"""Tree hazard class"""

"""Could be a single tree if the grid size is small enough, or a particularly dense stand of trees"""

class Tree(Hazard, Entity[HazardState]):
    def __init__(self, state: HazardState):
        self._state = state

    def get_id(self) -> str:
        return self._state.id

    def get_location(self) -> tuple[float,float]:
        return self._state.x, self._state.y

    def get_type(self) -> HazardType:
        return self._state.type

    def update_state(self, new_state):
        self._state = new_state
    
"""Undergrowth hazard class"""

class Undergrowth(Hazard, Entity[HazardState]):
    def __init__(self, state: HazardState):
        self._state = state

    def get_id(self) -> str:
        return self._state.id

    def get_location(self) -> tuple[float,float]:
        return self._state.x, self._state.y

    def get_type(self) -> HazardType:
        return self._state.type

    def update_state(self, new_state):
        self._state = new_state
    
"""Boulder hazard class"""

class Boulder(Hazard, Entity[HazardState]):
    def __init__(self, state: HazardState):
        self._state = state

    def get_id(self) -> str:
        return self._state.id

    def get_location(self) -> tuple[float,float]:
        return self._state.x, self._state.y

    def get_type(self) -> HazardType:
        return self._state.type

    def update_state(self, new_state):
        self._state = new_state