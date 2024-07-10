import svgwrite
from dataclasses import dataclass
import numpy as np
import scipy

"""
dwg.add(dwg.line((0, 0), (100, 0), stroke=svgwrite.rgb(10, 10, 16, '%')))
dwg.add(dwg.line((0, 0), (0, 100), stroke=svgwrite.rgb(10, 12, 16, '%')))
dwg.add(dwg.text('Test', insert=(0, 0.2), fill='red'))

dwg.save()
"""

def vec2(x, y):
    return np.array((x,y))

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
            dwg.add(dwg.line(line.pos1, line.pos2,
                             stroke=svgwrite.rgb(0, 0, 0, '%')))

        for force in self.forces:
            dwg.add(dwg.line(force.pos,
                             tuple(np.array(force.pos) - np.array(force.direction)*20),
                             stroke=svgwrite.rgb(0, 128, 0, '%')))

        for dist in self.distances:
            pos = tuple(0.5 * (np.array(dist.line.pos1) + np.array(dist.line.pos2)))
            dwg.add(dwg.line(dist.line.pos1, dist.line.pos2,
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

# representation for model answer
@dataclass
class AnswerNode:
    #pos: vec2
    label: str
    metric: "vec2 -> float" # distance metric

@dataclass
class AnswerForce:
    #pos: vec2
    #direction: vec2
    label: str
    metric: "vec2 -> float" # distance metric

    def dist(self, force):
        return self.metric(...)

@dataclass
class AnswerMoment:
    #pos: vec2
    label: str
    metric: "vec2 -> float" # distance metric

    def dist(self, moment):
        return self.metric(...)

# metrics and stuff for determining how close a particular arrow is to it's ideal location
def node_dist_metric(pos, scale=1):
    return lambda xy: np.linalg.norm(xy - pos) / scale

def force_dist_metric(pos,):
    return ...

@dataclass
class AnswerDiagram:
    # nodes
    nodes: [AnswerNode]
    forces: [AnswerForce]
    moments: [AnswerMoment]

    distances: ... # to be continued

    tolerance: float # how far is it allowed to be from the actual answer

    def check_diagram(self, coord_repr) -> bool:
        total_cost = 0

        # match forces up (hungarian algorithm)
        cost_matrix = np.array([
            [answer_force.metric(response_force) for response_force in coord_repr.forces]
            for answer_force in self.forces])

        row_ind, col_ind = scipy.optimize.linear_sum_assignment(cost_matrix)
        cost = cost_matrix[row_ind, col_ind].sum()
        total_cost += cost

        # moments: hungarian algorithm
        # TBC

# test on example 3
eg3 = CoordRepr(
    lines = [CoordLine((202, 283), (627, 283))],
    forces = [
        CoordForce(
            pos = (202, 283),
            direction = (-0.99, 0.05),
            label = "A_H",
        ),
        CoordForce(
            pos = (202, 283),
            direction = (0.05, 0.99),
            label = "A_V",
        ),
        CoordForce(
            pos = (627, 283),
            direction = (0.1, -0.99),
            label = "F_1",
        ),
        CoordForce(
            pos = (415, 283),
            direction = (0.1, 0.99),
            label = "B_v",
        ),
    ],
    moments = [CoordMoment((415, 283), False, "X")],
    distances = [
        CoordDistance(
            line = CoordLine((202, 287), (415, 287)),
            label = "L/2"
        ),
        CoordDistance(
            line = CoordLine((415, 291), (627, 291)),
            label = "L/2"
        ),
    ]
)

answer3 = AnswerDiagram(
    nodes = [
        #tbc
    ],
    forces = [
        AnswerForce(
            pos = vec2(202, 283),
            direction = vec2(-0.99, 0.05),
            label = "A_H",
        ),
        AnswerForce(
            pos = vec2(202, 283),
            direction = vec2(0.05, 0.99),
            label = "A_V",
        ),
        AnswerForce(
            pos = vec2(627, 283),
            direction = vec2(0.1, -0.99),
            label = "F_1",
        ),
        AnswerForce(
            pos = vec2(415, 283),
            direction = vec2(0.1, 0.99),
            label = "B_v",
        ),
    ],
    moments = [AnswerMoment((415, 283), False, "X")],

    distances = [],
    tolerance = 10
)

dwg = svgwrite.Drawing('test.svg')
eg3.draw(dwg)
dwg.save()

