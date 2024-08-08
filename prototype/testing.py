from judge import *

# test on example 3
eg3 = CoordRepr(
    lines = [CoordLine(vec2(202, 283), vec2(627, 283))],
    forces = [
        CoordForce(
            pos = vec2(202, 283),
            direction = DIRECTION(180),
            label = "A_H",
        ),
        CoordForce(
            pos = vec2(202, 283),
            direction = vec2(0.05, 0.99),
            label = "A_V",
        ),
        CoordForce(
            pos = vec2(627, 283),
            direction = DIRECTION(-90),
            label = "F_1",
        ),
        CoordForce(
            pos = vec2(415, 283),
            direction = DIRECTION(90),
            label = "B_v",
        ),
    ],
    moments = [CoordMoment(vec2(415, 283), False, "X")],
    distances = [
        CoordDistance(
            line = CoordLine(vec2(202, 287), vec2(415, 287)),
            label = "L/2"
        ),
        CoordDistance(
            line = CoordLine(vec2(415, 291), vec2(627, 291)),
            label = "L/2"
        ),
    ]
)

answer3 = AnswerDiagram(
    # hard-coded values for now
    nodes = [
        AnswerNode(
            pos = vec2(202, 283),
        ),
        AnswerNode(
            pos = vec2(415, 283),
        ),
        AnswerNode(
            pos = vec2(627, 283),
        ),
    ],
    distances = [
        AnswerDistance(0, 1, "L/2"),
        AnswerDistance(0, 2, "L"),
    ],
    forces = [
        AnswerForce(
            pos = vec2(202, 283),
            direction = DIRECTION(180),
            label = "A_H",
            metric = force_metric(bidirectional=True)
        ),
        AnswerForce(
            pos = vec2(202, 283),
            direction = DIRECTION(90),
            label = "A_V",
            metric = force_metric(bidirectional=True)
        ),
        AnswerForce(
            pos = vec2(627, 283),
            direction = DIRECTION(-90),
            label = "F_1",
            metric = force_metric()
        ),
        AnswerForce(
            pos = vec2(415, 283),
            direction = DIRECTION(90),
            label = "B_v",
            metric = force_metric()
        ),
    ],
    moments = [AnswerMoment(vec2(415, 283), False, "X", metric = moment_metric())],

    tolerance = 15,

    # not used yet, but the idea is that it provides information about
    # what symbols are part of the questions and which the student made up
    # TODO: implement this
    context = ...
)

skeleton1 = CoordRepr(
    lines = [CoordLine(vec2(202, 283), vec2(627, 283))],
    forces=[],
    moments=[],
    distances=[]
)
dwg = svgwrite.Drawing('questions/skeleton1.svg')
skeleton1.draw(dwg)
dwg.save()

# dwg = svgwrite.Drawing('test.svg')
# eg3.draw(dwg)
# dwg.save()

#print(answer3.check_diagram(eg3))

#x = decode_JSON(load_JSON("./canvas-drawing.json"))    