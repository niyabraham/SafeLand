# SafeLand
## AI-Based Flood Risk Prediction System for Kerala

SafeLand is a machine-learning-based system that predicts flood risk levels for specific locations in Kerala. Unlike traditional systems requiring manual data entry, SafeLand automates the process by fetching real-time environmental data based on location coordinates.

## 🚀 Features
- **Automated Data Collection:** Fetches Rainfall, Soil Moisture, and Elevation automatically using Open-Meteo APIs.
- **Location-Based:** Users simply provide Latitude & Longitude.
- **AI Prediction:** Uses a Random Forest Classifier to predict Flood Risk (Low / Medium / High).

## 🛠️ Tech Stack
- **Backend:** Python, Flask
- **ML:** Scikit-learn, Pandas, Joblib
- **External APIs:** Open-Meteo (Weather & Elevation)

## 📡 API Endpoints

### `POST /predict-by-location`
Accepts coordinates, fetches environmental data, and returns flood risk.

**Request:**
```json
{
  "latitude": 9.9312,
  "longitude": 76.2673
}