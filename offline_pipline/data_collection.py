import requests
import time
from datetime import datetime, timedelta, timezone
import pandas as pd
import os

# ================= CONFIG =================
API_KEY = "09f32567882a99651d51fd9064202419"
LOCATION_NAME = "Nungambakkam,Chennai,IN"

# ⚠️ MUST BE PAST OR PRESENT
START_IST_STR = "2025-08-23 23:25:58"
END_IST_STR   = "2026-01-04 23:59:59"

DATA_FOLDER = r"C:\Users\Neha\Neha's-DESKTOP\pollucast_api_res\1AQI\datasets"
# =========================================


# ================= TIME =================
def ist_to_utc_epoch(ist_str):
    ist = timezone(timedelta(hours=1, minutes=30))
    dt_ist = datetime.strptime(ist_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=ist)
    dt_utc = dt_ist.astimezone(timezone.utc)
    return int(dt_utc.timestamp()), dt_utc


# ================= GEO =================
def geocode_location(location, api_key):
    url = "http://api.openweathermap.org/geo/1.0/direct"
    r = requests.get(
        url,
        params={"q": location, "limit": 1, "appid": api_key},
        timeout=20
    )
    r.raise_for_status()
    data = r.json()

    if not data:
        raise ValueError("❌ Location not found")

    return float(data[0]["lat"]), float(data[0]["lon"])


# ================= AQI =================
def fetch_air_pollution_history(lat, lon, start_ts, end_ts, api_key, chunk_days=7):
    url = "http://api.openweathermap.org/data/2.5/air_pollution/history"
    rows = []

    step = chunk_days * 86400
    cur = start_ts

    while cur <= end_ts:
        cur_end = min(cur + step - 1, end_ts)
        print(f"🌫 AQI: {datetime.utcfromtimestamp(cur)} → {datetime.utcfromtimestamp(cur_end)}")

        r = requests.get(
            url,
            params={
                "lat": lat,
                "lon": lon,
                "start": cur,
                "end": cur_end,
                "appid": api_key
            },
            timeout=30
        )

        data = r.json()

        for item in data.get("list", []):
            ts = item["dt"]
            c = item["components"]

            rows.append({
                "timestamp_unix": ts,
                "timestamp_utc": pd.to_datetime(ts, unit="s"),
                "pm2_5": c.get("pm2_5"),
                "pm10": c.get("pm10"),
                "co": c.get("co"),
                "no": c.get("no"),
                "no2": c.get("no2"),
                "o3": c.get("o3"),
                "so2": c.get("so2"),
                "nh3": c.get("nh3"),
            })

        time.sleep(1)
        cur = cur_end + 1

    df = pd.DataFrame(rows)

    if not df.empty:
        df["timestamp_ist"] = df["timestamp_utc"] + timedelta(hours=5, minutes=30)
        df["date_hour"] = df["timestamp_utc"].dt.floor("h")

    return df


# ================= WEATHER =================
# def fetch_weather(lat, lon, df_aqi, api_key):
#     url = "https://api.openweathermap.org/data/3.0/onecall/timemachine"
#     rows = []

#     df_aqi["date_utc"] = df_aqi["timestamp_utc"].dt.floor("d")
#     unique_days = sorted(df_aqi["date_utc"].unique())
#     now_utc = pd.Timestamp.utcnow().tz_localize(None)

#     print(f"🌡 Weather days to fetch: {len(unique_days)}")

#     for day in unique_days:
#         if day > now_utc:
#             print(f"⏭ Skipping future date: {day.date()}")
#             continue

#         print(f"🌡 Weather for {day.date()}")
#         ts_day = int(pd.Timestamp(day).timestamp())

#         r = requests.get(
#             url,
#             params={
#                 "lat": lat,
#                 "lon": lon,
#                 "dt": ts_day,
#                 "appid": api_key,
#                 "units": "metric"
#             },
#             timeout=30
#         )

