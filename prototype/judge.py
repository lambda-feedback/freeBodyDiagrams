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
        for answer_force in target]).T

    row_ind, col_ind = scipy.optimize.linear_sum_assignment(cost_matrix)
    return cost_matrix, row_ind, col_ind

def compare_labels(target, answer, context: SymbolContext) -> bool:
    # defer to karl's program
    # oversimplified implementation for now
    #TODO: add useful info to symbol context and use it here
    return target == answer

# 
@dataclass
class AnswerNode:
    pos: vec2

    #TODO: this should calculate the position dynamically
    def get_pos(this) -> vec2:
        return this.pos

# determines whether a distance marker is close enough to the model answer
@dataclass
class AnswerDistance:
    start_node: int #AnswerNode
    end_node: int #AnswerNode
    label: str
    # is the distance metric necessary?
    #metric: "... -> float" # distance metric

def dist_to_answer_dist(coord_dist) -> AnswerDistance:
    return AnswerDistance(coord_dist.line.pos1, coord_dist.line.pos2, coord_dist.label)

# what the user gets back
@dataclass
class AnswerFeedback:
    score: float
    surplus_forces: int
    surplus_moments: int
    distance_feedback: str #TODO: a string is a bad way to represent this, fix
    warnings: [vec2]

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
        cost_trace1, row_ind1, col_ind1 = hungarian(self.forces, coord_repr.forces)
        cost = sum(cost_trace1[row_ind1, col_ind1] ** 4) ** 0.25
        total_cost += cost

        # moments: hungarian algorithm
        cost_trace2, row_ind2, col_ind2 = hungarian(self.moments, coord_repr.moments)
        #TODO: perhaps this should be changed to 'max' instead
        cost = sum(cost_trace2[row_ind2, col_ind2] ** 4) ** 0.25
        total_cost += cost

        # danger sign (forces only rn)
        warnings = []
        if cost_trace1.shape[1] > 0 and len(coord_repr.forces)-len(self.forces) >= 0:
            for i in range(len(coord_repr.forces)):
                if i not in col_ind1 or min(cost_trace1[i]) > 15:
                    warnings.append(coord_repr.forces[i].pos + coord_repr.forces[i].direction / 2 - vec2(25, 25))
            
        # distances
        distances_valid = self.check_distances(coord_repr)

        return AnswerFeedback(
            score = total_cost - self.tolerance + (0 if distances_valid else 15),
            surplus_forces =  len(coord_repr.forces) - len(self.forces),
            surplus_moments = len(coord_repr.moments) - len(self.moments),
            distance_feedback = "distances correct" if distances_valid else "distances incorrect",
            warnings = warnings
        )
    
    # provides the answer matrix (used for student's matrix too)
    def build_matrix(self, distances):
        params = {
            "strict_syntax": False,
            "elementary_functions": True,
        }
        parsing_params = expression_utilities.create_sympy_parsing_params(params)
        rows = []
        for distance_marker in distances:
            row = ["0"] * (len(self.nodes) + 1)
            neg, pos = sorted((distance_marker.start_node, distance_marker.end_node))
            row[neg] = "-1"
            row[pos] = "1"
            row[-1] = distance_marker.label
            rows.append(row)
        return parse_matrices.parse_matrix(rows, parsing_params)
    
    def check_distances(self, coord_repr) -> bool:
        answer_matrix = self.build_matrix(self.distances)
        matched_nodes = self.pair_up_distance_nodes(coord_repr.distances)
        user_matrix = self.build_matrix(matched_nodes)
        valid = parse_matrices.check_matrix_equivalence(user_matrix, answer_matrix)
        return valid

    # take a list of distance markers and convert them to AnswerDistance
    #TODO: ensure the start and end nodes are unique
    def pair_up_distance_nodes(self, distances) -> [AnswerDistance]:
        answer = []
        for distance_marker in distances:
            #start = self.nodes[distance_marker.start_node].get_pos()
            #end = self.nodes[distance_marker.end_node].get_pos()
            start = distance_marker.line.pos1
            end = distance_marker.line.pos2
            # find closest nodes
            # ans_start = min(self.nodes, key=lambda node: norm(node.get_pos() - start))
            # ans_end   = min(self.nodes, key=lambda node: norm(node.get_pos() - end))
            ans_start = np.argmin([norm(node.get_pos() - start) for node in self.nodes])
            ans_end = np.argmin([norm(node.get_pos() - end) for node in self.nodes])
            answer.append(AnswerDistance(ans_start, ans_end, distance_marker.label))
        return answer

