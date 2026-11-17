# Aranet Cloud to SQL Data Warehouse

A starter Python ETL pipeline that fetches data from Aranet Cloud and stores normalized device measurements in PostgreSQL.

> Replace the placeholders in `aranet_client.py` with the endpoints and response fields documented by Aranet Cloud.

## Features

- Configurable API key header
- Optional API key prefix (for example `Bearer`)
- Incremental sync checkpoint
- Idempotent device and measurement upserts
- PostgreSQL JSON storage
- Raw API payload storage
- Scheduled five-minute synchronization
- **Skycast weather forecasting app** with city search, current conditions, hourly trends, and a 7-day forecast

## Setup

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
```

Edit `.env` with your database and Aranet Cloud settings before starting the ETL pipeline.

## Weather app

The weather dashboard uses the free Open-Meteo geocoding and forecast APIs; it does not require an API key. Install dependencies and run:

```bash
pip install -r requirements.txt
streamlit run weather_app.py
```

Open the local URL printed by Streamlit, search for a city, and choose Celsius or Fahrenheit. Nairobi is loaded by default.

## Security

Never commit `.env` or API keys. `.env` is excluded by `.gitignore`.
