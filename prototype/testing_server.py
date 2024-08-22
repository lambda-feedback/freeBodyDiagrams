# Run this file to start the testing server.

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import numpy as np
from evaluation import *
import testing

app = Flask(__name__)
CORS(app)

def judge(diagram):
    # Process the diagram and return feedback
    ans = testing.answer3
    feedback = ans.check_diagram(diagram)
    return jsonify({'feedback': f"""score: {feedback.score} <br>
surplus forces: {feedback.surplus_forces} <br>
surplus moments: {feedback.surplus_moments} <br>
distances: """ + feedback.distance_feedback,
        'warnings': [{'x': warning.pos[0], 'y': warning.pos[1], 'message': warning.message} for warning in feedback.warnings]
    })
            

@app.route('/upload', methods=['POST'])
def judge_diagram():
    data = request.json
    diagram = decode_JSON(data)
    return judge(diagram)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)