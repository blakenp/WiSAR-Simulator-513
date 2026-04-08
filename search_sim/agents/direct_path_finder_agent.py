"""Base agent class and state definitions."""

from search_sim.agents.definitions.schema import AgentAction, AgentState
from search_sim.agents.definitions.interfaces import Agent
from search_sim.entities.interfaces import Entity
from search_sim.world.probability_map import ProbabilityMap
from search_sim.utils import validate_move
from numpy import pi
import math

class DirectPathFinderAgent(Agent, Entity[AgentState]):
    def __init__(self, initial_agent_state: AgentState, initial_map: ProbabilityMap):
        self._state = initial_agent_state
        self.belief_map = initial_map

    def get_id(self) -> str:
        return self._state.id

    def get_location(self) -> tuple[float, float]:
        return self._state.x, self._state.y

    def get_desired_action(self, dt: float, environment) -> AgentAction:
        goal_x, goal_y = self.belief_map.get_max_probability_location()
        
        dx = goal_x - self._state.x
        dy = goal_y - self._state.y
        
        # atan2 returns radians, we convert to degrees 0-360
        angle_rad = math.atan2(dy, dx)
        target_heading = math.degrees(angle_rad) % 360

        """Validate move"""
        speed = self._state.speed_mps
        distance = speed*dt
        x = self._state.x
        y = self._state.y
        position = (x + math.cos(angle_rad) * distance, y + math.sin(angle_rad) * distance)
        is_valid = validate_move(x,y,position[0],position[1],self._state.speed_mps,environment,self._state.traversable_hazards)

        eps = 10 * pi/180

        while not is_valid:
            if eps > pi:
                # more of a fail state than anything else; hopefully we never hit this. basically just a way to get out if we haven't found a valid action
                return AgentAction(target_heading=target_heading, target_speed=0)

            new_headings = (angle_rad + eps, angle_rad - eps)
            position1 = (x + math.cos(new_headings[0]) * distance, y + math.sin(new_headings[0]) * distance)
            position2 = (x + math.cos(new_headings[1]) * distance, y + math.sin(new_headings[1]) * distance)
            is_valid1 = validate_move(x,y,position1[0],position1[1],self._state.speed_mps,environment,self._state.traversable_hazards)
            is_valid2 = validate_move(x,y,position2[0],position2[1],self._state.speed_mps,environment,self._state.traversable_hazards)

            if is_valid1:
                target_heading = math.degrees(new_headings[0]) % 360
                is_valid = True
                break
            elif is_valid2:
                target_heading = math.degrees(new_headings[1]) % 360
                is_valid = True
                break
            
            eps += eps
        
        return AgentAction(
            target_heading=target_heading, 
            target_speed=self._state.speed_mps
        )

    def update_state(self, new_state: AgentState) -> None:
        self._state = new_state

    def update_belief(self, sensor_data):
        pass
