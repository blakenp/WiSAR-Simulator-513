from search_sim.targets.definitions import Target
from search_sim.agents.definitions import Agent
from search_sim.world.nodes.definitions.schema import EnvironmentNode
from search_sim.world.nodes.definitions.interfaces import Node
from typing import Optional

"""Basic node class to keep track of entities in the environment"""

class EnvironmentGridNode(Node[EnvironmentNode]):
    def __init__(self, population: Optional[set] = None) -> None:
        self._data = EnvironmentNode(population=population or set())

    # methods to check for specific entity types
    def has_target(self) -> bool:
        has_target = False

        for entity in self._data.population:
            if type(entity) == Target:
                has_target = True
        
        return has_target
    
    def has_agent(self) -> bool:
        has_agent = False

        for entity in self.get_population():
            if type(entity) == Agent:
                has_agent = True
        
        return has_agent
    
    def has_hazard(self) -> bool:
        has_hazard = False

        # for entity in self._data.population:  # uncomment this section when Hazards are implemented
        #     if type(entity) == Hazard:
        #         has_hazard = True

        return has_hazard
    
    # basic getter and setter methods    
    def get_node_data(self) -> EnvironmentNode:
        return self._data

    def update_node_data(self, new_node_data: EnvironmentNode) -> None:
        self._data = new_node_data