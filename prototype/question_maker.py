# the idea is to make it easier to create questions
# only applies to questions on a line
# only applies if you know the order of the nodes
from dataclasses import dataclass
import numpy as np

from representation import *
from freeBodyDiagrams.prototype.evaluation import *

# enum
class Orientation:
    HORIZONTAL = vec2(1, 0)
    VERTICAL = vec2(0, -1)

class LineQuestionMaker:
    def __init__(self, orientation=Orientation.HORIZONTAL, length=100, nodes=2, rough_node_positions=None, dimensions=vec2(800, 600)):
        self.direction = orientation
        self.length = length
        self.nodes = nodes
        self.rough_node_positions = rough_node_positions
        self.dimensions = dimensions
        self.MIDDLE = dimensions / 2

        self.distances = []
        self.forces = []

    def add_distance(self, node1, node2, dist):
        self.distances.append((node1, node2, dist))

    def add_force(self, direction, node, label, bidirectional=False):
        self.forces.append((direction, node, label, bidirectional))

    def build(self) -> AnswerDiagram:
        # nodes
        nodes = []
        start = self.MIDDLE - self.direction * self.length / 2
        for i in range(self.nodes):
            r = 0
            if self.rough_node_positions is not None:
                r = self.rough_node_positions[i]
            else:
                r = i * self.length / (self.nodes - 1)
            nodes.append(start + self.direction * r)
        
        # distance markers
        distances = []
        for d in self.distances:
            distances.append(AnswerDistance(
                start_node = d[0],
                end_node = d[1],
                distance = d[2],
            ))

        forces = []
        for force in self.forces:
            direction, node, label, bidirectional = force
            forces.append(AnswerForce(
                pos = nodes[node],
                direction = direction,
                label = label,
                metric = force_metric(
                    bidirectional = bidirectional,
                ),
                parent = ...
            ))

        return AnswerDiagram(
            nodes = nodes,
            distances = distances,
            forces = [],
            moments = [],
            tolerance = 15,
            context = ...
        )