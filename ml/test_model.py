"""
Simple automated test of the flood risk model on real Kerala locations.
"""

import joblib
import pandas as pd
import os

# Load model
model = joblib.load(os.path.join("ml", "flood_risk_model.pkl"))
encoder = joblib.load(os.path.join("ml", "label_encoder.pkl"))

print("="*60)
print("FLOOD RISK MODEL - AUTOMATED TESTS")
print("="*60)

# Test locations
tests = [
    ("Kuttanad (2018 flooded)", 9.6, 76.4, 1, 0, 0, 1, "Medium"),
    ("Chengannur (2018 flooded)", 9.32, 76.62, 1, 0, 0, 1, "Medium"),
    ("Wayanad hills (safe)", 11.6, 76.1, 0, 0, 0, 0, "Low"),
    ("Thiruvananthapuram (safe)", 8.5, 76.9, 0, 0, 0, 0, "Low"),
    ("Aluva (2018 & 2019)", 10.1, 76.35, 1, 1, 0, 2, "High"),
    ("Kochi (2019 flooded)", 9.93, 76.27, 0, 1, 0, 1, "Medium"),
    ("Idukki (safe)", 9.85, 77.1, 0, 0, 0, 0, "Low"),
    ("Pathanamthitta (2018)", 9.27, 76.79, 1, 0, 0, 1, "Medium"),
]

correct = 0
print("\nTest Results:\n")

for name, lat, lon, f18, f19, f21, count, expected in tests:
    data = pd.DataFrame([{
        "latitude": lat,
        "longitude": lon,
        "flooded_2018": f18,
        "flooded_2019": f19,
        "flooded_2021": f21,
        "flood_history_count": count
    }])
    
    pred = model.predict(data)[0]
    risk = encoder.inverse_transform([pred])[0]
    probs = model.predict_proba(data)[0]
    
    is_correct = risk == expected
    correct += is_correct
    status = "✓" if is_correct else "✗"
    
    print(f"{status} {name}")
    print(f"   Expected: {expected}, Predicted: {risk}")
    print(f"   Confidence: L={probs[0]:.1%} M={probs[1]:.1%} H={probs[2] if len(probs)>2 else 0:.1%}")
    print()

accuracy = (correct / len(tests)) * 100
print("="*60)
print(f"Accuracy: {correct}/{len(tests)} ({accuracy:.1f}%)")
print("="*60)
