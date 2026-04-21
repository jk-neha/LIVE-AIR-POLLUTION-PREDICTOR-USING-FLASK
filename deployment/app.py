from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# Load trained model
model = joblib.load("model.pkl")

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

@app.route("/")
def home():
    return jsonify({"message": "PolluCast API Running 🚀"})

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    features = np.array([[
        data["pm2_5"],
        data["pm10"],
        data["co"],
        data["no"],
        data["no2"],
        data["o3"],
        data["so2"],
        data["nh3"],
        data["temp_c"],
        data["humidity"]
    ]])

    prediction = model.predict(features)[0]

    return jsonify({
        "AQI": round(float(prediction), 2),
        "Category": aqi_category(prediction)
    })

if __name__ == "__main__":
    app.run()
