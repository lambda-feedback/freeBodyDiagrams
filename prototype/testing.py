# NOTE: this file is not really used much anymore, but kept for reference and for eg3
from evaluation import *

# test on example 3
eg3 = CoordRepr(
    lines = [CoordLine(vec2(200, 300), vec2(600, 300))],
    forces = [
        CoordForce(
            pos = vec2(200, 300),
            direction = DIRECTION(180),
            label = "A_H",
        ),
        CoordForce(
            pos = vec2(200, 300),
            direction = vec2(0.05, 0.99),
            label = "A_V",
        ),
        CoordForce(
            pos = vec2(600, 300),
            direction = DIRECTION(-90),
            label = "F_1",
        ),
        CoordForce(
            pos = vec2(400, 300),
            direction = DIRECTION(90),
            label = "B_v",
        ),
    ],
    moments = [CoordMoment(vec2(400, 300), False, "X")],
    distances = [
        CoordDistance(
            line = CoordLine(vec2(200, 287), vec2(400, 287)),
            label = "L/2"
        ),
        CoordDistance(
            line = CoordLine(vec2(400, 291), vec2(600, 291)),
            label = "L/2"
        ),
    ]
)

answer3 = AnswerDiagram(
    # hard-coded values for now
    nodes = [
        AnswerNode(
            start_pos = vec2(200, 300),
            things_to_average = [(vec2, vec2(200, 300), DIAGONAL(1, 1))],
            metric = None,
        ),
        AnswerNode(
            start_pos = vec2(400, 300),
            # keep horizontal component of force and constant vertical component
            things_to_average = [(AnswerForce, 3, DIAGONAL(1, 0)), (vec2, vec2(0, 300), DIAGONAL(0, 1))],
            metric = None,
        ),
        AnswerNode(
            start_pos = vec2(600, 300),
            things_to_average = [(vec2, vec2(600, 300), DIAGONAL(1, 1))],
            metric = None,
        ),
    ],
    distances = [
        AnswerDistance(0, 1, "L/2"),
        AnswerDistance(0, 2, "L"),
    ],
    forces = [
        AnswerForce(
            pos = 0,
            direction = DIRECTION(180),
            label = "A_H",
            metric = force_metric(bidirectional=True)
        ),
        AnswerForce(
            pos = 0,
            direction = DIRECTION(90),
            label = "A_V",
            metric = force_metric(bidirectional=True)
        ),
        AnswerForce(
            pos = 2,
            direction = DIRECTION(-90),
            label = "F_1",
            metric = force_metric()
        ),
        AnswerForce(
            pos = 1,
            direction = DIRECTION(90),
            label = "B_V",
            metric = force_metric()
        ),
    ],
    moments = [AnswerMoment(vec2(200, 300), False, "X", metric = moment_metric())],

    tolerance = 15,

    # not used yet, but the idea is that it provides information about
    # what symbols are part of the questions and which the student made up
    # TODO: implement this
    context = ...
)

# create image for question
# UNCOMMENT TO GENERATE NEW IMAGE
# skeleton1 = CoordRepr(
#     lines = [CoordLine(vec2(200, 300), vec2(600, 300))],
#     forces=[],
#     moments=[],
#     distances=[]
# )
# dwg = svgwrite.Drawing('questions/skeleton1.svg')
# skeleton1.draw(dwg)
# dwg.save()


# examples of functionality that exists
# dwg = svgwrite.Drawing('test.svg')
# eg3.draw(dwg)
# dwg.save()

#print(answer3.check_diagram(eg3))

#x = decode_JSON(load_JSON("./canvas-drawing.json"))    