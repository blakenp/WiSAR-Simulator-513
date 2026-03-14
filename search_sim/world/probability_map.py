from math import floor
import numpy as np
from search_sim.world.nodes.probability_map_node import ProbabilityMapNode
from search_sim.world.nodes.definitions.schema import ProbabilityNode

class ProbabilityMap:
    def __init__(
        self,
        x_length: float = 10.0,
        y_length: float = 10.0,
        num_x_pts: int = 10,
        num_y_pts: int = 10
    ) -> None:
        self.x_length = x_length
        self.y_length = y_length
        self.num_x_pts = num_x_pts
        self.num_y_pts = num_y_pts

        self.x_size = x_length / num_x_pts
        self.y_size = y_length / num_y_pts

        # Initialize the grid with ProbabilityMapNode objects
        # We start with 0.0, or use the 'uniform' factory method below
        self.grid: list[list[ProbabilityMapNode]] = [
            [ProbabilityMapNode(np.float64(0.0)) for _ in range(num_x_pts)] 
            for _ in range(num_y_pts)
        ]

    def _get_indices(self, coords: tuple[float, float]) -> tuple[int, int]:
        """Convert continuous (meters) to discrete grid indices."""
        x_idx = floor(coords[0] / self.x_size)
        y_idx = floor(coords[1] / self.y_size)
        # Boundary clamping to prevent IndexError
        x_idx = max(0, min(x_idx, self.num_x_pts - 1))
        y_idx = max(0, min(y_idx, self.num_y_pts - 1))
        return x_idx, y_idx

    def get_node(self, coords: tuple[float, float]) -> ProbabilityMapNode:
        x, y = self._get_indices(coords)
        return self.grid[y][x]

    def uniform(cls, x_len: float, y_len: float, nx: int, ny: int) -> "ProbabilityMap":
        instance = cls(x_len, y_len, nx, ny)
        uniform_val = np.float64(1.0 / (nx * ny))
        
        for y in range(ny):
            for x in range(nx):
                instance.grid[y][x].update_node_data(ProbabilityNode(probability=uniform_val))
        return instance

    def get_max_probability_location(self) -> tuple[float, float]:
        """Returns spatial coordinates (center of the cell) with highest probability."""
        max_p = -1.0
        best_indices = (0, 0)

        for y in range(self.num_y_pts):
            for x in range(self.num_x_pts):
                p = self.grid[y][x].get_node_data().probability
                if p > max_p:
                    max_p = p
                    best_indices = (x, y)

        spatial_x = (best_indices[0] * self.x_size) + (self.x_size / 2)
        spatial_y = (best_indices[1] * self.y_size) + (self.y_size / 2)
        return spatial_x, spatial_y

    def to_numpy(self) -> np.ndarray:
        """Helper to convert the object-based grid back to a numpy array for vector math."""
        arr = np.zeros((self.num_y_pts, self.num_x_pts), dtype=np.float64)
        for y in range(self.num_y_pts):
            for x in range(self.num_x_pts):
                arr[y, x] = self.grid[y][x].get_node_data().probability
        return arr