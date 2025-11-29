import eventlet
eventlet.monkey_patch() # CRITICAL: Must be first

import os
import json
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Credentials from Environment (The Vault)
DATABASE_URL = os.environ.get('DATABASE_URL')
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN')
app.config = os.environ.get('ADMIN_TOKEN', 'fallback_secret')

# Async Mode for Render
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

def get_db_connection():
    try:
        # V14 Security: SSL Mode Mandatory
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn
    except Exception as e:
        print(f"DB Connection Error: {e}")
        return None

@app.route('/')
def index():
    return "<h1>SkySeeAll V14 Command Center Online</h1>"

@app.route('/api/init', methods=)
def init_db():
    conn = get_db_connection()
    if not conn: return jsonify({'error': 'DB Fail'}), 500
    try:
        cur = conn.cursor()
        # V14 Table Schema
        cur.execute("""
            CREATE TABLE IF NOT EXISTS v14_logs (
                id SERIAL PRIMARY KEY,
                device_id TEXT,
                log_data JSONB,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        return jsonify({'status': 'Initialized'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    socketio.run(app, host='0.0.0.0', port=port)
