from flask import Flask, render_template, jsonify
import random
import pandas as pd
import datetime
from sklearn.linear_model import LinearRegression
import numpy as np
import collections
import requests
from cachetools import TTLCache

app = Flask(__name__)

MAX_READINGS = 100
data = collections.deque(maxlen=MAX_READINGS)
district_cache = TTLCache(maxsize=100, ttl=300) # Cache for 5 minutes

# Rajasthan districts with base AQI levels (for simulation realism)
RAJASTHAN_DISTRICTS = [
    {"name": "Jaipur",      "lat": 26.9124, "lon": 75.7873, "base": 140},
    {"name": "Jodhpur",     "lat": 26.2389, "lon": 73.0243, "base": 110},
    {"name": "Kota",        "lat": 25.2138, "lon": 75.8648, "base": 160},
    {"name": "Bikaner",     "lat": 28.0229, "lon": 73.3119, "base":  90},
    {"name": "Ajmer",       "lat": 26.4499, "lon": 74.6399, "base": 120},
    {"name": "Udaipur",     "lat": 24.5854, "lon": 73.7125, "base":  75},
    {"name": "Bhilwara",    "lat": 25.3561, "lon": 74.6367, "base": 130},
    {"name": "Alwar",       "lat": 27.5530, "lon": 76.6346, "base": 155},
    {"name": "Bharatpur",   "lat": 27.2152, "lon": 77.5030, "base": 145},
    {"name": "Nagaur",      "lat": 27.2018, "lon": 73.7338, "base":  85},
    {"name": "Sikar",       "lat": 27.6094, "lon": 75.1399, "base": 100},
    {"name": "Pali",        "lat": 25.7711, "lon": 73.3234, "base":  95},
    {"name": "Barmer",      "lat": 25.7463, "lon": 71.3917, "base":  70},
    {"name": "Chittorgarh", "lat": 24.8888, "lon": 74.6269, "base": 115},
    {"name": "Jhunjhunu",   "lat": 28.1289, "lon": 75.3997, "base": 105},
    {"name": "Tonk",        "lat": 26.1662, "lon": 75.7885, "base": 125},
    {"name": "Swai Madhopur","lat":26.0139, "lon": 76.3541, "base":  88},
    {"name": "Bundi",       "lat": 25.4384, "lon": 75.6394, "base":  92},
    {"name": "Dholpur",     "lat": 26.6999, "lon": 77.8935, "base": 170},
    {"name": "Sirohi",      "lat": 24.8847, "lon": 72.8616, "base":  65},
    {"name": "Jaisalmer",   "lat": 26.9157, "lon": 70.9083, "base":  55},
    {"name": "Hanumangarh", "lat": 29.5810, "lon": 74.3299, "base": 118},
    {"name": "Ganganagar",  "lat": 29.9038, "lon": 73.8772, "base": 112},
    {"name": "Churu",       "lat": 28.2957, "lon": 74.9685, "base":  98},
    {"name": "Jhalawar",    "lat": 24.5980, "lon": 76.1647, "base":  82},
    {"name": "Baran",       "lat": 25.1043, "lon": 76.5145, "base":  88},
    {"name": "Dausa",       "lat": 26.8816, "lon": 76.3350, "base": 135},
    {"name": "Karauli",     "lat": 26.5023, "lon": 77.0220, "base": 125},
    {"name": "Rajsamand",   "lat": 25.0701, "lon": 73.8843, "base":  80},
    {"name": "Dungarpur",   "lat": 23.8437, "lon": 73.7122, "base":  68},
    {"name": "Banswara",    "lat": 23.5468, "lon": 74.4393, "base":  62},
    {"name": "Pratapgarh",  "lat": 24.0328, "lon": 74.7782, "base":  72},
    {"name": "Jalor",       "lat": 25.3461, "lon": 72.6166, "base":  78},
]


def fetch_real_aqi_data(lat, lon):
    """Fetch real-time air quality data from Open-Meteo Air Quality API."""
    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=pm2_5,pm10,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        current = data.get("current", {})
        
        # Open-Meteo gives CO in ug/m3, we convert to ppm for the UI (approx / 1150)
        co_ug = current.get("carbon_monoxide", 0)
        co_ppm = round(co_ug / 1150.0, 1) if co_ug else 0
        
        return {
            "aqi": current.get("us_aqi", 0),
            "pm25": current.get("pm2_5", 0),
            "co2": current.get("carbon_monoxide", 0), # Using CO as a proxy for CO2 if not available
            "pm10": current.get("pm10", 0),
            "no2": current.get("nitrogen_dioxide", 0),
            "so2": current.get("sulphur_dioxide", 0),
            "o3": current.get("ozone", 0)
        }
    except Exception as e:
        print(f"Error fetching real data: {e}")
        return None


