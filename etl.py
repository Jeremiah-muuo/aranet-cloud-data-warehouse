from datetime import datetime, timezone
from decimal import Decimal

from psycopg2.extras import Json

from aranet_client import fetch_devices, fetch_measurements_since
from db import get_db_connection


def iso_utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_last_synced_at():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT value FROM sync_state WHERE key = 'last_synced_at'")
            row = cur.fetchone()
            return row[0] if row else None


def set_last_synced_at(timestamp):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO sync_state(key, value, updated_at)
                VALUES ('last_synced_at', %s, NOW())
                ON CONFLICT (key)
                DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()
            """, (timestamp,))
        conn.commit()


def upsert_device(device):
    # Update these field names to match Aranet Cloud's devices response.
    device_id = device.get("device_id") or device.get("id")
    if not device_id:
        return False

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO devices (device_id, name, location, metadata, updated_at)
                VALUES (%s, %s, %s, %s, NOW())
                ON CONFLICT (device_id)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    location = EXCLUDED.location,
                    metadata = EXCLUDED.metadata,
                    updated_at = NOW()
            """, (
                str(device_id),
                device.get("name"),
                device.get("location"),
                Json(device),
            ))
        conn.commit()
    return True


def upsert_measurement(item):
    # Update these field names to match Aranet Cloud's measurements response.
    device_id = item.get("device_id") or item.get("deviceId") or item.get("id")
    metric = item.get("metric")
    value = item.get("value")
    timestamp = item.get("timestamp") or item.get("recorded_at")

    if not device_id or not metric or value is None or not timestamp:
        return False

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO measurements (
                    device_id, metric, value, unit, recorded_at, raw_payload
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (device_id, metric, recorded_at)
                DO NOTHING
            """, (
                str(device_id),
                str(metric),
                Decimal(str(value)),
                item.get("unit"),
                timestamp,
                Json(item),
            ))
        conn.commit()
    return True


def sync_data():
    started_at = iso_utc_now()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO sync_runs (started_at, status)
                VALUES (NOW(), 'running')
                RETURNING id
            """)
            run_id = cur.fetchone()[0]
        conn.commit()

    fetched = 0
    inserted = 0

    try:
        devices = fetch_devices()
        if isinstance(devices, list):
            for device in devices:
                if upsert_device(device):
                    fetched += 1
                    inserted += 1

        last_synced_at = get_last_synced_at()
        measurements = fetch_measurements_since(last_synced_at)

        if isinstance(measurements, list):
            for item in measurements:
                if upsert_measurement(item):
                    fetched += 1
                    inserted += 1

        set_last_synced_at(iso_utc_now())

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE sync_runs
                    SET finished_at = NOW(),
                        status = 'succeeded',
                        records_fetched = %s,
                        records_inserted = %s
                    WHERE id = %s
                """, (fetched, inserted, run_id))
            conn.commit()

        return inserted

    except Exception as exc:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE sync_runs
                    SET finished_at = NOW(),
                        status = 'failed',
                        records_fetched = %s,
                        records_inserted = %s,
                        error_message = %s
                    WHERE id = %s
                """, (fetched, inserted, str(exc), run_id))
            conn.commit()
        raise
