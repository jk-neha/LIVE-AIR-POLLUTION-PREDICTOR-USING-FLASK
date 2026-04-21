# 6model_training.py
import pandas as pd
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import numpy as np

# ================= CONFIG =================
DATA_FOLDER = r"C:\Users\Neha\Neha's-DESKTOP\pollucast_api_res\1AQI\datasets"
WITH_PM_FILE = os.path.join(DATA_FOLDER, "4.1nungambakkam_aqi_with_pm.csv")
WITHOUT_PM_FILE = os.path.join(DATA_FOLDER, "4.11nungambakkam_aqi_without_pm.csv")
MODEL_FOLDER = os.path.join(r"C:\Users\Neha\Neha's-DESKTOP\pollucast_api_res\1AQI\modelsrfgb")
os.makedirs(MODEL_FOLDER, exist_ok=True)
# =========================================

def train_and_evaluate(df, name_suffix):
    # 1️⃣ Features and target
    X = df.drop(columns=["timestamp_unix","timestamp_utc","timestamp_ist","AQI"])
    y = df["AQI"]
    
    # Convert any remaining object columns to numeric if necessary
    X = X.apply(pd.to_numeric, errors='coerce').fillna(0)
    
    # 2️⃣ Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 3️⃣ Train Random Forest
    model = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42)
    model.fit(X_train, y_train)
    
    # 4️⃣ Predictions
    y_pred = model.predict(X_test)
    
    # 5️⃣ Evaluation
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print(f"\n📊 Model: {name_suffix}")
    print(f"MAE : {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"R2  : {r2:.2f}")
    
    # 6️⃣ Save model
    model_file = os.path.join(MODEL_FOLDER, f"rf_model_{name_suffix}.pkl")
    joblib.dump(model, model_file)
    print(f"✅ Model saved: {model_file}")

def main():
    # ================= WITH PM FEATURES =================
    df_with_pm = pd.read_csv(WITH_PM_FILE)
    train_and_evaluate(df_with_pm, "with_pm")
    
    # ================= WITHOUT PM FEATURES =================
    df_no_pm = pd.read_csv(WITHOUT_PM_FILE)
    train_and_evaluate(df_no_pm, "without_pm")

if __name__ == "__main__":
    main()
