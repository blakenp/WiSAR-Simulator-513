from abc import ABC, abstractmethod
from search_sim.agents.definitions.dataclasses import AgentAction

class Agent(ABC):
    @abstractmethod
    def get_id(self) -> str:
        pass

    @abstractmethod
    def get_location(self) -> tuple[float, float]:
        pass

    @abstractmethod
    def get_desired_action(self) -> AgentAction:
        pass