# AirWatch — Rajasthan Air Quality Monitor

AirWatch is a real-time air quality monitoring dashboard for Rajasthan, India. It provides live AQI, PM2.5, and environmental gas data across all 33 districts, utilizing the Open-Meteo API for high-precision, current metrics.

![AirWatch Preview](https://images.unsplash.com/photo-1529686342540-1b43aec0df75?w=1200&q=80)

## 🌟 Key Features

- **Live Data Integration**: Real-time air quality data for all 33 districts of Rajasthan via Open-Meteo API.
- **Interactive GeoJSON Map**: A choropleth map that visualises pollution levels across district boundaries.
- **District Status**: A searchable and sortable table of all districts with live PM2.5 and AQI metrics.
- **ML-Based Forecasting**: Uses `scikit-learn` to predict the next AQI value based on recent trends.
- **Health & Safety Guidelines**: Actionable health tips tailored to current air quality levels.
- **Analytics Dashboard**: Deep dive into the most polluted vs cleanest districts and 24-hour trends.
- **Performance Caching**: Intelligent 5-minute TTL caching to ensure fast loading and API efficiency.

## 🛠️ Tech Stack

- **Backend**: Python, [Flask](https://flask.palletsprojects.com/)
- **Machine Learning**: [scikit-learn](https://scikit-learn.org/), [pandas](https://pandas.pydata.org/), [numpy](https://numpy.org/)
- **API**: [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api)
- **Frontend**: Vanilla JS, [Chart.js](https://www.chartjs.org/), [Leaflet.js](https://leafletjs.com/)
- **Deployment**: [Gunicorn](https://gunicorn.org/) (ready for Render/Railway/Heroku)

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation
1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd airwatch
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```
   The app will be available at `http://127.0.0.1:8888`.

## 📂 Project Structure

- `app.py`: Flask backend, API integrations, and ML logic.
- `templates/`: HTML5 templates for all dashboard views.
- `requirements.txt`: Python dependencies.
- `Procfile`: Production server configuration for deployment.

## ☁️ Deployment

This project is configured for easy deployment on platforms like Render or Railway.
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

---
Built with ❤️ for a cleaner Rajasthan.
