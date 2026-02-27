"""
    This class will implement the space we are searching.

    target/hazard_indices: list of (x,y) coordinate pairs for a given target/hazard. For example, [[0,2],[4,4]] for two targets. Coordinates are given as
    indices in an array.

    target/hazard_values: a numerical score associated with a particular target/hazard. maybe useful for some kind of cost function.

    x/y_length: spatial length, probably in meters, of the x/y dimension of the space.

    num_x/y_pts: controls the resolution in the x/y dimension.

    grid: a num_y_pts by num_x_pts list, initially filled with zeros, and populated with a -1 at each index where there's a target.

    x/y_size: length divided by num_pts. Useful for calculating distance traveled when traversing a cell.

    TODO:
    - add third dimension
"""

class Environment:    
    def __init__(self, target_indices, target_values, hazard_indices, hazard_values, x_length=10, y_length=10, num_x_pts=10, num_y_pts=10):
        self.x_length = x_length
        self.y_length = y_length
        
        self.num_x_pts = num_x_pts
        self.num_y_pts = num_y_pts

        self.grid = [[0 for i in range(num_x_pts)] for j in range(num_y_pts)]

        self.num_targets = len(target_indices)

        for i in range(len(target_values)):
            x = target_indices[i][0]
            y = target_indices[i][1]
            self.grid[y][x] = target_values[i]  # indexing is a little wonky, since python indexes rows first but rows match better
                                                # with the y direction in my brain. the upshot is that if we want to be able to pass in coordinates
                                                # as (x,y) pairs, then when we're accessing the grid we just need to flip the order and it's fine.

        for i in range(len(hazard_values)):
            x = hazard_indices[i][0]
            y = hazard_indices[i][1]
            self.grid[y][x] = hazard_values[i]
        
        self.x_size = x_length/num_x_pts
        self.y_size = y_length/num_y_pts