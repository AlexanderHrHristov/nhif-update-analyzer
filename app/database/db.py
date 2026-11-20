
import os
import sqlite3
from pathlib import Path


APP_NAME = "NHIFUpdateAnalyzer"


def get_database_path():
    """Връща постоянен път до потребителската SQLite база."""

    local_app_data = os.environ.get("LOCALAPPDATA")

    if local_app_data:
        base_dir = Path(local_app_data)
    else:
        base_dir = Path.home() / "AppData" / "Local"

    database_dir = base_dir / APP_NAME
    database_dir.mkdir(parents=True, exist_ok=True)

    return database_dir / "nhif_analyzer.db"


DB_PATH = get_database_path()


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS update_batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                effective_date TEXT NOT NULL,
                filename TEXT NOT NULL,
                checksum TEXT NOT NULL UNIQUE,
                imported_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS product_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id INTEGER NOT NULL,
                nhif_code TEXT NOT NULL,
                atc_code TEXT,
                inn TEXT,
                name TEXT,
                manufacturer TEXT,
                strength TEXT,
                package_text TEXT,
                package_quantity TEXT,
                pharmaceutical_form TEXT,

                flag_10 TEXT,
                item_type TEXT,
                field_12 TEXT,
                prescription_group TEXT,
                flag_14 TEXT,

                reimbursement_value TEXT,
                price_source TEXT,
                flag_17 TEXT,
                package_price TEXT,
                patient_difference TEXT,
                flag_20 TEXT,

                national_number TEXT,
                status_flag TEXT,

                FOREIGN KEY (batch_id)
                    REFERENCES update_batches(id),

                UNIQUE(batch_id, nhif_code)
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_snapshots_nhif
            ON product_snapshots(nhif_code)
        """)

    print(f"Database initialized: {DB_PATH}")
