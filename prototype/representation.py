import svgwrite
from dataclasses import dataclass
import numpy as np
import scipy
import json

import parse_matrices
import expression_utilities

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

def load_JSON(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def decode_JSON(data):
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
    return CoordRepr([], forces, moments, distances)

"""
dwg.add(dwg.line((0, 0), (100, 0), stroke=svgwrite.rgb(10, 10, 16, '%')))
dwg.add(dwg.line((0, 0), (0, 100), stroke=svgwrite.rgb(10, 12, 16, '%')))
dwg.add(dwg.text('Test', insert=(0, 0.2), fill='red'))

dwg.save()
"""

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