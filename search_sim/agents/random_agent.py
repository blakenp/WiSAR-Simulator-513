"""Base agent class and state definitions."""

from search_sim.agents.definitions.dataclasses import AgentAction
from search_sim.agents.definitions.interfaces import Agent

# TODO: Implement methods and constructor once we know what we want this to do
class RandomAgent(Agent):
    def __init__(self):
        pass

    def get_id(self) -> str:
        pass

    def get_location(self) -> tuple[float, float]:
        pass

    def get_desired_action(self) -> AgentAction:
        pass