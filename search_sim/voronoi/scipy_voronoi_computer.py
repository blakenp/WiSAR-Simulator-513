import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt

class ScipyVoronoiComputer:
    def __init__(self, points: np.ndarray):
        self.points = points

    def compute_voronoi(self):
        voronoi = Voronoi(self.points)
        return voronoi

    def plot(self, voronoi):
        voronoi_plot_2d(voronoi, show_vertices=False)
        plt.scatter(self.points[:, 0], self.points[:, 1], c='red')
        plt.title("Voronoi Diagram")
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")
        plt.grid()
        plt.show()