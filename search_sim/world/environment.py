from math import floor
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

        self.grid: list[list[EnvironmentGridNode]] = [[EnvironmentGridNode() for _ in range(num_x_pts)] for _ in range(num_y_pts)]

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