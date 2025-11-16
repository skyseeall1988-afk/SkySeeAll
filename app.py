import os
import sys
import json
import psycopg2
import psycopg2.extras
import requests
from flask import Flask, request, jsonify, render_template, send_from_directory

# V10 SECURITY ADDITIONS (V9)
try:
    from flask_talisman import Talisman
except ImportError:
    print("flask_talisman not found. Run 'pip install flask-talisman'")
    sys.exit(1)

# V10 CHAT ADDITIONS
try:
    from flask_socketio import SocketIO, join_room, leave_room, emit
except ImportError:
    print("flask_socketio not found. Run 'pip install flask-socketio'")
    sys.exit(1)

# App Configuration
# FIX: Corrected '__name__'
app = Flask(__name__, template_folder='templates')
DATABASE_URL = os.environ.get('DATABASE_URL')
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN')

# V10 SECURITY ADDITION (V9)
# This forces HTTPS and sets secure headers
Talisman(app)

# V10 CHAT ADDITIONS
#--- V10.1/V11.2 CRITICAL FIX: Fatal bug corrected.
# We must set the 'SECRET_KEY' *inside* the config dictionary.
# FIX: Corrected string assignment to dictionary key assignment
app.config['SECRET_KEY'] = 'A_NEW_LONG_RANDOM_SECRET_KEY_V11_2'

socketio = SocketIO(app, engineio_logger=True, async_mode='eventlet')

#
# Database Functions (V7)
#

