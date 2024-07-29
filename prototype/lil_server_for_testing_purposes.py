from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import numpy as np
from judge import *
import testing

app = Flask(__name__)
CORS(app)

def judge(diagram):
    # Process the diagram and return feedback
    ans = testing.answer3
    score = ans.check_diagram(diagram)
    feedback = f"This is a feedback message based on the diagram. {score}"
    return feedback

@app.route('/upload', methods=['POST'])
def judge_diagram():
    data = request.json
    diagram = decode_JSON(data)
    feedback = judge(diagram)
    return jsonify({'feedback': feedback})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)