from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class EnvironmentNode:
    """A node in the environment class's grid.

    Attributes:
        population: A set of all entities currently in this node.
    """
    population: set
    
@dataclass(frozen=True)
class ProbabilityNode:
    """The probability of the target being in a given node. Used in probability maps.
    
    Attributes:
        probability: The probability of the target being in this node.
    """
    probability: np.float64