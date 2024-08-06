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

def force_metric(bidirectional=False, dir_sensitivity=100, pos_matrix=np.array([[0.1, 0],[0, 0.1]])):
    def fn(target, ans):
        #dist = norm(target.pos - ans.pos)
        dot = (target.direction * ans.direction).sum() / max((norm(target.direction) * norm(ans.direction)), 0.0001)
        if bidirectional:
            dot = abs(dot)
        error_vec = target.pos - ans.pos
        cost_quadratic_form = np.sqrt(np.dot(error_vec, pos_matrix @ error_vec))
        label_cost = 0
        if target.label != ans.label:
            label_cost = 20
        return label_cost + cost_quadratic_form + dir_sensitivity * abs(1-dot)
    return fn

def moment_metric():
    def fn(target, ans):
        dist = norm(target.pos - ans.pos) * 0.01
        # ... tbc
        return dist
    return fn

# QOL function
def DIRECTION(theta) -> vec2:
    theta *= np.pi / 180
    return vec2(np.cos(theta), -np.sin(theta))

def hungarian(target, ans):
    # not limited to forces
    cost_matrix = np.array([
        [answer_force.dist(response_force) for response_force in ans]
        for answer_force in target])

    row_ind, col_ind = scipy.optimize.linear_sum_assignment(cost_matrix)
    return cost_matrix[row_ind, col_ind]

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
class AnswerFeedback:
    score: float
    surplus_forces: int
    surplus_moments: int
    distance_feedback: ...

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

    def check_diagram(self, coord_repr) -> AnswerFeedback:
        total_cost = 0

        # match forces up
        cost_trace1 = hungarian(self.forces, coord_repr.forces)
        cost = sum(cost_trace1 ** 4) ** 0.25
        total_cost += cost

        # moments: hungarian algorithm
        cost_trace2 = hungarian(self.moments, coord_repr.moments)
        cost = sum(cost_trace2 ** 4) ** 0.25
        total_cost += cost

        return AnswerFeedback(
            score = total_cost - self.tolerance,
            surplus_forces =  len(coord_repr.forces) - len(self.forces),
            surplus_moments = len(coord_repr.moments) - len(self.moments),
            distance_feedback = "not implemented yet"
        )

        """return total_cost - self.tolerance, f"{(list(cost_trace1), len(self.forces), len(coord_repr.forces))} <br>\
              {list(cost_trace2)} {len(self.moments)} {len(coord_repr.moments)}"""
    
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

