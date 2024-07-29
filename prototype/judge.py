import svgwrite
from dataclasses import dataclass
import numpy as np
import scipy
import json

import parse_matrices
import expression_utilities

from representation import *

# not used right now
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
    forces: [AnswerForce]
    moments: [AnswerMoment]

    # not used right now but in the future?
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
        # skeleton
        m0_strings = [
            ["-1","1","0","0","2L"],
            ["0","-1","1","0","L"],
            ["0","0","-1","1","2L"],
            ["1","0","0","0","0"]
        ]
        model_strings = [
            ["1","0","0","0","0"],
            ["0","1","0","0","2L"],
            ["0","0","1","0","3L"],
            ["0","0","0","1","5L"]
        ]
        params = {
            "strict_syntax": False,
            "elementary_functions": True,
        }
        parsing_params = expression_utilities.create_sympy_parsing_params(params)
        m0 = parse_matrices.parse_matrix(m0_strings, parsing_params)
        m1 = parse_matrices.parse_matrix(model_strings, parsing_params)
        print(m0)
        print(m1)
        print(parse_matrices.check_matrix_equivalence(m0, m1))

    def determine_node_locations() -> [vec2]:
        pass

