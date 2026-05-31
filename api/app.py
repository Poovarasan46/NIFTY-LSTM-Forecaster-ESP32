from flask import Flask, jsonify

import os
import csv

from datetime import datetime

from training.predict import get_prediction

app = Flask(__name__)

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

PREDICTIONS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "predictions.csv"
)

# Create file if missing

if not os.path.exists(
    PREDICTIONS_FILE
):
    with open(
        PREDICTIONS_FILE,
        "w",
        newline=""
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "Timestamp",
            "Current",
            "Predicted",
            "Trend",
            "Confidence"
        ])


@app.route("/")
def home():

    return jsonify({
        "status":
            "running",

        "message":
            "NIFTY Predictor API"
    })


@app.route("/predict")
def predict():

    result = get_prediction()

    with open(
        PREDICTIONS_FILE,
        "a",
        newline=""
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            datetime.now(),

            result["current"],

            result["predicted"],

            result["trend"],

            result["confidence"]
        ])

    return jsonify(
        result
    )


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )