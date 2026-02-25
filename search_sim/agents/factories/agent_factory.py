from search_sim.agents.random_agent import RandomAgent
from search_sim.agents.definitions.interfaces import Agent
from search_sim.agents.definitions.types import AgentType
from typing import Optional

def agent_factory(agent_type: AgentType) -> Optional[Agent]:
    match agent_type:
        case AgentType.RANDOM_AGENT:
            return RandomAgent()
        case _:
            raise ValueError(f"Unknown Agent Type: {agent_type}")
            return None