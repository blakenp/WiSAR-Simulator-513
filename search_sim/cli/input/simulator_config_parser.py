import yaml
from typing import Any, Dict
from search_sim.cli.input.simulator_builder import SimulatorBuilder
from search_sim.simulator.definitions.schema import SimulatorConfig, SimulatorState

class SimulatorConfigParser:
    def __init__(self, config_builder: SimulatorBuilder):
        self._config_builder = config_builder

    @staticmethod
    def load_yaml(file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)

    def parse(self, file_path: str) -> tuple[SimulatorConfig, SimulatorState]:
        data = self.load_yaml(file_path)

        world_config = data.get("world", {})
        simulation_config = data.get("simulation", {})
        agent_configs = data.get("agents", [])
        target_configs = data.get("targets", [])
        hazard_configs = data.get("hazards", [])

        agents = self._config_builder.build_agents(agent_configs, world_config)
        targets = self._config_builder.build_targets(target_configs)
        hazards = self._config_builder.build_hazards(hazard_configs)

        environment = self._config_builder.build_environment(agents, targets, hazards, world_config)
        simulator_config = self._config_builder.build_simulator_config(simulation_config)

        initial_state = self._config_builder.build_simulator_state(
            simulator_config=simulator_config,
            environment=environment,
            agents=agents,
            targets=targets,
            hazards=hazards
        )

        return simulator_config, initial_state