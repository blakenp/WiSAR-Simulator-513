from search_sim.world.nodes.definitions.schema import ProbabilityNode
from search_sim.world.nodes.definitions.interfaces import Node
import numpy as np

"""Basic probability node class to keep track of probabilities of finding targets in the environment"""

class ProbabilityMapNode(Node[ProbabilityNode]):
    def __init__(self, probability: np.float64) -> None:
        self._data = ProbabilityNode(probability=probability)
    
    def get_node_data(self):
        return self._data

    def update_node_data(self, new_node_data: ProbabilityNode):
        self._data = new_node_data