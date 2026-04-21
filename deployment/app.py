from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# ================= LOAD MODEL =================
model = joblib.load("model.pkl")

# ================= AQI CATEGORY =================
def aqi_category(aqi):
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Satisfactory"
    elif aqi <= 200:
        return "Moderate"
    elif aqi <= 300:
        return "Poor"
    elif aqi <= 400:
        return "Very Poor"
    else:
        return "Severe"

# ================= HOME ROUTE =================
@app.route("/")
def home():
    return jsonify({
        "message": "🌫 PolluCast API is Running",
        "usage": "/predict endpoint"
    })

# ================= PREDICT ROUTE =================
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        # Input features (same order as training)
        pm2_5 = data["pm2_5"]
        pm10 = data["pm10"]
        co = data["co"]
        no = data["no"]
        no2 = data["no2"]
        o3 = data["o3"]
        so2 = data["so2"]
        nh3 = data["nh3"]
        temp_c = data["temp_c"]
        humidity = data["humidity"]

        # Feature array
        features = np.array([[pm2_5, pm10, co, no, no2, o3, so2, nh3, temp_c, humidity]])

        # Prediction
        prediction = model.predict(features)[0]
        category = aqi_category(prediction)

        return jsonify({
            "AQI": round(float(prediction), 2),
            "Category": category
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        })

# ================= RUN APP =================
if __name__ == "__main__":
    app.run(debug=True)
