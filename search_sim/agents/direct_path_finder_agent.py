"""Base agent class and state definitions."""

from search_sim.agents.definitions.schema import AgentAction, AgentState
from search_sim.agents.definitions.interfaces import Agent
from search_sim.entities.interfaces import Entity
from search_sim.world.probability_map import ProbabilityMap
import math

class DirectPathFinderAgent(Agent, Entity[AgentState]):
    def __init__(self, initial_agent_state: AgentState, initial_map: ProbabilityMap):
        self._state = initial_agent_state
        self.belief_map = initial_map

    def get_id(self) -> str:
        return self._state.id

    def get_location(self) -> tuple[float, float]:
        return self._state.x, self._state.y

    def get_desired_action(self) -> AgentAction:
        goal_x, goal_y = self.belief_map.get_max_probability_location()
        
        dx = goal_x - self._state.x
        dy = goal_y - self._state.y
        
        # atan2 returns radians, we convert to degrees 0-360
        angle_rad = math.atan2(dy, dx)
        target_heading = math.degrees(angle_rad) % 360
        
        return AgentAction(
            target_heading=target_heading, 
            target_speed=self._state.speed_mps
        )

    def update_state(self, new_state: AgentState) -> None:
        self._state = new_state

    def update_belief(self, sensor_data):
        pass