def get_db_conn():
    """Establishes database connection."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def initialize_database():
    """Creates all necessary tables for V6 (User, Pet, Command)."""
    print("Initializing V6 database tables...")
    conn = get_db_conn()
    if not conn:
        print("Cannot initialize DB: Connection failed.")
        return

    create_tables_sql = """
    CREATE TABLE IF NOT EXISTS v2_users (
        user_id VARCHAR(255) PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        notes TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS v2_pets (
        pet_id VARCHAR(255) PRIMARY KEY,
        user_id VARCHAR(255) NOT NULL REFERENCES v2_users(user_id) ON DELETE CASCADE,
        pet_name VARCHAR(255) NOT NULL,
        pet_data JSONB,
        notes TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS v2_commands (
        command_id SERIAL PRIMARY KEY,
        user_id VARCHAR(255) NOT NULL,
        pet_id VARCHAR(255),
        command_type VARCHAR(100) NOT NULL,
        parameters JSONB,
        status VARCHAR(50) DEFAULT 'pending',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES v2_users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (pet_id) REFERENCES v2_pets(pet_id) ON DELETE CASCADE
    );
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(create_tables_sql)
        conn.commit()
        print("Database tables initialized successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error initializing tables: {e}")
    finally:
        conn.close()

#
# API Helper Functions (V7)
#

def is_admin(request):
    """Checks for the Admin Token in headers."""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return False
    try:
        token_type, token = auth_header.split()
        return token_type == 'Bearer' and token == ADMIN_TOKEN
    except ValueError:
        return False

def get_user_from_db(user_id):
    """Fetches a single user by ID."""
    conn = get_db_conn()
    if not conn:
        return None
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM v2_users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()
            return user
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None
    finally:
        conn.close()

#--- Admin Routes (Tier 1 Full Control) (V7)

# FIX: Added methods=['POST']
@app.route('/admin/db/init', methods=['POST'])
def handle_db_init():
    """Admin-only route to initialize the database."""
    if not is_admin(request):
        return jsonify({"error": "Unauthorized"}), 403
    initialize_database()
    return jsonify({"message": "Database initialization attempted."}), 200

# FIX: Added methods=['GET']
@app.route('/admin/users', methods=['GET'])
def admin_get_all_users():
    if not is_admin(request):
        return jsonify({"error": "Unauthorized"}), 403
    conn = get_db_conn()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("""
            SELECT
                u.user_id,
                u.username,
                u.created_at,
                COUNT(p.pet_id) AS pet_count
            FROM v2_users u
            LEFT JOIN v2_pets p ON u.user_id = p.user_id
            GROUP BY u.user_id
            ORDER BY u.username;
            """)
            users = cursor.fetchall()
            return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# FIX: Added methods=['GET', 'DELETE']
@app.route('/admin/user/<user_id>', methods=['GET', 'DELETE'])
def admin_manage_user(user_id):
    if not is_admin(request):
        return jsonify({"error": "Unauthorized"}), 403
    conn = get_db_conn()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            if request.method == 'GET':
                cursor.execute("SELECT * FROM v2_users WHERE user_id = %s", (user_id,))
                user = cursor.fetchone()
                if not user:
                    return jsonify({"error": "User not found"}), 404
                cursor.execute("SELECT * FROM v2_pets WHERE user_id = %s", (user_id,))
                pets = cursor.fetchall()
                cursor.execute(
                    "SELECT * FROM v2_commands WHERE user_id = %s ORDER BY created_at DESC LIMIT 50",
                    (user_id,)
                )
                commands = cursor.fetchall()
                return jsonify({"user": user, "pets": pets, "commands": commands}), 200

            elif request.method == 'DELETE':
                cursor.execute("DELETE FROM v2_users WHERE user_id = %s", (user_id,))
                conn.commit()
                if cursor.rowcount == 0:
                    return jsonify({"error": "User not found"}), 404
                return jsonify({"message": f"User {user_id} and all associated data deleted"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

#
# V6: NEW ADMIN COMMAND ROUTES (V7)
#

# FIX: Added methods=['POST']
@app.route('/admin/command/push', methods=['POST'])
def admin_push_command():
    if not is_admin(request):
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    user_id = data.get('user_id')
    pet_id = data.get('pet_id')
    command_type = data.get('command_type')
    parameters = data.get('parameters', {})

    if not user_id or not pet_id or not command_type:
        return jsonify({"error": "user_id, pet_id, and command_type are required"}), 400

    conn = get_db_conn()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                """
                INSERT INTO v2_commands (user_id, pet_id, command_type, parameters, status)
                VALUES (%s, %s, %s, %s, 'pending')
                RETURNING *;
                """,
                (user_id, pet_id, command_type, json.dumps(parameters))
            )
            new_command = cursor.fetchone()
            conn.commit()
            return jsonify(new_command), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# FIX: Added methods=['GET']
@app.route('/admin/command/<command_id>', methods=['GET'])
def admin_get_command_status(command_id):
    if not is_admin(request):
        return jsonify({"error": "Unauthorized"}), 403
    conn = get_db_conn()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM v2_commands WHERE command_id = %s", (command_id,))
            command = cursor.fetchone()
            if not command:
                return jsonify({"error": "Command not found"}), 404
            return jsonify(command), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

#--- Public API Routes (Tier 2 User Level) (V7)

# FIX: Added methods=['POST']
@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.json
    user_id = data.get('user_id')
    username = data.get('username')

    if not user_id or not username:
        return jsonify({"error": "user_id and username are required"}), 400

    conn = get_db_conn()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO v2_users (user_id, username) VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING",
                (user_id, username)
            )
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({"error": "User ID already exists"}), 409
            return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

#
# Sentry (Collector) Routes (Tier 3 Pet Level) (V7)
#

# FIX: Added methods=['POST']
@app.route('/sentry/checkin', methods=['POST'])
def sentry_checkin():
    data = request.json
    user_id = data.get('user_id')
    pet_id = data.get('pet_id')
    pet_name = data.get('pet_name')
    pet_data = data.get('pet_data')

    if not user_id or not pet_id or not pet_name or not pet_data:
        return jsonify({"error": "user_id, pet_id, pet_name, and pet_data are required"}), 400

    user = get_user_from_db(user_id)
    if not user:
        return jsonify({"error": "User ID not found. Register user first."}), 404

    conn = get_db_conn()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO v2_pets (pet_id, user_id, pet_name, pet_data)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (pet_id) DO UPDATE SET
                    pet_name = EXCLUDED.pet_name,
                    pet_data = EXCLUDED.pet_data,
                    user_id = EXCLUDED.user_id
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

# FIX: Added methods=['GET']
@app.route('/sentry/get_commands/<pet_id>', methods=['GET'])
def sentry_get_commands(pet_id):
    conn = get_db_conn()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    # FIX: Corrected invalid syntax 'commands_to_send ='
    commands_to_send = []
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
                    "UPDATE v2_commands SET status = 'sent' WHERE command_id = ANY(%s::int[])",
                    (command_ids,)
                )
                conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
    
    return jsonify({"commands": commands_to_send}), 200

# FIX: Added methods=['POST']
@app.route('/sentry/update_command', methods=['POST'])
def sentry_update_command():
    data = request.json
    command_id = data.get('command_id')
    status = data.get('status')
    result = data.get('result') # V6: This now contains { "output": "...", "error": "..." }

    # FIX: Corrected 'command id' to 'command_id'
    if not command_id or not status:
        return jsonify({"error": "command_id and status are required"}), 400

    conn = get_db_conn()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            if result:
                # V6: Update parameters to store the result
                # FIX: Corrected the broken string literal
                cursor.execute(
                    "UPDATE v2_commands SET status = %s, parameters = parameters || %s::jsonb WHERE command_id = %s",
                    (status, json.dumps({"result": result}), command_id)
                )
            else:
                cursor.execute(
                    "UPDATE v2_commands SET status = %s WHERE command_id = %s",
                    (status, command_id)
                )
            conn.commit()
            return jsonify({"message": "Command updated"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

#
# Front-End Webpage Routes (V7)
#

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

#
# V10 CHAT ADDITIONS (Socket Events)
#

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    print(f'{username} has entered the room: {room}')
    emit('message', {'user': 'System', 'text': f'{username} has entered the room.'}, to=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    print(f'{username} has left the room: {room}')
    emit('message', {'user': 'System', 'text': f'{username} has left the room.'}, to=room)

@socketio.on('message')
def on_message(data):
    room = data['room']
    print(f"Message received in room {room}: {data}")
    emit('message', data, to=room)

#
# Main Execution (Modified for V10)
#

# FIX: Corrected 'sys.argv' to 'sys.argv[1]'
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'initdb':
        print("Running one-time database initialization...")
        initialize_database()
        print("Initialization complete. Run app without 'initdb' to start server.")
    else:
        if not DATABASE_URL or not ADMIN_TOKEN:
            print("FATAL ERROR: DATABASE_URL and ADMIN_TOKEN environment variables must be set.")
            print("Please check your ~/.bashrc file and 'source ~/.bashrc'")
        else:
            print("Starting Flask-SocketIO server...")
            # V10.1 MODIFICATION: Use socketio.run, not app.run
            socketio.run(app, host='0.0.0.0', port=8080)
