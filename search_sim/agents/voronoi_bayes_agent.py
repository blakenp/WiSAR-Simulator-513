from typing import List, Optional, Any
from search_sim.agents.definitions.schema import AgentAction, AgentState, SensorObservation
from search_sim.agents.definitions.interfaces import Agent
from search_sim.entities.interfaces import Entity
from search_sim.voronoi.scipy_voronoi_computer import ScipyVoronoiComputer
from search_sim.world.environment import Environment
from search_sim.world.probability_map import ProbabilityMap
from search_sim.utils import validate_move
import math
import random
import numpy as np
from dataclasses import replace

class VoronoiBayesAgent(Agent, Entity[AgentState]):
    def __init__(self, initial_agent_state: AgentState, initial_target_belief_map: ProbabilityMap, initial_hazard_belief_map: ProbabilityMap):
        self._state = initial_agent_state
        self.target_belief_map = initial_target_belief_map
        self.hazard_belief_map = initial_hazard_belief_map
        self.last_computed_ridges = []

    def get_id(self) -> str:
        return self._state.id

    def get_location(self) -> tuple[float, float]:
        return self._state.x, self._state.y

    def update_state(self, new_state: AgentState) -> None:
        self._state = new_state

    def update_belief(self, observations: Optional[List[SensorObservation]]) -> None:
        """Processes incoming sensor data to update the persistent hazard occupancy grid."""
        if observations:
            self.update_hazard_grid(observations)

    def get_desired_action(self, dt: float, environment: Optional[Environment]) -> AgentAction:
        """
        Calculates action by sampling a 'cloud' of possible Voronoi topologies
        based on the posterior distribution of obstacle locations.
        """
        hazard_cloud = self.sample_hazard_posterior(num_hazards=8, iterations=300, num_samples=10)
        
        all_ridges = []
        self.last_computed_ridges = []
        
        for hypothesized_hazards in hazard_cloud:
            voronoi_map = self.generate_voronoi_map(hypothesized_hazards)
            all_ridges.append(voronoi_map)
            
            sample_ridges = []
            for ridge_indices in voronoi_map.ridge_vertices:
                if -1 not in ridge_indices:
                    v1 = voronoi_map.vertices[ridge_indices[0]]
                    v2 = voronoi_map.vertices[ridge_indices[1]]
                    sample_ridges.append((v1, v2))
            self.last_computed_ridges.append(sample_ridges)
        
        target_x, target_y = self.target_belief_map.get_max_probability_location()
        best_heading = self.calculate_probabilistic_ridge_heading(all_ridges, (target_x, target_y))
        
        speed = self._state.speed_mps
        distance = speed * dt
        x, y = self._state.x, self._state.y
        
        angle_rad = math.radians(best_heading)
        next_x = x + math.cos(angle_rad) * distance
        next_y = y + math.sin(angle_rad) * distance
        
        is_valid = validate_move(x, y, next_x, next_y, speed, environment, self._state.traversable_hazards)
        
        eps = 5.0 * (math.pi / 180.0)
        while not is_valid:
            if eps > math.pi:
                return AgentAction(target_heading=best_heading, target_speed=0.0)

            for sign in [1, -1]:
                new_angle = angle_rad + (sign * eps)
                px = x + math.cos(new_angle) * distance
                py = y + math.sin(new_angle) * distance
                
                if validate_move(x, y, px, py, speed, environment, self._state.traversable_hazards):
                    return AgentAction(
                        target_heading=math.degrees(new_angle) % 360, 
                        target_speed=speed
                    )
            eps += (5.0 * math.pi / 180.0)
        
        return AgentAction(target_heading=best_heading, target_speed=speed)

    def sample_hazard_posterior(self, num_hazards: int, iterations: int, num_samples: int) -> List[np.ndarray]:
        """Runs Metropolis-Hastings and returns a list of sampled obstacle configurations."""
        samples = []
        current_h = self.initialize_hypotheses(num_hazards)
        current_log_post = self.get_unnormalized_posterior(current_h)
        step_size = 0.5
        
        for i in range(iterations):
            proposal_h = current_h + np.random.normal(0, step_size, current_h.shape)
            proposal_log_post = self.get_unnormalized_posterior(proposal_h)
            
            if np.log(random.random()) < (proposal_log_post - current_log_post):
                current_h = proposal_h
                current_log_post = proposal_log_post
            
            if i > 100 and i % (iterations // num_samples) == 0:
                samples.append(current_h.copy())
                
        return samples

    def get_unnormalized_posterior(self, hypothesized_hazards: np.ndarray) -> float:
        """Combines historical grid knowledge with current sensor evidence."""
        return self.get_prior_over_hazards(hypothesized_hazards) + \
               self.get_likelihood_over_hazards(hypothesized_hazards)

    def get_prior_over_hazards(self, hypothesized_hazards: np.ndarray) -> float:
        """Evaluates log-prior using the historical hazard_belief_map."""
        log_prior = 0.0
        for point in hypothesized_hazards:
            node = self.hazard_belief_map.get_node((point[0], point[1]))
            prob = node.get_node_data().probability
            log_prior += math.log(prob + 1e-9)
        return log_prior

    def get_likelihood_over_hazards(self, hypothesized_hazards: np.ndarray) -> float:
        """Evaluates how well hypothesized points explain the most recent sensor hits."""
        log_likelihood = 0.0
        readings = self._state.recent_sensor_readings
        if not readings:
            return 0.0

        for obs in readings:
            abs_bearing = math.radians((self._state.heading + obs.bearing) % 360)
            hit_x = self._state.x + math.cos(abs_bearing) * obs.distance
            hit_y = self._state.y + math.sin(abs_bearing) * obs.distance
            hit_point = np.array([hit_x, hit_y])

            distances = np.linalg.norm(hypothesized_hazards - hit_point, axis=1)
            min_dist = np.min(distances)
            log_likelihood += -0.5 * (min_dist / obs.noise_sigma)**2

        return log_likelihood

    def initialize_hypotheses(self, num_hazards: int) -> np.ndarray:
        """Weighted sampling from the occupancy grid to seed MCMC chains."""
        probs = []
        coords = []
        for y in range(self.hazard_belief_map.num_y_pts):
            for x in range(self.hazard_belief_map.num_x_pts):
                node = self.hazard_belief_map.grid[y][x]
                probs.append(node.get_node_data().probability)
                coords.append(((x + 0.5) * self.hazard_belief_map.x_size, 
                               (y + 0.5) * self.hazard_belief_map.y_size))

        normalized_probs = np.array(probs) / (np.sum(probs) + 1e-9)
        chosen_indices = np.random.choice(len(coords), size=num_hazards, p=normalized_probs)

        return np.array([np.array(coords[idx]) + np.random.uniform(-0.1, 0.1, 2) for idx in chosen_indices])

    def update_hazard_grid(self, observations: List[SensorObservation]) -> None:
        """Inverse Sensor Model logic for Recursive Bayesian Updating."""
        P_OCC, P_FREE = 0.7, 0.3
        for obs in observations:
            abs_bearing = math.radians((self._state.heading + obs.bearing) % 360)
            hit_x = self._state.x + math.cos(abs_bearing) * obs.distance
            hit_y = self._state.y + math.sin(abs_bearing) * obs.distance
            
            if obs.distance < self._state.sensor_range:
                self.apply_bayesian_update((hit_x, hit_y), P_OCC)

            step_size = 0.5
            num_steps = int(obs.distance / step_size)
            for i in range(num_steps):
                cx = self._state.x + math.cos(abs_bearing) * (i * step_size)
                cy = self._state.y + math.sin(abs_bearing) * (i * step_size)
                if np.linalg.norm([cx - hit_x, cy - hit_y]) < step_size:
                    break
                self.apply_bayesian_update((cx, cy), P_FREE)

    def apply_bayesian_update(self, coords: tuple[float, float], p_z: float) -> None:
        """Updates a single cell's probability using log-odds notation."""
        node = self.hazard_belief_map.get_node(coords)
        curr_data = node.get_node_data()
        
        curr_p = curr_data.probability
        l_prev = math.log(curr_p / (1.0 - curr_p + 1e-9))
        l_sensor = math.log(p_z / (1.0 - p_z + 1e-9))
        l_new = l_prev + l_sensor 
        p_new = 1.0 / (1.0 + math.exp(-l_new))
        clamped_p = max(0.01, min(0.99, p_new))

        new_data = replace(curr_data, probability=clamped_p)
        node.update_node_data(new_data)

    def calculate_probabilistic_ridge_heading(self, ridge_cloud: List[Any], target_pos: tuple[float, float]) -> float:
        """Identifies the heading with the highest expected safety and goal alignment."""
        possible_headings = np.linspace(0, 360, num=36, endpoint=False)
        heading_scores = []

        for heading in possible_headings:
            safety_votes = sum(1 for voronoi in ridge_cloud if self.is_heading_on_ridge(heading, voronoi))
            alignment = self.get_goal_alignment(heading, target_pos)
            heading_scores.append(safety_votes * alignment)

        return possible_headings[np.argmax(heading_scores)]

    def is_heading_on_ridge(self, heading: float, voronoi: Any, tolerance_deg: float = 15.0) -> bool:
        """Checks if a heading aligns with any valid ridge in the Scipy Voronoi object."""
        for ridge_indices in voronoi.ridge_vertices:
            if -1 in ridge_indices:
                continue
                
            v1 = voronoi.vertices[ridge_indices[0]]
            v2 = voronoi.vertices[ridge_indices[1]]
            
            ridge_vec = v2 - v1
            ridge_angle = math.degrees(math.atan2(ridge_vec[1], ridge_vec[0])) % 360
            
            if abs(heading - ridge_angle) < tolerance_deg or \
            abs(heading - (ridge_angle + 180) % 360) < tolerance_deg:
                return True
                
        return False

    def get_goal_alignment(self, heading: float, target_pos: tuple[float, float]) -> float:
        """Returns a normalized score based on how close heading is to the goal vector."""
        dy, dx = target_pos[1] - self._state.y, target_pos[0] - self._state.x
        goal_angle = math.degrees(math.atan2(dy, dx)) % 360
        diff = abs(heading - goal_angle)
        if diff > 180: diff = 360 - diff
        return max(0, 1 - (diff / 180.0))

    def generate_voronoi_map(self, hypothesized_hazards: np.ndarray):
        """Wraps the Scipy construction of the Voronoi graph."""
        voronoi_computer = ScipyVoronoiComputer(hypothesized_hazards)
        return voronoi_computer.compute_voronoi()