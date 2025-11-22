import os
import sys
import json
import psycopg2
import psycopg2.extras
import requests
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_talisman import Talisman
from flask_socketio import SocketIO, join_room, leave_room, emit

# V14.2 ARCHITECTURE: Hybrid-Monolith Setup
# The 'static_folder' points to the React build directory.
# The 'template_folder' is reserved for legacy server-side admin pages.
app = Flask(__name__, static_folder='build', template_folder='templates')

# Configuration from Source of Truth
DATABASE_URL = os.environ.get('DATABASE_URL')
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN')
app.config = os.environ.get('SECRET_KEY', 'skyseeall_v14_secure_key')

# Security Headers
# Forces HTTPS and sets strict security headers to prevent XSS/Clickjacking.
Talisman(app, content_security_policy=None, force_https=True)

# V11.8 Feature: Real-Time Socket Engine
# Async mode 'eventlet' is required for high-concurrency chat/video.
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Database Persistence Layer
def get_db_conn():
    """Establishes secure SSL connection to NeonDB using environment credentials."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Database Connection Error: {e}")
        return None

def initialize_database():
    """V14.3 Schema Initialization Protocol."""
    conn = get_db_conn()
    if not conn:
        print("CRITICAL: Failed to connect to DB during initialization.")
        return

    # Fixed SQL Syntax: Triple Quotes for multi-line safety and parameterized queries.
    schema_sql = """
    CREATE TABLE IF NOT EXISTS v2_users (
        user_id VARCHAR(255) PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS v2_pets (
        pet_id VARCHAR(255) PRIMARY KEY,
        user_id VARCHAR(255) REFERENCES v2_users(user_id),
        pet_name VARCHAR(255),
        pet_data JSONB,
        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS v2_commands (
        command_id SERIAL PRIMARY KEY,
        pet_id VARCHAR(255) REFERENCES v2_pets(pet_id),
        command_type VARCHAR(100),
        parameters JSONB,
        status VARCHAR(50) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(schema_sql)
        conn.commit()
        print("V14.3 Database Schema Initialized Successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Schema Initialization Error: {e}")
    finally:
        conn.close()

# V14.2 Routing Logic (SPA Support)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    """
    Serves the React frontend.
    If a requested file exists in 'build/', serve it.
    Otherwise, serve 'index.html' to let the client-side React Router handle the path.
    This "Catch-All" route is essential for SPAs.
    """
    if path!= "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# --- Sentry (Collector) Routes (Tier 3 - Pet Level) ---
@app.route('/sentry/checkin', methods=)
def sentry_checkin():
    """ Used by collector.py. Registers a pet or updates its 'pet_data'. """
    data = request.json
    user_id = data.get('user_id')
    pet_id = data.get('pet_id')
    pet_name = data.get('pet_name')
    pet_data = data.get('pet_data')

    if not user_id or not pet_id or not pet_name or not pet_data:
        return jsonify({"error": "user_id, pet_id, pet_name, and pet_data are required"}), 400

    conn = get_db_conn()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            # Upsert the pet: Insert if new, update if exists.
            cursor.execute(
                """
                INSERT INTO v2_pets (pet_id, user_id, pet_name, pet_data, last_seen) 
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP) 
                ON CONFLICT (pet_id) DO UPDATE 
                SET pet_name = EXCLUDED.pet_name, 
                    pet_data = EXCLUDED.pet_data, 
                    user_id = EXCLUDED.user_id,
                    last_seen = CURRENT_TIMESTAMP
                """,
                (pet_id, user_id, pet_name, json.dumps(pet_data))
            )
        conn.commit()
        return jsonify({"message": f"Pet {pet_id} checked in."}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/sentry/get_commands/<pet_id>', methods=)
def sentry_get_commands(pet_id):
    """ Used by collector.py. Fetches 'pending' commands for a specific pet. """
    conn = get_db_conn()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    commands_to_send =
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                "SELECT command_id, command_type, parameters FROM v2_commands WHERE pet_id = %s AND status = 'pending'",
                (pet_id,)
            )
            commands = cursor.fetchall()
            commands_to_send = list(commands)
            
            if commands:
                command_ids = [cmd['command_id'] for cmd in commands]
                cursor.execute(
                    "UPDATE v2_commands SET status = 'sent' WHERE command_id = ANY(%s::int)",
                    (command_ids,)
                )
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
        
    return jsonify({"commands": commands_to_send}), 200

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv == 'initdb':
        initialize_database()
    else:
        socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
