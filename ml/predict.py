"""
Test the trained flood risk model on real Kerala locations.

This script tests the model on known flood-prone and safe areas in Kerala
to validate its predictions against historical flood events.
"""

import joblib
import pandas as pd
import os

# Paths
MODEL_PATH = os.path.join("ml", "flood_risk_model.pkl")
ENCODER_PATH = os.path.join("ml", "label_encoder.pkl")

# Load model and encoder
print("Loading model...")
model = joblib.load(MODEL_PATH)
encoder = joblib.load(ENCODER_PATH)
print("✓ Model loaded successfully")

def predict_risk(latitude, longitude, flooded_2018=0, flooded_2019=0, flooded_2021=0, flood_history_count=0):
    """
    Predict flood risk for a location.
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
        flooded_2018: 1 if flooded in 2018, 0 otherwise
        flooded_2019: 1 if flooded in 2019, 0 otherwise
        flooded_2021: 1 if flooded in 2021, 0 otherwise
        flood_history_count: Total number of times flooded (0-3)
    
    Returns:
        Predicted risk level (Low, Medium, High)
    """
    data = pd.DataFrame([{
        "latitude": latitude,
        "longitude": longitude,
        "flooded_2018": flooded_2018,
        "flooded_2019": flooded_2019,
        "flooded_2021": flooded_2021,
        "flood_history_count": flood_history_count
    }])
    
    prediction = model.predict(data)
    risk_label = encoder.inverse_transform(prediction)[0]
    
    # Get probability scores
    probabilities = model.predict_proba(data)[0]
    prob_dict = {encoder.classes_[i]: probabilities[i] for i in range(len(encoder.classes_))}
    
    return risk_label, prob_dict


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTING FLOOD RISK MODEL ON REAL KERALA LOCATIONS")
    print("="*60)
    
    # Test locations with known flood history
    test_locations = [
        {
            "name": "Kuttanad (2018 flood zone)",
            "lat": 9.6,
            "lon": 76.4,
            "flooded_2018": 1,
            "flooded_2019": 0,
            "flooded_2021": 0,
            "flood_count": 1,
            "expected": "Medium"
        },
        {
            "name": "Chengannur (2018 severely flooded)",
            "lat": 9.32,
            "lon": 76.62,
            "flooded_2018": 1,
            "flooded_2019": 0,
            "flooded_2021": 0,
            "flood_count": 1,
            "expected": "Medium"
        },
        {
            "name": "Wayanad hills (safe, high elevation)",
            "lat": 11.6,
            "lon": 76.1,
            "flooded_2018": 0,
            "flooded_2019": 0,
            "flooded_2021": 0,
            "flood_count": 0,
            "expected": "Low"
        },
        {
            "name": "Thiruvananthapuram (coastal, safer)",
            "lat": 8.5,
            "lon": 76.9,
            "flooded_2018": 0,
            "flooded_2019": 0,
            "flooded_2021": 0,
            "flood_count": 0,
            "expected": "Low"
        },
        {
            "name": "Aluva (2018 & 2019 flooded)",
            "lat": 10.1,
            "lon": 76.35,
            "flooded_2018": 1,
            "flooded_2019": 1,
            "flooded_2021": 0,
            "flood_count": 2,
            "expected": "High"
        },
        {
            "name": "Kochi (moderate risk)",
            "lat": 9.93,
            "lon": 76.27,
            "flooded_2018": 0,
            "flooded_2019": 1,
            "flooded_2021": 0,
            "flood_count": 1,
            "expected": "Medium"
        },
        {
            "name": "Idukki (mountainous, safe)",
            "lat": 9.85,
            "lon": 77.1,
            "flooded_2018": 0,
            "flooded_2019": 0,
            "flooded_2021": 0,
            "flood_count": 0,
            "expected": "Low"
        },
        {
            "name": "Pathanamthitta (2018 flood zone)",
            "lat": 9.27,
            "lon": 76.79,
            "flooded_2018": 1,
            "flooded_2019": 0,
            "flooded_2021": 0,
            "flood_count": 1,
            "expected": "Medium"
        }
    ]
    
    print("\nTesting on known locations:\n")
    
    correct = 0
    total = len(test_locations)
    
    for loc in test_locations:
        risk, probabilities = predict_risk(
            latitude=loc["lat"],
            longitude=loc["lon"],
            flooded_2018=loc["flooded_2018"],
            flooded_2019=loc["flooded_2019"],
            flooded_2021=loc["flooded_2021"],
            flood_history_count=loc["flood_count"]
        )
        
        is_correct = risk == loc["expected"]
        correct += is_correct
        
        status = "✓" if is_correct else "✗"
        
        print(f"{status} {loc['name']}")
        print(f"   Location: ({loc['lat']:.2f}, {loc['lon']:.2f})")
        print(f"   Flood history: {loc['flood_count']} events")
        print(f"   Expected: {loc['expected']}")
        print(f"   Predicted: {risk}")
        print(f"   Confidence: Low={probabilities.get('Low', 0):.1%}, "
              f"Medium={probabilities.get('Medium', 0):.1%}, "
              f"High={probabilities.get('High', 0):.1%}")
        print()
    
    accuracy = (correct / total) * 100
    
    print("="*60)
    print(f"RESULTS: {correct}/{total} correct predictions ({accuracy:.1f}% accuracy)")
    print("="*60)
    
    # Interactive testing
    print("\n" + "="*60)
    print("INTERACTIVE TESTING")
    print("="*60)
    print("\nYou can now test any location in Kerala.")
    print("Enter coordinates and flood history to get a prediction.\n")
    
    try:
        while True:
            print("-" * 40)
            lat = float(input("Enter latitude (8-13): "))
            lon = float(input("Enter longitude (74-78): "))
            
            print("\nFlood history (enter 1 if flooded, 0 if not):")
            f2018 = int(input("  Flooded in 2018? (0/1): "))
            f2019 = int(input("  Flooded in 2019? (0/1): "))
            f2021 = int(input("  Flooded in 2021? (0/1): "))
            
            flood_count = f2018 + f2019 + f2021
            
            risk, probabilities = predict_risk(lat, lon, f2018, f2019, f2021, flood_count)
            
            print(f"\n📍 Location: ({lat}, {lon})")
            print(f"🌊 Flood history: {flood_count} events")
            print(f"⚠️  Predicted Risk: {risk}")
            print(f"📊 Confidence:")
            for risk_level, prob in probabilities.items():
                print(f"   {risk_level}: {prob:.1%}")
            print()
            
            cont = input("Test another location? (y/n): ")
            if cont.lower() != 'y':
                break
    except KeyboardInterrupt:
        print("\n\nTesting stopped.")
    except Exception as e:
        print(f"\nError: {e}")
    
    print("\nThank you for testing!")
