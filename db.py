import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS devices (
                    device_id TEXT PRIMARY KEY,
                    name TEXT,
                    location TEXT,
                    metadata JSONB,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS measurements (
                    id BIGSERIAL PRIMARY KEY,
                    device_id TEXT NOT NULL REFERENCES devices(device_id),
                    metric TEXT NOT NULL,
                    value NUMERIC(12, 4) NOT NULL,
                    unit TEXT,
                    recorded_at TIMESTAMPTZ NOT NULL,
                    raw_payload JSONB,
                    UNIQUE (device_id, metric, recorded_at)
                );

                CREATE TABLE IF NOT EXISTS sync_runs (
                    id BIGSERIAL PRIMARY KEY,
                    started_at TIMESTAMPTZ DEFAULT NOW(),
                    finished_at TIMESTAMPTZ,
                    status TEXT NOT NULL,
                    records_fetched INTEGER DEFAULT 0,
                    records_inserted INTEGER DEFAULT 0,
                    error_message TEXT
                );

                CREATE TABLE IF NOT EXISTS sync_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
        conn.commit()
