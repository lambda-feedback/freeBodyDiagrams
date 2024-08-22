# This file contains the evaluation functions as well as the representation for the model answer.
# It also contains a few helper functions

import svgwrite
from dataclasses import dataclass, field
import numpy as np
import scipy
import json
from typing import Callable # used for type hints

import parse_matrices
import expression_utilities

from representation import *

# not used right now
# context for the problem (which variables are defined, etc.)
# supposed to be used to determine whether the student is allowed to make up a name or not
class SymbolContext:
    def __init__(self) -> None:
        pass

@dataclass
class Warning:
    pos: vec2
    message: str

# representation for model answer
@dataclass
class AnswerForce:
    pos: int # this is the index of the node
    direction: vec2 # not normalised, normalise it yourself
    label: str
    metric: "... -> float" # distance metric

    parent: "AnswerDiagram" = None

    def get_pos(self):
        return self.parent.nodes[self.pos].get_pos()

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

        dot = (target.direction * ans.direction).sum() / max((norm(target.direction) * norm(ans.direction)), 0.0001)
        if bidirectional:
            dot = abs(dot)

        error_vec = target.get_pos() - ans.pos
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

# to be implemented
def node_metric():
    pass

# QOL function
def DIRECTION(theta) -> vec2:
    theta *= np.pi / 180
    return vec2(np.cos(theta), -np.sin(theta))

# QOL function
def DIAGONAL(x, y):
    return np.array([[x, 0],[0, y]])

def hungarian(target, ans):
    # not limited to forces
    cost_matrix = np.array([
        [answer_force.dist(response_force) for response_force in ans]
        for answer_force in target]).T

    row_ind, col_ind = scipy.optimize.linear_sum_assignment(cost_matrix)
    return cost_matrix, row_ind, col_ind

def compare_labels(target, answer, context: SymbolContext) -> bool:
    #return True # comment out this line if you want to compare labels
    # defer to karl's symbolic comparison
    # oversimplified implementation for now
    #TODO: add useful info to symbol context and use it here
    return target == answer

# idea: figure out 
@dataclass
class AnswerNode:
    # starting position
    start_pos: vec2

    # get position based on an average of force positions (refers to AnswerDiagram)
    # there needs to be some checking in check_diagram() to ensure that this lies on the line
    things_to_average: list # e.g. [(AnswerForce, 0, weight_matrix), (AnswerForce, 2, weight_matrix)]

    metric: Callable[..., float] # distance metric to determine if it is in an acceptable location

    _parent: "AnswerDiagram" = None
    _context: CoordRepr = None

    # this calculates the positions of the node dymaically
    def get_pos(self) -> vec2:
        if self._parent._first_iter:
            return self.start_pos
        total_weight = DIAGONAL(0, 0)
        total = vec2(0, 0)
        for source, value, weight in self.things_to_average:
            if source == AnswerForce:
                #total += weight @ self._context.forces[value].pos
                try:
                    total += weight @ self._context.forces[self._parent._force_matchings[value]].pos
                    total_weight += weight
                except Exception as e:
                    print("INFO")
                    print(len(self._context.forces))
                    print(self._parent._force_matchings)
                    print(value)
                    raise e
                
            elif source == vec2:
                total += weight @ value
                total_weight += weight
        inv_weight = np.linalg.inv(total_weight)
        ans = inv_weight @ total
        return ans

# determines whether a distance marker is close enough to the model answer
@dataclass
class AnswerDistance:
    start_node: int
    end_node: int
    label: str

def dist_to_answer_dist(coord_dist) -> AnswerDistance:
    return AnswerDistance(coord_dist.line.pos1, coord_dist.line.pos2, coord_dist.label)

# what the user gets back
@dataclass
class AnswerFeedback:
    score: float
    surplus_forces: int
    surplus_moments: int
    distance_feedback: str #TODO: a string is a bad way to represent this, fix
    warnings: list[vec2]

