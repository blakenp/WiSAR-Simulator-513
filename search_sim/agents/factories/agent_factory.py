from search_sim.agents.random_agent import RandomAgent
from search_sim.agents.direct_path_finder_agent import DirectPathFinderAgent
from search_sim.agents.definitions.interfaces import Agent
from search_sim.agents.definitions.schema import AgentState, AgentType
from search_sim.world.probability_map import ProbabilityMap
from typing import Optional

def agent_factory(
    agent_type: AgentType, 
    initial_state: AgentState, 
    initial_map: Optional[ProbabilityMap] = None
) -> Agent:
    if initial_state is None:
        raise ValueError("Initial state must be provided")
    
    if initial_map is None:
        raise ValueError("All agents requires an initial ProbabilityMap")

    match agent_type:
        case AgentType.RANDOM_AGENT:
            return RandomAgent(initial_state)
        case AgentType.DIRECT_PATH_FINDER_AGENT:
            return DirectPathFinderAgent(initial_state, initial_map)
        case _:
            raise ValueError(f"Unknown Agent Type: {agent_type}")