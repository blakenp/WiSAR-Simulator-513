"""Target which attempts to avoid the agent(s) by hiding in hazards."""

from search_sim.entities.interfaces import Entity
from search_sim.targets.definitions.interfaces import Target
from search_sim.targets.definitions.schema import TargetState, TargetAction
from search_sim.utils import compute_distance, compute_heading, sample_angles, sample_speeds, argmax
from math import radians, cos, sin, degrees

class EvasiveTarget(Target, Entity[TargetState]):
    def __init__(self, state: TargetState):
        self._state = state



    def get_id(self) -> str:
        return self._state.id
    


    def get_location(self) -> tuple[float,float]:
        return self._state.x, self._state.y



    def get_value(self) -> float:
        return self._state.value
    


    def get_desired_action(self, dt: float):
        """Identify directions to study more carefully."""
        x = self._state.x
        y = self._state.y
        entity_directions = []

        # pinpoint nearby agents and hazards
        for agent_state in self._state.nearby_agent_states:
            new_x = agent_state.x
            new_y = agent_state.y
            entity_directions.append(compute_heading(x,new_x,y,new_y))

        for hazard_state in self._state.nearby_hazard_states:
            new_x = hazard_state.x
            new_y = hazard_state.y
            entity_directions.append(compute_heading(x,new_x,y,new_y))
        
        n_directions = 16 + len(entity_directions)*4  # sample more angles if there are more things near the target

        candidate_actions = self.get_candidate_actions(self._state,n_angles=n_directions,preferred_angles=entity_directions)

        """Translate (speed,angle) pairs into (x,y) coordinates for scoring."""
        positions = []

        for action in candidate_actions:
            # rad = radians(action[0]) # sample_angles should be returning radians already
            distance = action[1] * dt
            positions.append((x + cos(action[0]) * distance, y + sin(action[0]) * distance))

        """Score potential new positions"""
        scores = []

        for position in positions:
            scores.append(self.score_move(position[0],position[1],self._state.nearby_agent_states,self._state.nearby_hazard_states))

        action = candidate_actions[argmax(scores)]
        
        return TargetAction(degrees(action[0]),action[1])



    def get_candidate_actions(self, state, n_angles=16, n_speeds=3, preferred_angles=None):
        """
        Returns a list of (angle, speed) pairs to be scored.
        """
        actions = []
        
        for angle in sample_angles(n_angles, preferred_angles):
            for speed in sample_speeds(state.max_speed, n_speeds):
                actions.append((angle, speed))
        
        return actions


    
    def score_move(self, x, y, agent_states, hazard_states):
        """Define scoring weights"""
        EVASION_WEIGHT = 0.5
        HAZARD_WEIGHT = 0.5

        """Add contributions to the score from each agent/hazard in the neighborhood"""
        score = 0.

        # Reward evasion (penalize proximity to agents)
        for agent_state in agent_states:
            agent_x = agent_state.x
            agent_y = agent_state.y
            distance = compute_distance(x,agent_x,y,agent_y)
            score -= EVASION_WEIGHT * (1 / (distance + 1e-6))
        
        # Reward movement towards hazards
        for hazard_state in hazard_states:
            hazard_x = hazard_state.x
            hazard_y = hazard_state.y
            distance = compute_distance(x,hazard_x,y,hazard_y)
            score += HAZARD_WEIGHT * (1 / (distance + 1e-6))

        return score
    


    def update_state(self, new_state: TargetState) -> None:
        self._state = new_state