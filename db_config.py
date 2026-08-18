"""
Database configuration and operations for Fuel Register using CockroachDB (Postgres-compatible).
"""
import os
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

import certifi
import streamlit as st
import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import RealDictCursor
import pandas as pd

FUEL_ENTRIES_COLUMNS = [
    "Driver Name", "Date", "Receipt No", "Registration No", "Product",
    "Quantity", "Amount", "Previous Km", "Current Km", "Distance"
]

FUEL_ENTRIES_COLUMNS_DB_TO_DF = {
    "driver_name": "Driver Name",
    "date": "Date",
    "receipt_no": "Receipt No",
    "registration_no": "Registration No",
    "product": "Product",
    "quantity": "Quantity",
    "amount": "Amount",
    "previous_km": "Previous Km",
    "current_km": "Current Km",
    "distance": "Distance",
}


def _normalize_ssl_params(db_url: str) -> str:
    """
    Make the connection string portable across hosts.

    CockroachDB Cloud hands out URLs with ``sslmode=verify-full`` and no
    ``sslrootcert``. libpq then falls back to ``~/.postgresql/root.crt``, which
    does not exist on Streamlit Cloud. Cockroach Cloud certificates chain to
    Let's Encrypt, so certifi's CA bundle verifies them. We point at certifi
    rather than ``sslrootcert=system`` because psycopg2-binary ships its own
    statically linked OpenSSL whose built-in CA directory is not present on
    most hosts.
    """
    parts = urlsplit(db_url)
    params = dict(parse_qsl(parts.query, keep_blank_values=True))

    if params.get("sslmode") in (None, "", "verify-full", "verify-ca"):
        params.setdefault("sslmode", "verify-full")
        if not params.get("sslrootcert"):
            params["sslrootcert"] = certifi.where()

    return urlunsplit(parts._replace(query=urlencode(params)))


def get_database_url() -> str:
    """
    Retrieve CockroachDB connection string.
    Credentials should be stored in Streamlit secrets or environment variables.
    """
    try:
        db_url = st.secrets["DATABASE_URL"]
    except (FileNotFoundError, KeyError):
        db_url = os.getenv("DATABASE_URL")

        if not db_url:
            st.error("⚠️ CockroachDB credentials not found. Please configure DATABASE_URL.")
            st.stop()

    return _normalize_ssl_params(db_url)


def get_connection():
    """
    Get a new psycopg2 connection to CockroachDB.
    Auto-creates the table on first successful connection.
    """
    db_url = get_database_url()
    try:
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        conn.autocommit = False
        _ensure_table_exists(conn)
        return conn
    except OperationalError as e:
        st.error(f"⚠️ Could not connect to CockroachDB: {str(e)}")
        raise


def _ensure_table_exists(conn):
    """
    Create the fuel_entries table and indexes if they don't exist.
    Runs once per connection.
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS fuel_entries (
        id BIGSERIAL PRIMARY KEY,
        driver_name TEXT NOT NULL,
        date DATE NOT NULL,
        receipt_no TEXT NOT NULL,
        registration_no TEXT NOT NULL,
        product TEXT NOT NULL,
        quantity NUMERIC DEFAULT 0,
        amount NUMERIC NOT NULL,
        previous_km NUMERIC DEFAULT 0,
        current_km NUMERIC DEFAULT 0,
        distance NUMERIC DEFAULT 0,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """

    idx1 = "CREATE INDEX IF NOT EXISTS idx_driver_name ON fuel_entries(driver_name);"
    idx2 = "CREATE INDEX IF NOT EXISTS idx_date ON fuel_entries(date DESC);"
    idx3 = "CREATE INDEX IF NOT EXISTS idx_registration_no ON fuel_entries(registration_no);"

    with conn.cursor() as cur:
        cur.execute(create_table_sql)
        cur.execute(idx1)
        cur.execute(idx2)
        cur.execute(idx3)
    conn.commit()


def _rows_to_dataframe(rows) -> pd.DataFrame:
    """Convert list of RealDict rows to a DataFrame with renamed columns."""
    if not rows:
        return pd.DataFrame(columns=FUEL_ENTRIES_COLUMNS)

    df = pd.DataFrame([dict(r) for r in rows])

    keep = [c for c in FUEL_ENTRIES_COLUMNS_DB_TO_DF.keys() if c in df.columns]
    df = df[keep]
    df = df.rename(columns=FUEL_ENTRIES_COLUMNS_DB_TO_DF)
    return df


def insert_fuel_entry(
    driver_name: str,
    date: str,
    receipt_no: str,
    registration_no: str,
    product: str,
    quantity: float,
    amount: float,
    previous_km: float,
    current_km: float,
    distance: float,
) -> bool:
    """Insert a new fuel entry into CockroachDB."""
    try:
        conn = get_connection()
        try:
            insert_sql = """
                INSERT INTO fuel_entries (
                    driver_name, date, receipt_no, registration_no,
                    product, quantity, amount, previous_km, current_km, distance
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            with conn.cursor() as cur:
                cur.execute(
                    insert_sql,
                    (
                        driver_name,
                        date,
                        receipt_no,
                        registration_no,
                        product,
                        quantity,
                        amount,
                        previous_km,
                        current_km,
                        distance,
                    ),
                )
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    except Exception as e:
        st.error(f"Error inserting entry: {str(e)}")
        return False


def get_all_fuel_entries() -> pd.DataFrame:
    """Retrieve all fuel entries from CockroachDB."""
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM fuel_entries ORDER BY date DESC;"
                )
                rows = cur.fetchall()
            return _rows_to_dataframe(rows)
        finally:
            conn.close()
    except Exception as e:
        st.error(f"Error retrieving entries: {str(e)}")
        return pd.DataFrame(columns=FUEL_ENTRIES_COLUMNS)


def filter_entries_by_driver(driver_name: str) -> pd.DataFrame:
    """Filter fuel entries by driver name (case-insensitive contains match)."""
    try:
        conn = get_connection()
        try:
            pattern = f"%{driver_name}%"
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM fuel_entries WHERE driver_name ILIKE %s ORDER BY date DESC;",
                    (pattern,),
                )
                rows = cur.fetchall()
            return _rows_to_dataframe(rows)
        finally:
            conn.close()
    except Exception as e:
        st.error(f"Error filtering entries: {str(e)}")
        return pd.DataFrame(columns=FUEL_ENTRIES_COLUMNS)


def get_entry_count() -> int:
    """Get total count of fuel entries."""
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS cnt FROM fuel_entries;")
                row = cur.fetchone()
                return int(row["cnt"]) if row and row["cnt"] is not None else 0
        finally:
            conn.close()
    except Exception as e:
        st.error(f"Error getting entry count: {str(e)}")
        return 0
