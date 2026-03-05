from abc import abstractmethod
from search_sim.entities.interfaces import Entity
from search_sim.agents.definitions.dataclasses import AgentAction

class Agent(Entity):
    @abstractmethod
    def get_desired_action(self) -> AgentAction:
        pass