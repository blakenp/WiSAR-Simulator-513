from search_sim.voronoi.custom_fortunes_algorithm_voronoi_computer import CustomFortunesAlgorithmVoronoiComputer
from search_sim.voronoi.custom_fortunes_algorithm_voronoi_computer import Point

def test_fortunes_algorithm():
    sites = [Point(2, 5), Point(6, 8), Point(3, 1), Point(9, 7)]
    computer = CustomFortunesAlgorithmVoronoiComputer(sites)
    regions = computer.compute()
    print("Voronoi Regions:")
    for i, region in enumerate(regions):
        print(f"  Region {i}: Site = {region.site}, Vertices = {region.vertices}")

    assert len(regions) == len(sites)
    for region in regions:
        assert region.site in sites
        assert isinstance(region.vertices, list)

test_fortunes_algorithm()