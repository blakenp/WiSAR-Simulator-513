from search_sim.agents.definitions.schema import AgentState
from search_sim.targets.definitions.schema import TargetState
from search_sim.hazards.definitions.schema import HazardState
from math import sqrt, atan2, degrees, pi
from numpy import linspace

def get_nearby_entity_states(id, x, y, awareness, agents, targets, hazards) -> tuple[list[AgentState], list[TargetState], list[HazardState]]:
    """Identifies all other entities within a specified radius of a given point.

        Parameters:
            id: the id string of the entity you want to find the neighbors of.
            x: the x position you want to find neighbors near.
            y: the y position you want to find neighbors near.
            awareness: the awareness radius of the relevant entity.
            agents: a list of all agents in the environment.
            targets: a list of all targets in the environment.
            hazards: a list of all hazards in the environment.
    """
    new_agent_states = [agent._state for agent in agents 
                    if compute_distance(x,agent._state.x,y,agent._state.y) <= awareness
                    and id != agent._state.id]
        
    new_target_states = [target._state for target in targets 
                    if compute_distance(x,target._state.x,y,target._state.y) <= awareness
                    and id != target._state.id]

    new_hazard_states = [hazard._state for hazard in hazards
                    if compute_distance(x,hazard._state.x,y,hazard._state.y) <= awareness
                    and id != hazard._state.id]
    
    return new_agent_states, new_target_states, new_hazard_states

def compute_distance(x_a: float, x_b: float, y_a: float, y_b: float) -> float:
    return sqrt((x_a - x_b)**2 + (y_a - y_b)**2)

def compute_heading(curr_x: float, new_x: float, curr_y: float, new_y: float):
    dx = new_x - curr_x
    dy = new_y - curr_y

    angle_rad = atan2(dy, dx)
    heading = degrees(angle_rad) % 360
    
    return heading

def sample_angles(n, preferred_angles=None, spread=pi / 2):
    """
    Samples n angles, some clustered around each angle in preferred_angles, and some uniform.
    """
    n_groups = 1 + len(preferred_angles)

    uniform = [2 * pi * i / (n // n_groups) for i in range(n // n_groups)]
    
    if len(preferred_angles) != 0:
        focused = []
        for angle in preferred_angles:
            for i in range(n // n_groups):
                focused.append(angle + spread *(i / (n // n_groups) - 0.5))
        return uniform + focused
    else:
         return uniform
    
def sample_speeds(max_speed, n):
    """A few discrete speed levels, always including a stop option."""
    if n == 1:
        return [0, max_speed]
    return [max_speed * i / (n - 1) for i in range(n)]

def argmax(list):
    return max(range(len(list)), key=list.__getitem__)

def validate_move(curr_x, curr_y, new_x, new_y, max_speed, environment, traversable_hazards, resolution=100):
    """Checks if a proposed move is valid given speed constraints and hazard collisions."""

    max_x = environment.x_length
    max_y = environment.y_length

    distance = compute_distance(curr_x, new_x, curr_y, new_y)
    if distance > max_speed:
        return False
    
    """Construct a list of all unique nodes along the proposed trajectory"""
    x_interval = linspace(curr_x,new_x,resolution)
    y_interval = linspace(curr_y,new_y,resolution)
    points = list(zip(x_interval,y_interval))
    nodes = [environment.get_node(point) for point in points]
    seen_ids = set()
    unique_nodes = []
    for node in nodes:
        if node._id not in seen_ids:
            seen_ids.add(node._id)
            unique_nodes.append(node)

    """Check each node sequentially for non-traversable hazards"""
    for node in unique_nodes:
        hazards = node.get_hazards()
        for hazard in hazards:
            if hazard.get_type().value not in traversable_hazards:
                return False
        
    if new_x < 0 or new_y < 0:
        return False
    
    if new_x > max_x or new_y > max_y:
        return False

    return True