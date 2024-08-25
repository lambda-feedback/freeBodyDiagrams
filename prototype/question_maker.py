# the idea is to make it easier to create questions
# only applies to questions on a line
# only applies if you know the order of the nodes
from dataclasses import dataclass
import numpy as np

from representation import *
from evaluation import *

# enum
class Orientation:
    HORIZONTAL = vec2(1, 0)
    VERTICAL = vec2(0, -1)

# NOTE: currently only works for horizontal lines due to time constraints
# to implement it just fix the two TODOs
class LineQuestionMaker:
    def __init__(self, orientation=Orientation.HORIZONTAL, length=400, nodes=2, rough_node_positions=None, dimensions=vec2(800, 600)):
        self.direction = orientation
        self.length = length
        self.nodes = nodes
        self.rough_node_positions = rough_node_positions
        self.dimensions = dimensions
        self.MIDDLE = dimensions / 2

        self.distances = []
        self.forces = []
        self.moments = [] # storing this as a list of points because we don't use the full line anyway

    def add_distance(self, node1, node2, dist):
        self.distances.append((node1, node2, dist))

    def add_force(self, direction, node, label, bidirectional=False):
        self.forces.append((direction, node, label, bidirectional))

    def add_moment(self, node, label, clockwise = True):
        self.moments.append((node, label, clockwise))

    def build(self) -> AnswerDiagram:
        # calculate useful stuff
        PERP = vec2(-self.direction[1], self.direction[0])

        # nodes
        node_positions = []
        start = self.MIDDLE - self.direction * self.length / 2
        for i in range(self.nodes):
            r = 0
            if self.rough_node_positions is not None:
                r = self.rough_node_positions[i]
            else:
                r = i * self.length / (self.nodes - 1)
            node_positions.append(start + self.direction * r)
        
        # distance markers
        distances = []
        for d in self.distances:
            distances.append(AnswerDistance(
                start_node = d[0],
                end_node = d[1],
                label = d[2],
            ))

        forces = []
        for force in self.forces:
            direction, node, label, bidirectional = force
            forces.append(AnswerForce(
                pos = node,
                direction = direction,
                label = label,
                metric = force_metric(
                    bidirectional = bidirectional,
                ),
                parent = ... # gets initialised later
            ))

        # moments
        moments = []
        for moment in self.moments:
            node, label, clockwise = moment
            moments.append(AnswerMoment(
                pos = node_positions[node],
                clockwise = clockwise,
                label = label,
                metric = moment_metric(),
                parent = ... # gets initialised later
            ))

        # tell nodes that they have forces etc that they need to average over
        final_nodes = []
        for i in range(self.nodes):
            things_to_average = []
            if i in [0, self.nodes - 1]:
                things_to_average.append((vec2, node_positions[i], DIAGONAL(1, 1)))
            else:
                # TODO: change matrix to be direction-independent
                things_to_average.append((vec2, node_positions[i], DIAGONAL(0, 1)))
                # go through all the forces to see if any of them are at this node
                for j, force in enumerate(forces):
                    if force.pos == i:
                        # TODO: change matrix to be direction-independent
                        things_to_average.append((AnswerForce, j, DIAGONAL(1, 0)))
                # TODO: repeat for moments, but weighted slightly less as you could expect them to be further out?
            final_nodes.append(AnswerNode(
                start_pos = node_positions[i],
                things_to_average = [],
                metric = None,
            ))

        # TODO: automatically generate a picture for the question?
        return AnswerDiagram(
            nodes = final_nodes,
            distances = distances,
            forces = forces,
            moments = moments,
            tolerance = 15,
            context = ...
        )
    

