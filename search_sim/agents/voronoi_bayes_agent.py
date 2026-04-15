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
    def __init__(
        self,
        initial_agent_state: AgentState,
        initial_target_belief_map: ProbabilityMap,
        initial_hazard_belief_map: ProbabilityMap,
    ):
        self._state = initial_agent_state
        self.target_belief_map = initial_target_belief_map
        self.hazard_belief_map = initial_hazard_belief_map
        self.last_computed_ridges = []

        self._smoothing_alpha = 0.35
        self._current_best_heading = initial_agent_state.heading

        self._last_pos = (initial_agent_state.x, initial_agent_state.y)
        self._stuck_counter = 0
        self._direct_blocked_count = 0
        self._blocked_headings: List[float] = []
        self._escape_heading: Optional[float] = None
        self._escape_steps = 0

    def get_id(self) -> str:
        return self._state.id

    def get_location(self) -> tuple[float, float]:
        return self._state.x, self._state.y

    def update_state(self, new_state: AgentState) -> None:
        self._state = new_state

    def update_belief(self, observations: Optional[List[SensorObservation]]) -> None:
        if observations:
            self.update_hazard_grid(observations)

    def get_desired_action(self, dt: float, environment: Optional[Environment]) -> AgentAction:
        """
        Calculates action by sampling a 'cloud' of possible Voronoi topologies
        based on the posterior distribution of obstacle locations.
        """
        x, y = self._state.x, self._state.y

        moved = math.hypot(x - self._last_pos[0], y - self._last_pos[1])
        if moved < 0.05:
            self._stuck_counter += 1
        else:
            self._stuck_counter = 0
            self._blocked_headings = []
        self._last_pos = (x, y)

        if self._escape_steps > 0:
            self._escape_steps -= 1
            angle_rad = math.radians(self._escape_heading)
            dist = self._state.speed_mps * dt
            nx = x + math.cos(angle_rad) * dist
            ny = y + math.sin(angle_rad) * dist
            if validate_move(x, y, nx, ny, self._state.speed_mps, environment, self._state.traversable_hazards):
                return AgentAction(target_heading=self._escape_heading, target_speed=self._state.speed_mps * 0.85)
            self._escape_steps = 0

        hazard_cloud = self.sample_hazard_posterior(num_hazards=10, iterations=350, num_samples=12)

        all_voronoi_maps = []
        self.last_computed_ridges = []
        for hypothesized_hazards in hazard_cloud:
            jitter = np.random.normal(0, 1e-6, hypothesized_hazards.shape)
            vor = self.generate_voronoi_map(hypothesized_hazards + jitter)
            all_voronoi_maps.append(vor)
            ridges = [
                (vor.vertices[ri[0]], vor.vertices[ri[1]])
                for ri in vor.ridge_vertices if -1 not in ri
            ]
            self.last_computed_ridges.append(ridges)

        target_pos = self.target_belief_map.get_max_probability_location()

        stuck_threshold = 2 if self._direct_blocked_count >= 5 else 4
        if self._stuck_counter >= stuck_threshold:
            escape = self._find_ridge_escape_heading(all_voronoi_maps, environment, dt)
            if escape is not None:
                self._escape_heading = escape
                self._escape_steps = 14
                self._stuck_counter = 0
                self._direct_blocked_count = 0
                return AgentAction(target_heading=escape, target_speed=self._state.speed_mps * 0.9)

        raw_heading = self.calculate_topological_heading(all_voronoi_maps, target_pos)

        diff = (raw_heading - self._current_best_heading + 180) % 360 - 180
        self._current_best_heading = (self._current_best_heading + self._smoothing_alpha * diff) % 360

        speed = self._state.speed_mps
        angle_rad = math.radians(self._current_best_heading)
        dist = speed * dt
        next_x = x + math.cos(angle_rad) * dist
        next_y = y + math.sin(angle_rad) * dist

        real_env_valid = validate_move(x, y, next_x, next_y, speed, environment, self._state.traversable_hazards)

        if not real_env_valid:
            self._direct_blocked_count += 1
            self._blocked_headings.append(self._current_best_heading)
            fallback = self._ranked_fallback_heading(environment, dt)
            self._current_best_heading = fallback
            return AgentAction(target_heading=fallback, target_speed=speed * 0.3)

        self._direct_blocked_count = 0
        return AgentAction(target_heading=self._current_best_heading, target_speed=speed)

    def calculate_topological_heading(
        self, voronoi_cloud: List[Any], target_pos: tuple[float, float]
    ) -> float:
        agent_pos = np.array([self._state.x, self._state.y])
        target_arr = np.array(target_pos)
        d_agent_goal = float(np.linalg.norm(agent_pos - target_arr))

        possible_headings = np.linspace(0, 360, num=72, endpoint=False)
        heading_scores = np.zeros(len(possible_headings))

        RIDGE_RADIUS = 5.0
        HAZARD_RADIUS = 5.0

        nearby_ridges: List[tuple] = []
        for vor in voronoi_cloud:
            for r_idx in vor.ridge_vertices:
                if -1 in r_idx:
                    continue
                v1 = vor.vertices[r_idx[0]]
                v2 = vor.vertices[r_idx[1]]
                seg_vec = v2 - v1
                seg_len_sq = float(np.dot(seg_vec, seg_vec))
                if seg_len_sq < 1e-4:
                    continue
                t = float(np.clip(np.dot(agent_pos - v1, seg_vec) / seg_len_sq, 0.0, 1.0))
                closest = v1 + t * seg_vec
                d = float(np.linalg.norm(agent_pos - closest))
                if d <= RIDGE_RADIUS:
                    nearby_ridges.append((v1.copy(), v2.copy(), d))

        nearby_hazards: List[tuple] = []
        for vor in voronoi_cloud:
            for pt in vor.points:
                d = float(np.linalg.norm(agent_pos - pt))
                if d < HAZARD_RADIUS:
                    nearby_hazards.append((pt.copy(), d))

        for i, heading in enumerate(possible_headings):
            heading_rad = math.radians(heading)
            move_dir = np.array([math.cos(heading_rad), math.sin(heading_rad)])

            ridge_score = 0.0
            for v1, v2, d_ridge in nearby_ridges:
                seg_vec = v2 - v1
                seg_len = float(np.linalg.norm(seg_vec))
                if seg_len < 0.1:
                    continue
                seg_dir = seg_vec / seg_len

                proximity = math.exp(-0.55 * d_ridge)
                for sign, far_endpoint in [(1.0, v2), (-1.0, v1)]:
                    dir_vec = sign * seg_dir
                    align = float(np.dot(move_dir, dir_vec))
                    if align <= 0.0:
                        continue

                    d_end_goal = float(np.linalg.norm(far_endpoint - target_arr))
                    raw_progress = (d_agent_goal - d_end_goal) / (d_agent_goal + 1.0)
                    goal_factor = max(0.4, 1.0 + raw_progress)

                    ridge_score += align * proximity * goal_factor

            repulsion_score = 0.0
            for hz_pos, d_hz in nearby_hazards:
                away = agent_pos - hz_pos
                away_norm = away / (float(np.linalg.norm(away)) + 1e-9)
                repulsion_score += float(np.dot(move_dir, away_norm)) / (d_hz + 0.5)
            if nearby_hazards:
                repulsion_score /= len(nearby_hazards)

            if d_agent_goal > 0.1:
                goal_dir = (target_arr - agent_pos) / d_agent_goal
                goal_score = float(np.dot(move_dir, goal_dir))
            else:
                goal_score = 0.0

            if nearby_ridges:
                heading_scores[i] = (
                    ridge_score   * 0.70
                    + repulsion_score * 0.20
                    + goal_score  * 0.10
                )
            else:
                heading_scores[i] = repulsion_score * 0.50 + goal_score * 0.50

        smoothed = np.convolve(heading_scores, [0.1, 0.2, 0.4, 0.2, 0.1], mode='same')
        if np.max(smoothed) > 0:
            return possible_headings[np.argmax(smoothed)]
        
        return self._current_best_heading

    def _find_ridge_escape_heading(
        self,
        voronoi_cloud: List[Any],
        environment: Optional[Environment],
        dt: float,
    ) -> Optional[float]:
        """
        Collect Voronoi ridge midpoints within a generous radius (12 m) and
        return the heading toward the best reachable one.

        Scoring favours:
        - Midpoints close to the agent (to escape quickly)
        - Midpoints that reduce distance to target (bypass midpoints naturally
          wrap around the obstacle so their distance to goal is shorter)
        - Headings not in the recently-failed set
        """
        agent_pos = np.array([self._state.x, self._state.y])
        target_pos = np.array(self.target_belief_map.get_max_probability_location())
        d_agent_goal = float(np.linalg.norm(agent_pos - target_pos))
        x, y = self._state.x, self._state.y
        speed = self._state.speed_mps
        dist = speed * dt

        candidates: List[tuple] = []
        for vor in voronoi_cloud:
            for r_idx in vor.ridge_vertices:
                if -1 in r_idx:
                    continue
                v1, v2 = vor.vertices[r_idx[0]], vor.vertices[r_idx[1]]
                mid = (v1 + v2) / 2.0
                d_agent = float(np.linalg.norm(agent_pos - mid))
                if d_agent > 12.0:
                    continue
                d_goal = float(np.linalg.norm(mid - target_pos))
                progress_bonus = max(0.0, d_agent_goal - d_goal) * 0.3
                score = d_agent - progress_bonus
                candidates.append((score, mid))

        if not candidates:
            return None

        candidates.sort(key=lambda t: t[0])

        for _, mid in candidates[:12]:
            dy = float(mid[1]) - y
            dx = float(mid[0]) - x
            heading = math.degrees(math.atan2(dy, dx)) % 360
            if any(abs((heading - bh + 180) % 360 - 180) < 15 for bh in self._blocked_headings):
                continue
            angle_rad = math.radians(heading)
            nx = x + math.cos(angle_rad) * dist
            ny = y + math.sin(angle_rad) * dist
            if validate_move(x, y, nx, ny, speed, environment, self._state.traversable_hazards):
                return heading

        return None

    def _ranked_fallback_heading(self, environment: Optional[Environment], dt: float) -> float:
        x, y = self._state.x, self._state.y
        speed = self._state.speed_mps
        dist = speed * dt

        for offset in [20, -20, 45, -45, 90, -90, 135, -135, 180]:
            h = (self._current_best_heading + offset) % 360

            if any(abs((h - bh + 180) % 360 - 180) < 10 for bh in self._blocked_headings[-6:]):
                continue

            angle_rad = math.radians(h)
            nx = x + math.cos(angle_rad) * dist
            ny = y + math.sin(angle_rad) * dist

            if validate_move(x, y, nx, ny, speed, environment, self._state.traversable_hazards):
                return h
            
        return (self._current_best_heading + 20) % 360

    def sample_hazard_posterior(
        self, num_hazards: int, iterations: int, num_samples: int
    ) -> List[np.ndarray]:
        samples = []
        current_h = self.initialize_hypotheses(num_hazards)
        current_log_post = self.get_unnormalized_posterior(current_h)
        thinning = max(1, (iterations - 100) // num_samples)

        for i in range(iterations):
            proposal_h = current_h + np.random.normal(0, 0.5, current_h.shape)
            proposal_log_post = self.get_unnormalized_posterior(proposal_h)
            if np.log(random.random() + 1e-300) < (proposal_log_post - current_log_post):
                current_h, current_log_post = proposal_h, proposal_log_post
            if i > 100 and (i - 101) % thinning == 0 and len(samples) < num_samples:
                samples.append(current_h.copy())

        return samples

    def get_unnormalized_posterior(self, hypothesized_hazards: np.ndarray) -> float:
        return self.get_prior_over_hazards(hypothesized_hazards) + self.get_likelihood_over_hazards(hypothesized_hazards)

    def get_prior_over_hazards(self, hypothesized_hazards: np.ndarray) -> float:
        log_prior = 0.0

        for point in hypothesized_hazards:
            node = self.hazard_belief_map.get_node((point[0], point[1]))
            log_prior += math.log(node.get_node_data().probability + 1e-9)

        return log_prior

    def get_likelihood_over_hazards(self, hypothesized_hazards: np.ndarray) -> float:
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
            log_likelihood += -0.5 * (float(np.min(distances)) / obs.noise_sigma) ** 2

        return log_likelihood

    def initialize_hypotheses(self, num_hazards: int) -> np.ndarray:
        probs, coords = [], []
        for gy in range(self.hazard_belief_map.num_y_pts):
            for gx in range(self.hazard_belief_map.num_x_pts):
                node = self.hazard_belief_map.grid[gy][gx]
                probs.append(node.get_node_data().probability)
                coords.append((
                    (gx + 0.5) * self.hazard_belief_map.x_size,
                    (gy + 0.5) * self.hazard_belief_map.y_size,
                ))

        total = sum(probs) + 1e-9
        idx = np.random.choice(len(coords), size=num_hazards, p=np.array(probs) / total)

        return np.array([
            np.array(coords[i]) + np.random.uniform(-0.1, 0.1, 2) for i in idx
        ])

    def update_hazard_grid(self, observations: List[SensorObservation]) -> None:
        P_OCC, P_FREE = 0.7, 0.3
        for obs in observations:
            abs_bearing = math.radians((self._state.heading + obs.bearing) % 360)
            hit_x = self._state.x + math.cos(abs_bearing) * obs.distance
            hit_y = self._state.y + math.sin(abs_bearing) * obs.distance

            if obs.distance < self._state.sensor_range:
                self.apply_bayesian_update((hit_x, hit_y), P_OCC)

            step_size = 0.5
            num_steps = int(obs.distance / step_size)
            for k in range(num_steps):
                cx = self._state.x + math.cos(abs_bearing) * (k * step_size)
                cy = self._state.y + math.sin(abs_bearing) * (k * step_size)

                if math.hypot(cx - hit_x, cy - hit_y) < step_size:
                    break

                self.apply_bayesian_update((cx, cy), P_FREE)

    def apply_bayesian_update(self, coords: tuple[float, float], p_z: float) -> None:
        node = self.hazard_belief_map.get_node(coords)
        curr_p = node.get_node_data().probability
        l_prev = math.log(curr_p / (1.0 - curr_p + 1e-9))
        l_sensor = math.log(p_z / (1.0 - p_z + 1e-9))
        p_new = 1.0 / (1.0 + math.exp(-(l_prev + l_sensor)))

        node.update_node_data(
            replace(node.get_node_data(), probability=max(0.01, min(0.99, p_new)))
        )

    def generate_voronoi_map(self, hypothesized_hazards: np.ndarray):
        return ScipyVoronoiComputer(hypothesized_hazards).compute_voronoi()
    