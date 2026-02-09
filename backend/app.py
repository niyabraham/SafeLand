from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

MODEL_PATH = os.path.join("ml", "flood_risk_model.pkl")
ENCODER_PATH = os.path.join("ml", "label_encoder.pkl")

model = joblib.load(MODEL_PATH)
encoder = joblib.load(ENCODER_PATH)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    required_fields = [
        "rainfall",
        "water_level",
        "elevation",
        "soil_moisture",
        "river_distance"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    df = pd.DataFrame([data])
    prediction = model.predict(df)
    risk = encoder.inverse_transform(prediction)[0]

    return jsonify({"flood_risk": risk})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "Backend is running"})


if __name__ == "__main__":
    app.run(debug=True)
