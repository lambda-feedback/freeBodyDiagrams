import svgwrite
from dataclasses import dataclass
import numpy as np
import scipy
import json

"""
dwg.add(dwg.line((0, 0), (100, 0), stroke=svgwrite.rgb(10, 10, 16, '%')))
dwg.add(dwg.line((0, 0), (0, 100), stroke=svgwrite.rgb(10, 12, 16, '%')))
dwg.add(dwg.text('Test', insert=(0, 0.2), fill='red'))

dwg.save()
"""

norm = np.linalg.norm

def vec2(x, y):
    return np.array((x,y))

def vec_to_tuple(vec):
    return tuple(int(v) for v in vec)

@dataclass
class CoordLine:
    pos1: vec2
    pos2: vec2

@dataclass
class CoordForce:
    pos: vec2
    direction: vec2
    label: str

@dataclass
class CoordMoment:
    pos: vec2
    clockwise: bool
    label: str

@dataclass
class CoordDistance:
    line: CoordLine
    label: str

# initial (coordinate) representation
@dataclass
class CoordRepr:
    lines: [CoordLine]
    forces: [CoordForce]
    moments: [CoordMoment]
    distances: [CoordDistance]

    def draw(self, dwg):
        for line in self.lines:
            dwg.add(dwg.line(vec_to_tuple(line.pos1), vec_to_tuple(line.pos2),
                             stroke=svgwrite.rgb(0, 0, 0, '%'),
                             stroke_width=5))

        for force in self.forces:
            dwg.add(dwg.line(vec_to_tuple(force.pos),
                             vec_to_tuple(np.array(force.pos) - np.array(force.direction)*20),
                             stroke=svgwrite.rgb(0, 128, 0, '%')))

        for dist in self.distances:
            pos = vec_to_tuple(0.5 * (np.array(dist.line.pos1) + np.array(dist.line.pos2)))
            dwg.add(dwg.line(vec_to_tuple(dist.line.pos1), vec_to_tuple(dist.line.pos2),
                             stroke=svgwrite.rgb(0, 0, 128, '%')))
            dwg.add(dwg.text(dist.label, insert=pos, fill='red'))

"""
# eg 1
eg1 = CoordRepr(
    lines = [CoordLine((20, 40), (224, 48))],
    forces = [
        CoordForce(
            pos = (23,46),
            direction = (-0.99, 0.05),
            label = "A_H",
        ),
        CoordForce(
            pos = (17,45),
            direction = (0.05, 0.99),
            label = "A_V",
        ),
        CoordForce(
            pos = (125,41),
            direction = (0.1, -0.99),
            label = "F_1",
        ),
        CoordForce(
            pos = (227,40),
            direction = (0.1, 0.99),
            label = "B_v",
        ),
    ],
    moments = [],
    distances = [
        CoordDistance(
            line = CoordLine((23, 50), (220, 61)),
            label = "L"
        ),
        CoordDistance(
            line = CoordLine((23, 30), (119, 31)),
            label = "L/2"
        ),
    ]
)
"""

# context for the problem (which variables are defined, etc.)
class SymbolContext:
    def __init__(self) -> None:
        pass

# representation for model answer
@dataclass
class AnswerForce:
    pos: vec2
    direction: vec2 # not normalised, normalise it yourself
    label: str
    metric: "... -> float" # distance metric

    def dist(self, force):
        return self.metric(self, force)

@dataclass
class AnswerMoment:
    pos: vec2
    label: str
    clockwise: bool
    metric: "... -> float" # distance metric

    def dist(self, moment):
        return self.metric(self, moment)

# metrics and stuff for determining how close a particular arrow is to it's ideal location
def node_metric(scale=1):
    return lambda target, node: norm(node.pos - target.pos) / scale

def force_metric():
    def fn(target, ans):
        dist = norm(target.pos - ans.pos)
        dot = (target.direction * ans.direction).sum() / (norm(target.direction) * norm(ans.direction))
        return dist*dist + 500 * (1-dot)**2
    return fn

def moment_metric():
    def fn(target, ans):
        dist = norm(target.pos - ans.pos)
        # ... tbc
        return dist
    return fn

# QOL function
def DIRECTION(theta) -> vec2:
    theta *= np.pi / 180
    return vec2(np.cos(theta), np.sin(theta))

def hungarian(target, ans):
    # not limited to forces
    cost_matrix = np.array([
        [answer_force.dist(response_force) for response_force in ans]
        for answer_force in target])

    row_ind, col_ind = scipy.optimize.linear_sum_assignment(cost_matrix)
    cost = cost_matrix[row_ind, col_ind].sum()
    return cost

def compare_labels(target, answer, context: SymbolContext) -> bool:
    # defer to karl's program
    # oversimplified implementation for now
    return target == answer

@dataclass
class AnswerNode:
    ...
    label: str
    metric: "... -> float" # distance metric

    def get_pos():
        return ...

@dataclass
class AnswerDistance:
    start_node: AnswerNode
    end_node: AnswerNode
    label: str
    metric: "... -> float" # distance metric

@dataclass
class AnswerDiagram:
    # nodes
    forces: [AnswerForce]
    moments: [AnswerMoment]

    context: SymbolContext # symbols we can use, etc.

    # figure out where answer nodes are and 
    nodes: [AnswerNode]
    distances: [AnswerDistance] # to be continued

    tolerance: float # how far is it allowed to be from the actual answer

    def check_diagram(self, coord_repr) -> bool:
        total_cost = 0

        # match forces up
        total_cost += hungarian(self.forces, coord_repr.forces)

        # moments: hungarian algorithm
        total_cost += hungarian(self.moments, coord_repr.moments)

        return total_cost - self.tolerance
    
    def check_distances(self, coord_repr) -> bool:
        pass

def decode_JSON(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    distances = []
    forces = []
    moments = []

    for arrow in data.get('distance_markers', []):
        line = CoordLine(pos1=vec2(arrow['startX'], arrow['startY']),
                         pos2=vec2(arrow['endX'], arrow['endY']))
        distances.append(CoordDistance(line=line, label=arrow['text']))

    for arrow in data.get('forces', []):
        start_vec = vec2(arrow['startX'], arrow['startY'])
        end_vec = vec2(arrow['endX'], arrow['endY'])
        direction = end_vec - start_vec
        forces.append(CoordForce(pos=start_vec, direction=direction, label=arrow['text']))

    for arrow in data.get('moments', []):
        start_vec = vec2(arrow['startX'], arrow['startY'])
        end_vec = vec2(arrow['endX'], arrow['endY'])
        direction = end_vec - start_vec
        clockwise = np.cross(direction, np.array([0, -1])) < 0
        moments.append(CoordMoment(pos=start_vec, clockwise=clockwise, label=arrow['text']))

    # no lines for now
    return CoordRepr([], distances, forces, moments)
