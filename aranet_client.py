import os

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("ARANET_API_BASE_URL", "").rstrip("/")
API_KEY = os.getenv("ARANET_API_KEY", "").strip()
API_KEY_HEADER = os.getenv("ARANET_API_KEY_HEADER", "X-API-Key").strip()
API_KEY_PREFIX = os.getenv("ARANET_API_KEY_PREFIX", "").strip()


def get_headers():
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    if API_KEY:
        if not API_KEY_HEADER:
            raise ValueError("ARANET_API_KEY_HEADER cannot be empty when an API key is set")

        value = f"{API_KEY_PREFIX} {API_KEY}".strip() if API_KEY_PREFIX else API_KEY
        headers[API_KEY_HEADER] = value

    return headers


def get_json(path, params=None):
    if not BASE_URL:
        raise ValueError("Set ARANET_API_BASE_URL in .env")

    response = requests.get(
        f"{BASE_URL}/{path.lstrip('/')}",
        headers=get_headers(),
        params=params,
        timeout=60,
    )
    response.raise_for_status()

    data = response.json()
    return data.get("data", data) if isinstance(data, dict) else data


def fetch_devices():
    # Replace this path with your Aranet Cloud devices endpoint.
    return get_json("/api/v1/devices")


def fetch_measurements_since(last_synced_at=None):
    # Replace this path and query parameter with Aranet Cloud's API fields.
    params = {"from": last_synced_at} if last_synced_at else None
    return get_json("/api/v1/measurements", params=params)
