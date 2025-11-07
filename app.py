import os
import sys
import json
import psycopg2
import psycopg2.extras
from flask import Flask, request, jsonify, render_template, send_from_directory

# --- Configuration ---
app = Flask(__name__)
DATABASE_URL = os.environ.get('DATABASE_URL')
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN')

# --- Database Functions ---
def get_db_conn():
    """Establishes database connection."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def initialize_database():
    """Creates all necessary tables if they don't exist."""
    print("Initializing database tables...")
    conn = get_db_conn()
    if not conn:
        print("Cannot initialize DB: Connection failed.")
        return

    tables = [
        """
        CREATE TABLE IF NOT EXISTS wifi_signals (
            id SERIAL PRIMARY KEY,
            bssid VARCHAR(255) NOT NULL,
            ssid VARCHAR(255),
            capabilities VARCHAR(500),
            level INTEGER,
            timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(bssid, timestamp)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS bluetooth_devices (
            id SERIAL PRIMARY KEY,
            mac_address VARCHAR(255) NOT NULL,
            name VARCHAR(255),
            timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(mac_address, timestamp)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS cell_towers (
            id SERIAL PRIMARY KEY,
            type VARCHAR(50),
            cid INTEGER,
            lac INTEGER,
            psc INTEGER,
            signal_strength INTEGER,
            timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );
        """
    ]

    try:
        with conn.cursor() as cur:
            for table in tables:
                cur.execute(table)
        conn.commit()
        print("Successfully created/verified 3 tables.")
    except Exception as e:
        print(f"Error creating tables: {e}")
    finally:
        conn.close()

# --- API Routes (The "Back-End") ---

@app.route('/')
def index():
    """Serves the main HTML 'front-end'."""
    return render_template('index.html')

@app.route('/legal')
def legal():
    """Serves the legal disclaimer file."""
    return send_from_directory('.', 'legal_disclaimer.md')

@app.route('/api/admin_login', methods=['POST'])
def admin_login():
    """Handles admin login."""
    data = request.json
    if not data or 'token' not in data:
        return jsonify({"error": "Missing token"}), 400

    if data['token'] == ADMIN_TOKEN:
        return jsonify({"success": True, "message": "Login successful"}), 200
    else:
        return jsonify({"success": False, "message": "Invalid token"}), 401

@app.route('/api/report', methods=['POST'])
def report_data():
    """Receives data from the 'collector.py' sentry."""
    data = request.json
    data_type = data.get('type')
    payload = data.get('payload')

    conn = get_db_conn()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cur:
            if data_type == 'wifi' and payload:
                for device in payload:
                    cur.execute(
                        "INSERT INTO wifi_signals (bssid, ssid, capabilities, level) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
                        (device.get('bssid'), device.get('ssid'), device.get('capabilities'), device.get('level'))
                    )
            elif data_type == 'bluetooth' and payload:
                for device in payload:
                    cur.execute(
                        "INSERT INTO bluetooth_devices (mac_address, name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                        (device.get('mac_address'), device.get('name'))
                    )

        conn.commit()
        return jsonify({"success": True, "message": f"Saved {len(payload)} {data_type} items"}), 200
    except Exception as e:
        print(f"Error inserting data: {e}")
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/get_data', methods=['POST'])
def get_data():
    """Provides data to the dashboard (admin only)."""
    data = request.json
    if data.get('token') != ADMIN_TOKEN:
        return jsonify({"error": "Not authorized"}), 401

    conn = get_db_conn()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    results = {}
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM wifi_signals ORDER BY timestamp DESC LIMIT 20")
            results['wifi'] = cur.fetchall()
            cur.execute("SELECT * FROM bluetooth_devices ORDER BY timestamp DESC LIMIT 20")
            results['bluetooth'] = cur.fetchall()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# --- Main Launch ---
if __name__ == "__main__":
    if not DATABASE_URL or not ADMIN_TOKEN:
        print("FATAL ERROR: DATABASE_URL or ADMIN_TOKEN not set.")
        print("Please run 'source ~/.bashrc' and try again.")
        sys.exit(1)

    if os.environ.get('RUN_DB_INIT') == 'true':
        initialize_database()
    else:
        print("Starting SkySeeAll Server at http://1.2.3.4:5000")
        app.run(host='0.0.0.0', port=5000)

