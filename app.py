from flask import Flask, jsonify, request
from flask_cors import CORS

app =  Flask(__name__)

CORS(app, resources = {r"/evaluate/*": {"origins": "http://localhost:3000"}})

@app.route('/evaluate', methods=['POST'])
def evaluate():

    metrics = {"overall": 100,"clarity": 90, "accuracy": 88}
    return jsonify(metrics)


if __name__ == '__main__':
    app.run()