#         data = r.json()

#         for h in data.get("hourly", []):
#             rows.append({
#                 "timestamp_unix": h["dt"],
#                 "temp_c": h.get("temp"),
#                 "humidity": h.get("humidity"),
#             })

#         time.sleep(1)

#     df_weather = pd.DataFrame(rows)

#     if not df_weather.empty:
#         df_weather["timestamp_utc"] = pd.to_datetime(df_weather["timestamp_unix"], unit="s")
#         df_weather["date_hour"] = df_weather["timestamp_utc"].dt.floor("h")

#     return df_weather
def fetch_weather(lat, lon, df_aqi, api_key):
    url = "https://api.openweathermap.org/data/3.0/onecall/timemachine"
    rows = []

    df_aqi["date_utc"] = df_aqi["timestamp_utc"].dt.floor("d")
    unique_days = sorted(df_aqi["date_utc"].unique())
    now_utc = pd.Timestamp.utcnow().tz_localize(None)

    print(f"🌡 Weather days to fetch: {len(unique_days)}")

    for day in unique_days:
        if day > now_utc:
            print(f"⏭ Skipping future date: {day.date()}")
            continue

        print(f"🌡 Fetching weather for {day.date()}")
        ts_day = int(pd.Timestamp(day).timestamp())

        try:
            r = requests.get(
                url,
                params={
                    "lat": lat,
                    "lon": lon,
                    "dt": ts_day,
                    "appid": api_key,
                    "units": "metric"
                },
                timeout=30
            )
            data = r.json()
            for h in data.get("hourly", []):
                rows.append({
                    "timestamp_unix": h["dt"],
                    "temp_c": h.get("temp"),
                    "humidity": h.get("humidity"),
                })
        except Exception as e:
            print(f"⚠️ Error fetching weather for {day.date()}: {e}")

        time.sleep(1)

    # Always return a DataFrame with required columns
    df_weather = pd.DataFrame(rows)
    for col in ["timestamp_unix", "temp_c", "humidity"]:
        if col not in df_weather.columns:
            df_weather[col] = pd.NA

    if not df_weather.empty:
        df_weather["timestamp_utc"] = pd.to_datetime(df_weather["timestamp_unix"], unit="s")
        df_weather["date_hour"] = df_weather["timestamp_utc"].dt.floor("h")
    else:
        df_weather["date_hour"] = pd.Series(dtype="datetime64[ns]")

    return df_weather


# ================= MAIN =================
def main():
    lat, lon = geocode_location(LOCATION_NAME, API_KEY)

    start_ts, _ = ist_to_utc_epoch(START_IST_STR)
    end_ts, _ = ist_to_utc_epoch(END_IST_STR)

    df_aqi = fetch_air_pollution_history(lat, lon, start_ts, end_ts, API_KEY)

    if df_aqi.empty:
        print("❌ No AQI data fetched")
        return

    df_weather = fetch_weather(lat, lon, df_aqi, API_KEY)

    # ✅ SAFE HOURLY MERGE
    df = df_aqi.merge(
        df_weather[["date_hour", "temp_c", "humidity"]],
        on="date_hour",
        how="left"
    )

    df = df[
        [
            "timestamp_unix",
            "timestamp_utc",
            "timestamp_ist",
            "pm2_5",
            "pm10",
            "temp_c",
            "humidity",
            "co",
            "no",
            "no2",
            "o3",
            "so2",
            "nh3",
        ]
    ]

    os.makedirs(DATA_FOLDER, exist_ok=True)
    out_file = os.path.join(DATA_FOLDER, "1nungambakkam_raw.csv")
    df.to_csv(out_file, index=False)

    print("\n✅ COMPLETED SUCCESSFULLY")
    print(f"📊 Rows: {df.shape[0]} | Columns: {df.shape[1]}")
    print(f"📁 Saved to: {out_file}")


if __name__ == "__main__":
    main()
