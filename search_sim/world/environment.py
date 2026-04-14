from math import floor
import math
from typing import List
from search_sim.world.nodes.environment_grid_node import EnvironmentGridNode
from search_sim.world.nodes.definitions.schema import EnvironmentNode
from search_sim.entities.interfaces import Entity

"""
    This class will implement the space we are searching.
    entities: list of targets, agents, and hazards in the environment. Each entity should know its own location.
    x/y_length: spatial length, probably in meters, of the x/y dimension of the space.
    num_x/y_pts: controls the resolution in the x/y dimension.
    grid: a num_y_pts by num_x_pts list, initially filled with zeros, and populated with a -1 at each index where there's a target.
    x/y_size: length divided by num_pts. Useful for calculating distance traveled when traversing a cell.

    TODO:
    - add third dimension
"""

# indexing is a little wonky, since python indexes rows first but rows match better
# with the y direction in my brain. the upshot is that if we want to be able to pass in coordinates
# as (x,y) pairs, then when we're accessing the grid we just need to flip the order and it's fine.
class Environment:    
    def __init__(
        self,
        entities: list[Entity],
        x_length: float = 10,
        y_length: float = 10,
        num_x_pts: int = 10,
        num_y_pts: int = 10
    ) -> None:
        
        self.x_length = x_length
        self.y_length = y_length
        
        self.num_x_pts = num_x_pts
        self.num_y_pts = num_y_pts

        self.grid: list[list[EnvironmentGridNode]] = [[EnvironmentGridNode(id=(i,j)) for i in range(num_x_pts)] for j in range(num_y_pts)]

        self.x_size = x_length/num_x_pts
        self.y_size = y_length/num_y_pts

        for entity in entities:
            coords = entity.get_location()
            x, y = self.get_indices(coords)

            node = self.grid[y][x]
            current_data = node.get_node_data()
            
            new_population = current_data.population | {entity}
            
            node.update_node_data(EnvironmentNode(population=new_population))

    # getter and setter to access individual nodes
    def get_indices(self, coords: tuple[float, float]) -> tuple[int, int]:
        """Convert continuous (meters) to discrete grid indices."""
        x_idx = floor(coords[0] / self.x_size)
        y_idx = floor(coords[1] / self.y_size)
        
        # Boundary clamping to prevent IndexError
        x_idx = max(0, min(x_idx, self.num_x_pts - 1))
        y_idx = max(0, min(y_idx, self.num_y_pts - 1))
        return x_idx, y_idx

    def get_node(self, coords: tuple[float,float]) -> EnvironmentGridNode:
        x, y = self.get_indices(coords)

        return self.grid[y][x]

    def set_node(self, newNode: EnvironmentGridNode, coords: tuple[float,float]) -> None:
        x, y = self.get_indices(coords)

        self.grid[y][x] = newNode

    def handle_ray_cast(
        self, 
        origin_x: float, 
        origin_y: float, 
        angle_rad: float, 
        max_range: float, 
        traversable_hazards: List[str]
    ) -> float:
        """
        Traces a ray from (origin_x, origin_y) at angle_rad.
        Returns the distance to the first obstacle or max_range.
        """
        # Unit vector for the ray direction
        dx = math.cos(angle_rad)
        dy = math.sin(angle_rad)

        # We step at a resolution smaller than our smallest grid cell 
        # to ensure we don't "jump" over a corner.
        step_size = min(self.x_size, self.y_size) * 0.5
        
        current_dist = 0.0
        
        while current_dist < max_range:
            target_x = origin_x + dx * current_dist
            target_y = origin_y + dy * current_dist
            
            if not (0 <= target_x < self.x_length and 0 <= target_y < self.y_length):
                return current_dist

            node = self.get_node((target_x, target_y))
            node_data = node.get_node_data()

            for entity in node_data.population:
                if hasattr(entity, '_state') and entity._state.type.value not in traversable_hazards:
                    return current_dist
            
            current_dist += step_size

        return max_range