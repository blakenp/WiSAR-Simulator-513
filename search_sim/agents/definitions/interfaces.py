from abc import abstractmethod
from typing import Any
from search_sim.entities.interfaces import Entity
from search_sim.agents.definitions.schema import AgentAction, AgentState

class Agent(Entity[AgentState]):
    @abstractmethod
    def get_desired_action(self, dt: float, environment) -> AgentAction:
        """The agent's decision-making method, which outputs the next most desirable action to be taken."""
        pass

    @abstractmethod
    def update_belief(self, sensor_data: Any) -> None: # TODO: Define the type of sensor data
        """The 'learning' method for the agent, which updates the agent's belief state based on new sensor data."""
        pass