def district_reading(district):
    """Get a reading for a specific district using real API data (with caching)."""
    name = district["name"]
    if name in district_cache:
        return district_cache[name]

    real_data = fetch_real_aqi_data(district["lat"], district["lon"])
    
    if real_data:
        reading = {
            "name": name,
            "lat":  district["lat"],
            "lon":  district["lon"],
            "aqi":  int(real_data["aqi"]),
            "pm25": real_data["pm25"],
            "co2":  int(real_data["co2"]), # This is CO in the API, we keep it as CO2 in our variable name
        }
    else:
        # Fallback to simulation if API fails
        base = district["base"]
        aqi  = int(np.clip(base + random.randint(-25, 40), 20, 400))
        pm25 = round(aqi * random.uniform(0.35, 0.55), 1)
        co2  = random.randint(300, 900)
        reading = {
            "name": name,
            "lat":  district["lat"],
            "lon":  district["lon"],
            "aqi":  aqi,
            "pm25": pm25,
            "co2":  co2,
        }
    
    district_cache[name] = reading
    return reading


def generate_reading():
    """Generate a reading for the default dashboard location (Jaipur)."""
    jaipur = RAJASTHAN_DISTRICTS[0] # Jaipur
    real_data = fetch_real_aqi_data(jaipur["lat"], jaipur["lon"])
    
    if real_data:
        return {
            "time": datetime.datetime.now().isoformat(),
            "aqi":  int(real_data["aqi"]),
            "pm25": real_data["pm25"],
            "co2":  int(real_data["co2"]),
        }
    else:
        return {
            "time": datetime.datetime.now().isoformat(),
            "aqi":  random.randint(50, 300),
            "pm25": round(random.uniform(10, 150), 1),
            "co2":  random.randint(300, 1000),
        }


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/map")
def map_page():
    return render_template("map.html")


@app.route("/analytics")
def analytics_page():
    return render_template("analytics.html")


@app.route("/about")
def about_page():
    return render_template("about.html")


@app.route("/health")
def health_page():
    return render_template("health.html")


@app.route("/districts")
def districts_page():
    return render_template("districts.html")


# ── Data APIs ────────────────────────────────────────────────────────────────

@app.route("/readings")
def get_readings():
    return jsonify(list(data))


@app.route("/readings/latest")
def get_latest():
    if not data:
        return jsonify({"error": "No data yet"}), 404
    return jsonify(data[-1])


@app.route("/readings/generate", methods=["POST"])
def generate():
    reading = generate_reading()
    data.append(reading)
    return jsonify(reading), 201


@app.route("/alert")
def check_alert():
    if not data:
        return jsonify({"level": "unknown", "message": "No data available"})
    aqi = data[-1]["aqi"]
    if aqi > 200:
        level, message = "hazardous", "Hazardous — stay indoors 🚨"
    elif aqi > 150:
        level, message = "unhealthy", "Unhealthy — limit outdoor activity ⚠️"
    elif aqi > 100:
        level, message = "moderate", "Moderate — sensitive groups take care 🟡"
    else:
        level, message = "good", "Air quality is good ✅"
    return jsonify({"level": level, "message": message, "aqi": aqi})


@app.route("/predict")
def predict():
    readings = list(data)
    if len(readings) < 5:
        return jsonify({"predicted_aqi": None, "error": "Need at least 5 readings"})
    df = pd.DataFrame(readings)
    df.loc[:, "ts"] = pd.to_datetime(df["time"]).astype(np.int64) // 10**9
    X = df["ts"].values.reshape(-1, 1)
    y = df["aqi"].values
    model = LinearRegression()
    model.fit(X, y)
    next_ts = df["ts"].iloc[-1] + 10
    predicted = int(np.clip(model.predict([[next_ts]])[0], 0, 500))
    return jsonify({"predicted_aqi": predicted})


@app.route("/api/districts")
def api_districts():
    """Return live-simulated AQI readings for all Rajasthan districts."""
    readings = [district_reading(d) for d in RAJASTHAN_DISTRICTS]
    return jsonify(readings)


@app.route("/api/analytics")
def api_analytics():
    """Return analytics data: top polluted districts + hourly trend simulation."""
    districts = [district_reading(d) for d in RAJASTHAN_DISTRICTS]
    districts_sorted = sorted(districts, key=lambda x: x["aqi"], reverse=True)

    # Simulate 24-hour trend
    now = datetime.datetime.now()
    hourly = []
    for i in range(24):
        t = now - datetime.timedelta(hours=23 - i)
        hourly.append({
            "hour":  t.strftime("%H:00"),
            "aqi":   random.randint(60, 250),
            "pm25":  round(random.uniform(15, 120), 1),
        })

    return jsonify({
        "top_polluted":   districts_sorted[:8],
        "cleanest":       districts_sorted[-5:],
        "hourly_trend":   hourly,
        "total_districts": len(RAJASTHAN_DISTRICTS),
        "avg_aqi":        round(sum(d["aqi"] for d in districts) / len(districts), 1),
    })


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8888))
    app.run(host="0.0.0.0", port=port)
