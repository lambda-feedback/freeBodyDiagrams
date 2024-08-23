# Evalation function for free body diagrams
(please see template_README.md for original README message) \

## Quick explanation of free body diagrams
A FBD illustrates the forces acting on a single object or system, isolated from its surroundings. The forces and moments acting on the object are all drawn. It is important that the distances are labelled correctly.

## High-level overview of features
- There is a website that the user can use to draw (arrows only) free body diagrams over a background image (the beam in this case)
- The backend gives feedback to the user, including:
   - A score, which we want to minimise (if it's less than 0 the diagram is accepted)
   - Excess forces
   - Excess moments
   - Whether or not the user-drawn distances are correct or not
   - Warnings signs at places where there is something wrong, along with text to the side *
- There is a tool to dynamically generate questions *
- There are representations of user-drawn diagrams and model answers
- There is functionality to display user-drawn diagrams as an svg, but this is not maintained and probably missing a lot of features
- There is a website that allows the user to draw over a background image (like using a pen) and will save their answer as a png
- Karl has provided two files involved with comparing the RRE form of matrices (but with symbolic entries), and these are used in checking distances

## Explanation of evaluation function algorithm
The class `AnswerDiagram` contains the following:
- a list of `AnswerForce`
- a list of `AnswerMoment`
- a list of `AnswerDistance`
- tolerance, which is subtracted from the total cost at the end

First, the Hungarian algorithm is used to match up the target forces with the user's forces. The weights are determined by customisable metrics. This is repeated for moments. \
Next, we recalculate the positions of the `AnswerNode`s, to which the forces' positions are tied. This is done by doing a weighted average of fixed vectors and forces, weighted by matrices for further flexibility. Then we do the hungarian algorithm again, as the nodes have shifted. This is done once more for good luck. \
We use the matchings to calculate the score, combining individual scores with the l4 norm (perhaps max is better idk). Then we move on to distance markers. \
We match each endpoint of each distance marker to the closest node. Then we treat each node as a variable (x0, x1, ..., xn). A distance marker from node 2 to node 3 of length L is represented as x3 - x2 = L. Doing this for each distance marker gets us a system of equations, which we put in matrix form. We then compare the span of all the equations with the span of the model answer. \
Finally, we add a punishment to the score for excess/too few forces or moments.


## How to use `question_maker.py`
to be written when it is finished

## Purpose of some files
- canvas-drawing.json just serves as an example and can be deleted
- drawing_canvas.html lets the user draw over a background image in a way that mimics a pen
- test.svg is generated as a test and can be ignored or deleted
- questions/skeleton1.svg is used as a background image

## Known bugs, loose ends and possible features
- Warnings signs do not always show up when necessary (they are currently only implemented for forces).
- Warnings signs could show better messages, perhaps customisable.
- BUG: Currently nodes have flexible positions, however there is nothing ensuring that nodes are in the right relative positions. It is entirely possible that the user swaps the positions of two nodes and still gets their diagram marked as right.
- BUG: Nodes can be located off the edge of the beam.
- Currently the weighted average to calculate each node's position does not take into account moments.
- BUG: currently distance markers are checked by determining the nearest node to each endpoint. This is a problem as we can have very "slanted" or inaccurate distance markers still being marked as correct. Perhaps calculate the vectors from the endpoints to their respective nodes and compare them?
- The `question_maker.py` file is currently not finished. *
- The question maker does not support shapes other than straight lines.
- The handling of moments needs some tweaking. Currently moments are stored as arrows, but they should probably be stored as a singular point, with an associated label, as that is how they are used. Also they could be tied to nodes.
- BUG: If a force is facing into the beam instead of away from it, it is currently not counted as correct, but it should be.
- TODO: make better use of customisable metrics (you can specify a matrix but it is always the same right now)

## Image recognition stuff
The idea is that a user can draw, by hand, a diagram, and then this is converted into our internal representation. \
This is one big loose end, so I will lay out what I have looked at so far:
 - **YOLOv9** seems like a good way to detect the arrows.
 - When you set it up, it is important to keep information such as which direction the arrows are facing, and where the arrow head is, because a simple bounding box is not enough.
 - There might be an open-source model out there already that lets you do all this, but I haven't found it.
 - Most of the difficulty comes from **creating and labelling training data**.
 - My plan was to **create a website that displays arrows (etc), and then asks the users to draw over them, and then creates training data from that**. I have started work on that, but there is an alternative (see next point).
 - There is a website, **roboflow**, which claims to provide tools to help label the data and build/train the model, even going so far as labelling it automatically. You may need to **look into the licence**, as it is not for commercial use.
 - potentially useful: [opencv.org](https://opencv.org/)

## Guide to using testing server
- Install prerequesites by just doing `pip install -r requirements.txt`
- Run `python testing_server` to set up the server
- Open up the file `arrow_canvas.html` in your browser
- Draw/move arrows using left mouse button and delete using right mouse button
- You should now get live feedback every second
- The target answer is stored in questions.py

## Guide to adding new feature (distributed loads):
- Let us suppose, for simplicity, our distributed load is constant
- Add a new type of arrow to `arrow_canvas.html`, along with code to render and draw it
- Add a `CoordDistributedLoad` class to `representation.py` to store information about what the user drew (using coordinates), such as
   - Start point
   - End point
   - Load label
   - Load direction
- Add an `AnswerDistributedLoad` class to `evaluation.py` to store the model answer
- Store some `CoordDistributedLoad`s in `CoordRepr` and  `AnswerDistributedLoad`s in `AnswerDiagram`
- Add a `distributed_load_metric` to `evaluation.py`, perhaps with some customisable parameters
- Modify `AnswerDiagram.check_diagram()`so that it compares the distributed loads the user drew with the model answer
   - You can use `hungarian(target, ans)` where target is a list of `AnswerDistributedLoad` and ans is a list of `CoordDistributedLoad`
   - Note that everything in target must have a `dist(x)` function (that uses the metric to find the 'distance' from x)
   - `hungarian` will return a tuple: cost_matrix, row_ind, col_ind
      - `cost_matrix` is just the matrix of costs
      - `zip(row_ind, col_ind)` gives you a list of matchings
