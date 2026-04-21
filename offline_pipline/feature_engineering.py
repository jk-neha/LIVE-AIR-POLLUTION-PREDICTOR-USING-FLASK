# ================= Feature Engineering for PolluCast =================
import pandas as pd
import os

# ================= CONFIG =================
DATA_FOLDER = r"C:\Users\Neha\Neha's-DESKTOP\pollucast_api_res\1AQI\datasets"
INPUT_FILE = os.path.join(DATA_FOLDER, "3nungambakkam_final.csv")  # cleaned data after processing
OUTPUT_FILE = os.path.join(DATA_FOLDER, "4.0nungambakkam_features.csv")
# =========================================

# ---------------- Load Dataset ----------------
df = pd.read_csv(INPUT_FILE)

# Ensure timestamp is datetime
df['timestamp_ist'] = pd.to_datetime(df['timestamp_ist'])

# ---------------- Time Features ----------------
df['hour'] = df['timestamp_ist'].dt.hour
df['day'] = df['timestamp_ist'].dt.day
df['weekday'] = df['timestamp_ist'].dt.weekday  # 0 = Monday
df['month'] = df['timestamp_ist'].dt.month

# ---------------- Rolling / Moving Averages ----------------
pollutants = ['pm2_5', 'pm10', 'co', 'no', 'no2', 'o3', 'so2', 'nh3', 'temp_c', 'humidity']

# 3-hour rolling average (short-term trend)
for col in pollutants:
    df[f'{col}_3h_avg'] = df[col].rolling(window=3, min_periods=1).mean()

# 24-hour rolling average (long-term trend)
for col in pollutants:
    df[f'{col}_24h_avg'] = df[col].rolling(window=24, min_periods=1).mean()

# ---------------- Lag Features ----------------
# Lag values for pollutants and AQI (if available)
for col in pollutants:
    df[f'{col}_lag_1h'] = df[col].shift(1)
    df[f'{col}_lag_3h'] = df[col].shift(3)
    df[f'{col}_lag_24h'] = df[col].shift(24)

# Optional: If AQI column is present, create lag features
if 'AQI' in df.columns:
    df['AQI_lag_1h'] = df['AQI'].shift(1)
    df['AQI_lag_3h'] = df['AQI'].shift(3)
    df['AQI_lag_24h'] = df['AQI'].shift(24)

# ---------------- Fill Missing Values ----------------
# Fill any remaining NaNs after rolling/lag
df.fillna(method='bfill', inplace=True)
df.fillna(method='ffill', inplace=True)

# ---------------- Save Features ----------------
os.makedirs(DATA_FOLDER, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False)

print("✅ Feature engineering completed")
print(f"📊 Rows: {df.shape[0]} | Columns: {df.shape[1]}")
print(f"📁 File saved at: {OUTPUT_FILE}")
print(df.head())
