import yaml
from typing import Any, Dict, List
from search_sim.simulator.definitions.schema import SimulatorConfig, SimulatorState, Timekeeper
from search_sim.agents.definitions.schema import AgentState, AgentType
from search_sim.targets.definitions.schema import TargetState, TargetType
from search_sim.agents.factories.agent_factory import agent_factory
from search_sim.targets.factories.target_factory import target_factory
from search_sim.world.environment import Environment
from search_sim.world.nodes.definitions.schema import ProbabilityNode
from search_sim.world.probability_map import ProbabilityMap

class SimulatorConfigParser:
    @staticmethod
    def load_yaml(file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
        
    def _generate_initial_map(self, belief_config: dict, world_config: dict) -> ProbabilityMap:
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

    def _parse_targets(self, target_configs: List[Dict[str, Any]]) -> List[Any]:
        targets = []
        for config in target_configs:
            state = TargetState(
                id=config["id"],
                x=float(config["x"]),
                y=float(config["y"]),
                type=TargetType(config["type"]),
                value=float(config.get("value", 1.0)),
                traversable_hazards=[],
                heading=float(config.get("heading", 0.0)),
                speed_mps=float(config.get("speed_mps", 0.0)),
                max_speed=float(config.get("max_speed", 1.0)),
                awareness_radius=float(config.get("awareness_radius", 0.0)),
                nearby_agents=[],
                nearby_targets=[],
                nearby_hazards=[]
            )
            targets.append(target_factory(TargetType(config["type"]), target_state=state))
        return targets

    def parse(self, file_path: str) -> tuple[SimulatorConfig, SimulatorState]:
        data = self.load_yaml(file_path)

        world_data = data.get("world", {})
        world_dimensions = {
            "x_length": float(world_data.get("x_length", 10.0)),
            "y_length": float(world_data.get("y_length", 10.0)),
            "num_x_pts": int(world_data.get("num_x_pts", 10)),
            "num_y_pts": int(world_data.get("num_y_pts", 10))
        }

        simulation_data = data.get("simulation", {})
        config = SimulatorConfig(
            time_limit_seconds=float(simulation_data.get("time_limit_seconds", 30.0)),
            step_time_seconds=float(simulation_data.get("step_time_seconds", 0.1))
        )

        agent_configs = data.get("agents", [])
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
            initial_map = self._generate_initial_map(belief_config, world_dimensions)

            agents.append(agent_factory(
                state.type, 
                initial_state=state, 
                initial_map=initial_map
            ))

        targets = self._parse_targets(data.get("targets", []))

        environment = Environment(
            entities=agents + targets,
            **world_dimensions
        )

        initial_state = SimulatorState(
            timekeeper=Timekeeper(time_step_seconds=config.step_time_seconds),
            environment=environment,
            agents=agents,
            targets=targets,
            hazards=[]
        )

        return config, initial_state