@dataclass
class AnswerDiagram:
    forces: list[AnswerForce]
    moments: list[AnswerMoment]

    # not used right now but in the future?
    # idea: sometimes the user can invent symbols and sometimes the answer needs to use specific symbols
    context: SymbolContext # symbols we can use, etc.

    # figure out where answer nodes are and 
    nodes: list[AnswerNode]
    distances: list[AnswerDistance] # to be continued

    tolerance: float # how far is it allowed to be from the actual answer

    # temporary parameter to store matchings
    # this is used by answer nodes
    _force_matchings: dict = None#field(default_factory=lambda: dict()) # from model answer to user answer
    _first_iter: bool = False

    def _get_force(self, index):
        return self._force_matchings[index]

    def check_diagram(self, coord_repr) -> AnswerFeedback:
        total_cost = 0

        # provide necessary context for forces
        for force in self.forces:
            force.parent = self
        
        # provide parent info for nodes
        for node in self.nodes:
            node._context = coord_repr
            node._parent = self
        
        self._first_iter = True

        # initialise to None for use later
        cost_trace1, row_ind1, col_ind1 = None, None, None
        cost_trace2, row_ind2, col_ind2 = None, None, None

        # we do this a couple of times
        # we need to know the rought force matchings before we can figure out the node positions
        # I don't know of a better way to do this
        for i in range(3):
            cost_trace1, row_ind1, col_ind1 = hungarian(self.forces, coord_repr.forces)

            # save the pairings (TODO: is this even correct?)
            self._force_matchings = {row_ind1[i]: col_ind1[i] for i in range(len(row_ind1))}

            # moments: hungarian algorithm
            cost_trace2, row_ind2, col_ind2 = hungarian(self.moments, coord_repr.moments)
            self._first_iter = False

        # TODO: perhaps this should be changed to `max` instead?
        total_cost += sum(cost_trace1[row_ind1, col_ind1] ** 4) ** 0.25
        total_cost += sum(cost_trace2[row_ind2, col_ind2] ** 4) ** 0.25

        # TODO: penalty for nodes that stray too far from their ideal positions

        # TODO: pentaly for distance markers that are in "crazy" positions
        # I don't know the right way to do this yet
        # you don't want to punish distance markers that are, for example, directly below the model answer, because it is still correct
        # but you do want to punish distance markers that are off to the side
        # however you want to punish distance markers if the endpoints have wildly different y values

        # danger sign (forces only rn)
        # TODO: expand this to moments, etc
        warnings = []
        if cost_trace1.shape[1] > 0 and len(coord_repr.forces)-len(self.forces) >= 0:
            for i in range(len(coord_repr.forces)):
                if i not in col_ind1 or min(cost_trace1[i]) > 15:
                    warnings.append(Warning(
                        coord_repr.forces[i].pos + coord_repr.forces[i].direction / 2,
                        min(cost_trace1[i])
                    ))

        # for debugging
        warnings.append(Warning(self.nodes[0].get_pos() - vec2(0, 200), "node 0"))
        warnings.append(Warning(self.nodes[1].get_pos() - vec2(0, 200), "node 1"))
        warnings.append(Warning(self.nodes[2].get_pos() - vec2(0, 200), "node 2"))
            
        # distances
        distances_valid = self.check_distances(coord_repr)

        # surpluses
        surplus_forces = len(coord_repr.forces) - len(self.forces)
        surplus_moments = len(coord_repr.moments) - len(self.moments)

        return AnswerFeedback(
            # we want the score to be NEGATIVE if the answer is correct
            score = total_cost - self.tolerance + (0 if distances_valid else 15)
                + (abs(surplus_moments) + abs(surplus_forces)) * 15, # so that the score is positive when there are not enough forces
            surplus_forces = surplus_forces,
            surplus_moments = surplus_moments,
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
    def pair_up_distance_nodes(self, distances) -> list[AnswerDistance]:
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

