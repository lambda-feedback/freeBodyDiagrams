# Evalation function for free body diagrams
(please see template_README.md for original README message) \
I will label any **loose ends** in bold, which you are free to remove after implementing or dismissing.


## What we have so far and what is missing
There is a website, called testing_canvas.html, which allows the user to draw a free body diagram.
This website requires you to run the Flask server, called lil_server_for_testing_purposes.html.
 - There is a basic scoring system implemented. This works using the hungarian algorithm. I have custom metrics to determine how different an arrow is to it's target configuration. These are customisable, with more details in judge.py.
 - The website has some basic feedback implemented.
    - **The score is not accurate when there are no arrows or moments drawn.**
    - There are details about how many moments are expected and how many forces are expected.
    - The score is visible.
    - When an answer label and anoth label do not match up, there is an extra fixed distance added to the metric.
    - There are **warnings, that tell the user where the biggest problem is**. The information from the hungarian algorithm is enough for you to figure out what force, etc is causing the problem and relay it to the user.
 - I will now explain my plan to **handle distances**. Only some of this is implemented.
    - I am currently restricting myself to verifying distance markers that all lie on a line. The plan is as follows:
        - **Identify the key points on the diagram that the distance markers need to reference and match up with answer**. These are for example the end-points and the position where a force is applied.
        - Encode each of these nodes as a position on a line.
        - This means a distance marker between two nodes, A and B, of length 2m, is encoded as B - A = 2.
        - All of these equations from all the distance markers can be **put into matrix form** and we look at the RRE form and compare it with the answer.

## Image recognition stuff
The idea is that a user can draw, by hand, a diagram, and then this is converted into our internal representation. \
This is one big loose end, so I will lay out what I have looked at so far:
 - **YOLOv9** seems like a good way to detect the arrows.
 - When you set it up, it is important to keep information such as which direction the arrows are facing, and where the arrow head is, because a simple bounding box is not enough.
 - There might be an open-source model out there already that lets you do all this, but I haven't found it.
 - Most of the difficulty comes from **creating and labelling training data**.
 - My plan was to **create a website that displays arrows (etc), and then asks the users to draw over them, and then creates training data from that**. I have started work on that, but there is an alternative (see next point).
 - There is a website, **roboflow**, which claims to provide tools to help label the data and build/train the model, even going so far as labelling it automatically. You may need to **look into the liscence**, as it is not for commercial use.