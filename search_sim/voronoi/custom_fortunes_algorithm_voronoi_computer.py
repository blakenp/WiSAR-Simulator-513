import heapq
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass(frozen=True, order=True)
class Point:
    x: float
    y: float

class Event:
    def __init__(self, point: Point, site_index: int, is_site: bool, arc_node=None):
        self.point = point
        self.site_index = site_index
        self.is_site = is_site
        self.arc_node = arc_node
        self.is_valid = True  

    def __lt__(self, other):
        if abs(self.point.x - other.point.x) < 1e-9:
            return self.point.y < other.point.y
        return self.point.x < other.point.x

class VoronoiRegion:
    def __init__(self, site: Point):
        self.site = site
        self.vertices: List[Point] = []

class BeachNode:
    def __init__(self, site: Point = None, is_leaf: bool = False):
        self.site = site
        self.is_leaf = is_leaf
        self.left = None
        self.right = None
        self.parent = None
        self.left_site = None
        self.right_site = None
        self.circle_event = None

class CustomFortunesAlgorithmVoronoiComputer:
    def __init__(self, sites: List[Point]):
        self.sites = sites
        self.event_queue = []
        self.regions = [VoronoiRegion(s) for s in sites]
        self.beach_line_root = None
        self.sweep_x = 0
        self.all_vertices = []

        for i, s in enumerate(self.sites):
            heapq.heappush(self.event_queue, Event(s, i, True))

    def compute(self):
        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            if not event.is_valid: continue
            
            self.sweep_x = event.point.x
            
            if event.is_site:
                self._handle_site_event(event)
            else:
                self._handle_circle_event(event)
        
        return self.regions

    def _calculate_breakpoint_y(self, s1: Point, s2: Point) -> float:
        l = self.sweep_x
        if abs(s1.x - s2.x) < 1e-9: return (s1.y + s2.y) / 2.0
        
        z1 = 2 * (s1.x - l)
        z2 = 2 * (s2.x - l)
        
        a = 1/z1 - 1/z2
        b = -2 * (s1.y/z1 - s2.y/z2)
        c = (s1.y**2 + s1.x**2 - l**2)/z1 - (s2.y**2 + s2.x**2 - l**2)/z2
        
        discr = b**2 - 4*a*c
        return (-b + math.sqrt(max(0, discr))) / (2*a)

    def _find_arc_at_y(self, y: float) -> BeachNode:
        curr = self.beach_line_root
        while not curr.is_leaf:
            intersect_y = self._calculate_breakpoint_y(curr.left_site, curr.right_site)
            curr = curr.right if y > intersect_y else curr.left
        return curr

    def _handle_site_event(self, event: Event):
        new_p = event.point
        if not self.beach_line_root:
            self.beach_line_root = BeachNode(site=new_p, is_leaf=True)
            return

        target_arc = self._find_arc_at_y(new_p.y)
        if target_arc.circle_event:
            target_arc.circle_event.is_valid = False

        old_site = target_arc.site
        new_arc_b = BeachNode(site=new_p, is_leaf=True)
        new_arc_a_right = BeachNode(site=old_site, is_leaf=True)

        bp_ab = BeachNode(is_leaf=False)
        bp_ab.left_site, bp_ab.right_site = old_site, new_p
        
        bp_ba = BeachNode(is_leaf=False)
        bp_ba.left_site, bp_ba.right_site = new_p, old_site

        if target_arc.parent:
            if target_arc.parent.left == target_arc: target_arc.parent.left = bp_ab
            else: target_arc.parent.right = bp_ab
        else: self.beach_line_root = bp_ab
        
        bp_ab.parent = target_arc.parent
        bp_ab.left, bp_ab.right = target_arc, bp_ba
        target_arc.parent = bp_ab
        
        bp_ba.parent, bp_ba.left, bp_ba.right = bp_ab, new_arc_b, new_arc_a_right
        new_arc_b.parent = new_arc_a_right.parent = bp_ba

        self._check_circle(target_arc)
        self._check_circle(new_arc_a_right)

    def _handle_circle_event(self, event: Event):
        arc = event.arc_node
        l_n = self._get_left_n(arc)
        r_n = self._get_right_n(arc)
        
        center, _ = self._get_circumcircle(l_n.site, arc.site, r_n.site)
        if center:
            self.all_vertices.append(center)
            for s in [l_n.site, arc.site, r_n.site]:
                for r in self.regions:
                    if r.site == s:
                        r.vertices.append(center)

        pass

    def _get_left_n(self, node: BeachNode) -> Optional[BeachNode]:
        curr = node
        while curr.parent and curr.parent.left == curr:
            curr = curr.parent
        if not curr.parent: return None
        curr = curr.parent.left
        while not curr.is_leaf:
            curr = curr.right
        return curr

    def _get_right_n(self, node: BeachNode) -> Optional[BeachNode]:
        curr = node
        while curr.parent and curr.parent.right == curr:
            curr = curr.parent
        if not curr.parent: return None
        curr = curr.parent.right
        while not curr.is_leaf:
            curr = curr.left
        return curr

    def _get_radius(self, arc: BeachNode) -> float:
        l_n, r_n = self._get_left_n(arc), self._get_right_n(arc)
        if not l_n or not r_n: return 0.0
        _, radius = self._get_circumcircle(l_n.site, arc.site, r_n.site)
        return radius if radius else 0.0

    def _check_circle(self, arc: BeachNode):
        l_n = self._get_left_n(arc)
        r_n = self._get_right_n(arc)
        if not l_n or not r_n or l_n.site == r_n.site: return
        
        center, radius = self._get_circumcircle(l_n.site, arc.site, r_n.site)
        if center and center.x + radius >= self.sweep_x:
            event = Event(Point(center.x + radius, center.y), -1, False, arc)
            arc.circle_event = event
            heapq.heappush(self.event_queue, event)

    def _get_circumcircle(self, a, b, c) -> Tuple[Optional[Point], Optional[float]]:
        D = 2 * (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y))
        if abs(D) < 1e-9: return None, None
        ux = ((a.x**2 + a.y**2) * (b.y - c.y) + (b.x**2 + b.y**2) * (c.y - a.y) + (c.x**2 + c.y**2) * (a.y - b.y)) / D
        uy = ((a.x**2 + a.y**2) * (c.x - b.x) + (b.x**2 + b.y**2) * (a.x - c.x) + (c.x**2 + c.y**2) * (b.x - a.x)) / D
        center = Point(ux, uy)
        radius = math.sqrt((a.x - ux)**2 + (a.y - uy)**2)
        return center, radius

    def _finish_edges(self):
        pass