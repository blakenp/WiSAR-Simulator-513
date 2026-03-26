from typing import Any, Dict, List

from search_sim.agents.definitions.interfaces import Agent
from search_sim.agents.definitions.schema import AgentState, AgentType
from search_sim.agents.factories.agent_factory import agent_factory
from search_sim.hazards.definitions.interfaces import Hazard
from search_sim.hazards.definitions.schema import HazardState, HazardType
from search_sim.hazards.factories import hazard_factory
from search_sim.simulator.definitions.schema import SimulatorConfig, SimulatorState, Timekeeper
from search_sim.targets.definitions.interfaces import Target
from search_sim.targets.definitions.schema import TargetState, TargetType
from search_sim.targets.factories import target_factory
from search_sim.world.environment import Environment
from search_sim.world.nodes.definitions.schema import ProbabilityNode
from search_sim.world.probability_map import ProbabilityMap


class SimulatorBuilder:
    def __init__(self):
        pass

    def generate_agent_initial_belief_map(self, belief_config: dict, world_config: dict) -> ProbabilityMap:
        probability_map = ProbabilityMap(
            x_length=world_config['x_length'],
            y_length=world_config['y_length'],
            num_x_pts=world_config['num_x_pts'],
            num_y_pts=world_config['num_y_pts']
        )
        
        distribution_type = belief_config.get("type", "uniform")

        if distribution_type == "point":
            target_coordinates = (float(belief_config["target_x"]), float(belief_config["target_y"]))
            node = probability_map.get_node(target_coordinates)
            node.update_node_data(ProbabilityNode(probability=1.0))
            
        return probability_map
    
    def build_agents(self, agent_configs: List[Dict[str, Any]], world_config: dict) -> List[Agent]:
        agents = []
        for agent_config in agent_configs:
            state = AgentState(
                id=agent_config["id"],
                type=AgentType(agent_config["type"]),
                x=float(agent_config["x"]),
                y=float(agent_config["y"]),
                heading=float(agent_config.get("heading", 0.0)),
                battery_percent=float(agent_config.get("battery_percent", 100.0)),
                speed_mps=float(agent_config.get("speed_mps", 0.0)),
                is_active=bool(agent_config.get("is_active", True))
            )

            belief_config = agent_config.get("belief", {"type": "uniform"})
            initial_map = self.generate_agent_initial_belief_map(belief_config, world_config)

            agents.append(agent_factory(state.type, initial_state=state, initial_map=initial_map))

        return agents 
    
    def build_targets(self, target_configs: List[Dict[str, Any]]) -> List[Target]:
        targets = []
        for target_config in target_configs:
            traversable_strings = target_config.get("traversable_hazards", [])
            traversable_enums = [HazardType(hazard_string) for hazard_string in traversable_strings]

            state = TargetState(
                id=target_config["id"],
                x=float(target_config["x"]),
                y=float(target_config["y"]),
                type=TargetType(target_config["type"]),
                value=float(target_config.get("value", 1.0)),
                traversable_hazards=traversable_enums,
                heading=float(target_config.get("heading", 0.0)),
                speed_mps=float(target_config.get("speed_mps", 0.0)),
                max_speed=float(target_config.get("max_speed", 1.0)),
                awareness_radius=float(target_config.get("awareness_radius", 0.0)),
                nearby_agents=[],
                nearby_targets=[],
                nearby_hazards=[]
            )
            
            targets.append(target_factory(state.type, target_state=state))

        return targets
    
    def build_hazards(self, hazard_configs: dict) -> List[Hazard]:
        hazards = []
        for hazard_config in hazard_configs:
            state = HazardState(
                id=hazard_config["id"],
                x=float(hazard_config["x"]),
                y=float(hazard_config["y"]),
                type=HazardType(hazard_config["type"])
            )
            hazards.append(hazard_factory(state.type, hazard_state=state))

        return hazards

    def build_environment(self, agents: List[Agent], targets: List[Target], world_config: dict) -> Environment:
        return Environment(
            entities=agents + targets,
            x_length=world_config['x_length'],
            y_length=world_config['y_length'],
            num_x_pts=world_config['num_x_pts'],
            num_y_pts=world_config['num_y_pts']
        )   
    
    def build_simulator_config(self, simulation_data: dict) -> SimulatorConfig:
        return SimulatorConfig(
            time_limit_seconds=float(simulation_data.get("time_limit_seconds", 30.0)),
            step_time_seconds=float(simulation_data.get("step_time_seconds", 0.1))
        )
    
    def build_simulator_state(self, 
        simulator_config: SimulatorConfig, 
        environment: Environment, 
        agents: List[Agent], 
        targets: List[Target],
        hazards: List[Hazard]
    ) -> SimulatorState:
        return SimulatorState(
            timekeeper=Timekeeper(time_step_seconds=simulator_config.step_time_seconds),
            environment=environment,
            agents=agents,
            targets=targets,
            hazards=hazards
        )

