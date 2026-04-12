from abc import abstractmethod
from typing import Any, List, Optional
from search_sim.entities.interfaces import Entity
from search_sim.agents.definitions.schema import AgentAction, AgentState, SensorObservation

class Agent(Entity[AgentState]):
    @abstractmethod
    def get_desired_action(self, dt: float, environment: Optional[Any]) -> AgentAction:
        """The agent's decision-making method, which outputs the next most desirable action to be taken."""
        pass

    @abstractmethod
    def update_belief(self, sensor_data: Optional[List[SensorObservation]]) -> None:
        """Updates internal belief (e.g., probability maps) based on observations."""
        pass