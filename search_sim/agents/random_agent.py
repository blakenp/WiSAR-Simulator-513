"""Base agent class and state definitions."""

from search_sim.agents.definitions.schema import AgentAction, AgentState
from search_sim.agents.definitions.interfaces import Agent
from search_sim.entities.interfaces import Entity

# TODO: Implement methods and constructor once we know what we want this to do
class RandomAgent(Agent, Entity[AgentState]):
    def __init__(self):
        pass

    def get_id(self) -> str:
        pass

    def get_location(self) -> tuple[float, float]:
        pass

    def get_desired_action(self) -> AgentAction:
        pass

    def update_state(self, new_state: AgentState) -> None:
        pass

    def update_belief(self, sensor_data):
        pass