"""Basic random-walking target class. No hazard-avoiding logic; can move through anything."""

from search_sim.entities.interfaces import Entity
from search_sim.targets.definitions.interfaces import Target
from search_sim.targets.definitions.schema import TargetState, TargetAction
from search_sim.utils import validate_move
from random import random
from math import sin, cos

class RandomTarget(Target, Entity[TargetState]):
    def __init__(self, state: TargetState):
        self._state = state

    def get_id(self) -> str:
        return self._state.id

    def get_location(self) -> tuple[float,float]:
        return self._state.x, self._state.y

    def get_value(self) -> float:
        return self._state.value
    
    def get_desired_action(self, dt: float, environment):
        heading = random()*360
        speed = random()*self._state.max_speed
        distance = speed*dt
        x = self._state.x
        y = self._state.y
        position = (x + cos(heading) * distance, y + sin(heading) * distance)
        is_valid = validate_move(x,y,position[0],position[1],self._state.max_speed,environment,self._state.traversable_hazards)

        while not is_valid:
            heading = random()*360
            speed = random()*self._state.max_speed
            distance = speed*dt
            x = self._state.x
            y = self._state.y
            position = (x + cos(heading) * distance, y + sin(heading) * distance)
            is_valid = validate_move(x,y,position[0],position[1],self._state.max_speed,environment,self._state.traversable_hazards)


        return TargetAction(heading,speed)

    def update_state(self, new_state: TargetState) -> None:
        self._state = new_state