from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import os
import requests

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
# Get the absolute path to the backend folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Go UP one level ("..") to find the 'ml' folder
MODEL_PATH = os.path.join(BASE_DIR, "..", "ml", "flood_risk_model.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "..", "ml", "label_encoder.pkl")

# --- LOAD MODEL ---
if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
    model = joblib.load(MODEL_PATH)
    encoder = joblib.load(ENCODER_PATH)
    print("✅ Model loaded successfully.")
else:
    model = None
    encoder = None
    print("⚠️ Model files not found. Please train the model first.")

# --- HELPER FUNCTION: Fetch Data from APIs ---
def fetch_environmental_data(lat, lon):
    try:
        # 1. Fetch Rainfall (Open-Meteo Weather API)
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "precipitation_sum",
            "hourly": "soil_moisture_0_to_1cm",
            "timezone": "auto",
            "forecast_days": 1
        }
        resp = requests.get(weather_url, params=weather_params)
        data = resp.json()
        
        rainfall = data.get("daily", {}).get("precipitation_sum", [0])[0]
        soil_moisture_raw = data.get("hourly", {}).get("soil_moisture_0_to_1cm", [0])[0]
        soil_moisture = soil_moisture_raw * 100  # Scale to 0-100

        # 2. Fetch Elevation (Open-Meteo Elevation API)
        elev_url = "https://api.open-meteo.com/v1/elevation"
        elev_params = {"latitude": lat, "longitude": lon}
        elev_resp = requests.get(elev_url, params=elev_params)
        elevation = elev_resp.json().get("elevation", [0])[0]

        return rainfall, soil_moisture, elevation

    except Exception as e:
        print(f"API Error: {e}")
        return 50.0, 40.0, 10.0  # Default fallback values

# --- API ENDPOINT ---
@app.route("/predict-by-location", methods=["POST"])
def predict_by_location():
    if not model:
        return jsonify({"error": "Model not loaded"}), 500

    data = request.json
    lat = data.get("latitude")
    lon = data.get("longitude")

    if lat is None or lon is None:
        return jsonify({"error": "Latitude and Longitude are required"}), 400

    print(f"📍 Request received for: {lat}, {lon}")

    # 1. Get Real Data
    rainfall, soil_moisture, elevation = fetch_environmental_data(lat, lon)

    # 2. Calculate Derived Features (Mock logic for now)
    water_level = 1.0 + (rainfall / 50.0)
    river_distance = 2.0  # Safe default distance

    features = {
        "rainfall": rainfall,
        "water_level": water_level,
        "elevation": elevation,
        "soil_moisture": soil_moisture,
        "river_distance": river_distance
    }

    # 3. Predict
    df = pd.DataFrame([features])
    prediction_idx = model.predict(df)[0]
    risk_label = encoder.inverse_transform([prediction_idx])[0]

    return jsonify({
        "location": {"lat": lat, "lon": lon},
        "environmental_data": features,
        "flood_risk": risk_label
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "Backend is running"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)