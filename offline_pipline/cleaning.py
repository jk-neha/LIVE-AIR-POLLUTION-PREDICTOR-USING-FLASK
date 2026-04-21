import pandas as pd
import numpy as np

# Load raw data
df = pd.read_csv(r"C:\Users\Neha\Neha's-DESKTOP\pollucast_api_res\1AQI\datasets\1nungambakkam_raw.csv")

# ------------------------
# 1. Handle missing weather
# ------------------------
df['temp_c'] = df['temp_c'].interpolate(method='linear').bfill().ffill()
df['humidity'] = df['humidity'].interpolate(method='linear').bfill().ffill()

# ------------------------
# 2. Handle missing pollutants
# ------------------------
pollutants = ['pm2_5','pm10','co','no','no2','o3','so2','nh3']
df[pollutants] = df[pollutants].interpolate(method='linear').bfill().ffill()

# ------------------------
# 3. Remove duplicates
# ------------------------
df.drop_duplicates(subset='timestamp_unix', inplace=True)

# ------------------------
# 4. Clip extreme outliers (IQR method)
# ------------------------
for col in pollutants:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    df[col] = df[col].clip(lower, upper)

# ------------------------
# 5. Optional: reset index
# ------------------------
df.reset_index(drop=True, inplace=True)

# Save cleaned data
df.to_csv(r"C:\Users\Neha\Neha's-DESKTOP\pollucast_api_res\1AQI\datasets\2nungambakkam_cleaned.csv", index=False)

print("✅ Cleaning completed")
print(df.head())
