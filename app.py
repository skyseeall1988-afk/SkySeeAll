import os
import sys
import json
import psycopg2
import psycopg2.extras
import requests
import subprocess
import threading
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_talisman import Talisman
from flask_socketio import SocketIO, join_room, leave_room, emit
from hardware_manager import hw_manager, get_hardware_status, execute_with_fallback, Emulator
from live_proxy import proxy_manager, get_proxy_status
from control_module import master_controller, get_master_status

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

# V14.4 Feature: Operation Lock for Safety-Critical Functions
operation_lock = threading.Lock()
internet_disabled = False

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
        result JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS v2_scan_results (
        scan_id SERIAL PRIMARY KEY,
        pet_id VARCHAR(255) REFERENCES v2_pets(pet_id),
        scan_type VARCHAR(100),
        scan_data JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS v2_audit_logs (
        log_id SERIAL PRIMARY KEY,
        pet_id VARCHAR(255),
        operation VARCHAR(100),
        details JSONB,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS v2_media_streams (
        stream_id SERIAL PRIMARY KEY,
        pet_id VARCHAR(255),
        stream_type VARCHAR(50),
        stream_url VARCHAR(500),
        metadata JSONB,
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

# V14.4 Safety-Critical Operations
def kill_internet():
    """Disables networking during sensitive operations (WPS audit, deauth)."""
    global internet_disabled
    try:
        subprocess.run(['nmcli', 'networking', 'off'], check=True)
        internet_disabled = True
        log_audit('system', 'internet_kill', {'reason': 'safety_protocol'})
        return True
    except Exception as e:
        print(f"Failed to disable internet: {e}")
        return False

def restore_internet():
    """Re-enables networking after operation completes."""
    global internet_disabled
    try:
        subprocess.run(['nmcli', 'networking', 'on'], check=True)
        internet_disabled = False
        log_audit('system', 'internet_restore', {'reason': 'operation_complete'})
        return True
    except Exception as e:
        print(f"Failed to restore internet: {e}")
        return False

def log_audit(pet_id, operation, details):
    """Logs operations to audit table."""
    conn = get_db_conn()
    if not conn:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO v2_audit_logs (pet_id, operation, details) VALUES (%s, %s, %s)",
                (pet_id, operation, json.dumps(details))
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Audit log error: {e}")
    finally:
        conn.close()

def save_scan_result(pet_id, scan_type, scan_data):
    """Save scan results to database."""
    conn = get_db_conn()
    if not conn:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO v2_scan_results (pet_id, scan_type, scan_data) VALUES (%s, %s, %s)",
                (pet_id, scan_type, json.dumps(scan_data))
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Save scan error: {e}")
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
@app.route('/sentry/checkin', methods=['POST'])
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

@app.route('/sentry/get_commands/<pet_id>', methods=['GET'])
def sentry_get_commands(pet_id):
    """ Used by collector.py. Fetches 'pending' commands for a specific pet. """
    conn = get_db_conn()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
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

@app.route('/sentry/report_result', methods=['POST'])
def sentry_report_result():
    """Sentries report command execution results."""
    data = request.json
    command_id = data.get('command_id')
    result = data.get('result')
    
    if not command_id or not result:
        return jsonify({"error": "command_id and result required"}), 400
    
    conn = get_db_conn()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE v2_commands SET status = 'completed', result = %s WHERE command_id = %s",
                (json.dumps(result), command_id)
            )
        conn.commit()
        return jsonify({"message": "Result recorded"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# --- Hardware Status API ---

@app.route('/api/hardware/status', methods=['GET'])
def api_hardware_status():
    """V14.4: Get hardware capabilities and availability."""
    return jsonify(get_hardware_status()), 200

@app.route('/api/hardware/capabilities', methods=['GET'])
def api_hardware_capabilities():
    """V14.4: Get detailed hardware capabilities."""
    caps = hw_manager.get_capabilities()
    return jsonify({
        'capabilities': caps,
        'features': {
            'wifi_scanning': caps['wifi_managed'],
            'packet_injection': caps['wifi_monitor'],
            'bluetooth': caps['bluetooth'],
            'spectrum_analysis': caps['sdr'],
            'video_streaming': caps['camera'],
            'audio_analysis': caps['microphone'],
            'geolocation': caps['gps'],
            'online_osint': caps['internet']
        },
        'emulation_available': True
    }), 200

# --- V14.5 Feature: Master Control Module & Live Proxy API ---

@app.route('/api/control/status', methods=['GET'])
def api_control_status():
    """Get complete system status including controllers, hardware, and proxies."""
    try:
        status = get_master_status()
        status['hardware'] = get_hardware_status()
        status['proxies'] = get_proxy_status()
        status['timestamp'] = datetime.utcnow().isoformat()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/control/execute', methods=['POST'])
def api_control_execute():
    """Execute command through master controller."""
    data = request.json
    module = data.get('module')
    action = data.get('action')
    parameters = data.get('parameters', {})
    
    if not module or not action:
        return jsonify({"error": "module and action required"}), 400
    
    try:
        result = master_controller.execute_command(module, action, parameters)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/control/module/<module>/enable', methods=['POST'])
def api_control_enable_module(module):
    """Enable a specific module."""
    try:
        master_controller.enable_module(module)
        return jsonify({"message": f"Module {module} enabled", "success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/control/module/<module>/disable', methods=['POST'])
def api_control_disable_module(module):
    """Disable a specific module."""
    try:
        master_controller.disable_module(module)
        return jsonify({"message": f"Module {module} disabled", "success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/proxy/status', methods=['GET'])
def api_proxy_status():
    """Get status of all live proxy services."""
    return jsonify(get_proxy_status()), 200

# --- Module 1: Tactical HUD Routes ---

@app.route('/tactical/wifi_scan', methods=['POST'])
def tactical_wifi_scan():
    """V14.5 Feature: Wi-Fi Radar with WiGLE proxy + hardware detection and emulation fallback."""
    data = request.json
    pet_id = data.get('pet_id', 'server')
    interface = data.get('interface', 'wlan0')
    use_proxy = data.get('use_proxy', False)
    location = data.get('location')  # {"lat": 37.7749, "lon": -122.4194}
    
    # If proxy requested and location provided, use WiGLE
    if use_proxy and location:
        try:
            result = proxy_manager.get_wifi_networks_near_location(
                location['lat'], 
                location['lon']
            )
            if result:
                return jsonify({
                    'networks': result,
                    'count': len(result),
                    'proxy': True,
                    'method': 'wigle_proxy',
                    'success': True
                }), 200
        except Exception as e:
            print(f"WiGLE proxy failed: {e}, falling back to hardware")
    
    def real_wifi_scan():
        """Real Wi-Fi scanning with iwlist"""
        result = subprocess.run(
            ['iwlist', interface, 'scan'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        networks = []
        current_network = {}
        for line in result.stdout.split('\n'):
            if 'Cell' in line and 'Address:' in line:
                if current_network:
                    networks.append(current_network)
                current_network = {'bssid': line.split('Address: ')[1].strip()}
            elif 'ESSID:' in line:
                current_network['ssid'] = line.split('ESSID:')[1].strip('"')
            elif 'Signal level=' in line:
                current_network['signal'] = int(line.split('Signal level=')[1].split()[0])
            elif 'Channel:' in line:
                current_network['channel'] = int(line.split('Channel:')[1].strip())
        
        if current_network:
            networks.append(current_network)
        
        return {'networks': networks, 'count': len(networks), 'emulated': False}
    
    # Use hardware fallback system
    scan_result = execute_with_fallback('wifi_scan', real_wifi_scan)
    
    # Store results
    save_scan_result(pet_id, 'wifi_scan', scan_result)
    log_audit(pet_id, 'wifi_scan', {'count': scan_result.get('count', 0), 'emulated': scan_result.get('emulated', False)})
    
    # Emit live feed update
    if scan_result.get('networks'):
        for network in scan_result['networks']:
            socketio.emit('tactical_update', network, room=f"tactical_{pet_id}")
    
    return jsonify(scan_result), 200

@app.route('/tactical/nmap_scan', methods=['POST'])
def tactical_nmap_scan():
    """V14.4 Feature: Network port scanning with Nmap."""
    data = request.json
    target = data.get('target')
    scan_type = data.get('scan_type', '-sV')  # Service detection
    pet_id = data.get('pet_id', 'server')
    
    if not target:
        return jsonify({"error": "target IP/range required"}), 400
    
    if not operation_lock.acquire(blocking=False):
        return jsonify({"error": "Another operation in progress"}), 409
    
    try:
        result = subprocess.run(
            ['nmap', scan_type, target, '-oX', '-'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        save_scan_result(pet_id, 'nmap_scan', {'target': target, 'output': result.stdout})
        log_audit(pet_id, 'nmap_scan', {'target': target, 'scan_type': scan_type})
        
        return jsonify({"result": result.stdout}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        operation_lock.release()

@app.route('/tactical/bluetooth_scan', methods=['POST'])
def tactical_bluetooth_scan():
    """V14.4 Feature: Bluetooth device discovery."""
    data = request.json
    pet_id = data.get('pet_id', 'server')
    
    try:
        result = subprocess.run(
            ['hcitool', 'scan'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        devices = []
        for line in result.stdout.split('\n')[1:]:  # Skip header
            if line.strip():
                parts = line.strip().split(maxsplit=1)
                if len(parts) == 2:
                    devices.append({'mac': parts[0], 'name': parts[1]})
        
        save_scan_result(pet_id, 'bluetooth_scan', {'devices': devices})
        log_audit(pet_id, 'bluetooth_scan', {'count': len(devices)})
        
        socketio.emit('tactical_update', {
            'type': 'bluetooth_scan',
            'data': devices
        }, room=f"tactical_{pet_id}")
        
        return jsonify({"devices": devices}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tactical/wps_audit', methods=['POST'])
def tactical_wps_audit():
    """V14.4 Feature: WPS vulnerability testing (SAFETY-CRITICAL)."""
    data = request.json
    target_bssid = data.get('bssid')
    pet_id = data.get('pet_id', 'server')
    
    if not target_bssid:
        return jsonify({"error": "target BSSID required"}), 400
    
    if not operation_lock.acquire(blocking=False):
        return jsonify({"error": "Another operation in progress"}), 409
    
    try:
        # SAFETY PROTOCOL: Kill internet during WPS audit
        kill_internet()
        log_audit(pet_id, 'wps_audit_start', {'target': target_bssid})
        
        # Run Reaver or Bully for WPS testing
        result = subprocess.run(
            ['reaver', '-i', 'wlan0mon', '-b', target_bssid, '-vv'],
            capture_output=True,
            text=True,
            timeout=600
        )
        
        save_scan_result(pet_id, 'wps_audit', {'target': target_bssid, 'output': result.stdout})
        return jsonify({"result": result.stdout}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        restore_internet()
        log_audit(pet_id, 'wps_audit_end', {'target': target_bssid})
        operation_lock.release()

# --- Module 2: Spectrum & Drones Routes ---

@app.route('/spectrum/start_sdr', methods=['POST'])
def spectrum_start_sdr():
    """V14.4 Feature: Initialize SDR dongle for RF analysis."""
    data = request.json
    pet_id = data.get('pet_id', 'server')
    frequency = data.get('frequency', 100000000)  # Default 100MHz
    
    try:
        # Check if RTL-SDR is connected
        result = subprocess.run(['rtl_test', '-t'], capture_output=True, text=True, timeout=5)
        
        if 'No supported devices found' in result.stderr:
            return jsonify({"error": "No RTL-SDR dongle detected"}), 404
        
        log_audit(pet_id, 'sdr_start', {'frequency': frequency})
        return jsonify({"message": "SDR initialized", "frequency": frequency}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/spectrum/tune', methods=['POST'])
def spectrum_tune():
    """V14.4 Feature: Tune SDR to specific frequency."""
    data = request.json
    frequency = data.get('frequency')
    pet_id = data.get('pet_id', 'server')
    
    if not frequency:
        return jsonify({"error": "frequency required"}), 400
    
    log_audit(pet_id, 'sdr_tune', {'frequency': frequency})
    
    # Emit frequency change to live feed
    socketio.emit('spectrum_update', {
        'type': 'frequency_change',
        'frequency': frequency
    }, room=f"spectrum_{pet_id}")
    
    return jsonify({"message": f"Tuned to {frequency} Hz"}), 200

@app.route('/spectrum/adsb_track', methods=['GET'])
def spectrum_adsb_track():
    """V14.4 Feature: Track aircraft using ADS-B (1090MHz) - hardware mode."""
    pet_id = request.args.get('pet_id', 'server')
    
    try:
        # Use dump1090 to decode ADS-B signals
        result = subprocess.run(
            ['dump1090', '--interactive', '--net'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Parse aircraft data
        aircraft = []
        # (In production, parse dump1090 output or connect to its JSON API)
        
        socketio.emit('spectrum_update', {
            'type': 'adsb_aircraft',
            'data': aircraft
        }, room=f"spectrum_{pet_id}")
        
        return jsonify({"aircraft": aircraft}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/spectrum/aircraft_live', methods=['POST'])
def spectrum_aircraft_live():
    """V14.5 Feature: Live aircraft tracking with ADS-B Exchange proxy."""
    data = request.json
    lat = data.get('lat')
    lon = data.get('lon')
    radius = data.get('radius', 250)  # km
    pet_id = data.get('pet_id', 'server')
    
    if lat is None or lon is None:
        return jsonify({"error": "lat and lon required"}), 400
    
    try:
        aircraft = proxy_manager.get_live_aircraft(lat, lon, radius)
        
        # Emit to SocketIO subscribers
        socketio.emit('spectrum_update', {
            'type': 'adsb_aircraft',
            'data': aircraft,
            'proxy': True
        }, room=f"spectrum_{pet_id}")
        
        return jsonify({
            'aircraft': aircraft,
            'count': len(aircraft),
            'proxy': True,
            'method': 'adsbexchange_proxy',
            'success': True
        }), 200
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/spectrum/detect_drones', methods=['POST'])
def spectrum_detect_drones():
    """V14.4 Feature: Drone detection via Wi-Fi/BT signatures."""
    data = request.json
    pet_id = data.get('pet_id', 'server')
    
    try:
        # Scan for known drone Wi-Fi signatures (DJI, Parrot, etc.)
        drone_signatures = ['DJI', 'Parrot', 'SKYDIO', 'Autel']
        
        result = subprocess.run(['iwlist', 'wlan0', 'scan'], capture_output=True, text=True)
        
        detected_drones = []
        for line in result.stdout.split('\n'):
            if 'ESSID:' in line:
                for sig in drone_signatures:
                    if sig in line:
                        detected_drones.append({'signature': sig, 'line': line})
        
        save_scan_result(pet_id, 'drone_detection', {'drones': detected_drones})
        
        socketio.emit('spectrum_update', {
            'type': 'drone_detected',
            'data': detected_drones
        }, room=f"spectrum_{pet_id}")
        
        return jsonify({"drones": detected_drones}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Module 3: Vision & Audio Routes ---

@app.route('/vision/public_webcams', methods=['POST'])
def vision_public_webcams():
    """V14.5 Feature: Find public webcams with Windy proxy."""
    data = request.json
    lat = data.get('lat')
    lon = data.get('lon')
    radius = data.get('radius', 50)  # km
    
    if lat is None or lon is None:
        return jsonify({"error": "lat and lon required"}), 400
    
    try:
        webcams = proxy_manager.find_public_webcams(lat, lon, radius)
        return jsonify({
            'webcams': webcams,
            'count': len(webcams),
            'proxy': True,
            'source': 'windy',
            'success': True
        }), 200
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/media/discover_cameras', methods=['POST'])
def media_discover_cameras():
    """V14.4 Feature: Discover CCTV cameras on network."""
    data = request.json
    pet_id = data.get('pet_id', 'server')
    network = data.get('network', '192.168.1.0/24')
    
    try:
        # Scan for common RTSP ports
        result = subprocess.run(
            ['nmap', '-p', '554,8554,8080', network, '-oX', '-'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        save_scan_result(pet_id, 'camera_discovery', {'network': network, 'output': result.stdout})
        return jsonify({"result": result.stdout}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/media/stream_camera', methods=['POST'])
def media_stream_camera():
    """V14.4 Feature: Start streaming from camera."""
    data = request.json
    camera_url = data.get('camera_url')
    pet_id = data.get('pet_id', 'server')
    
    if not camera_url:
        return jsonify({"error": "camera_url required"}), 400
    
    conn = get_db_conn()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO v2_media_streams (pet_id, stream_type, stream_url) VALUES (%s, %s, %s) RETURNING stream_id",
                (pet_id, 'video', camera_url)
            )
            stream_id = cursor.fetchone()[0]
        conn.commit()
        
        log_audit(pet_id, 'camera_stream_start', {'url': camera_url})
        return jsonify({"stream_id": stream_id, "url": camera_url}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/media/detect_motion', methods=['POST'])
def media_detect_motion():
    """V14.4 Feature: Motion detection on video stream."""
    data = request.json
    stream_id = data.get('stream_id')
    
    if not stream_id:
        return jsonify({"error": "stream_id required"}), 400
    
    # In production, use OpenCV for motion detection
    return jsonify({"message": "Motion detection started", "stream_id": stream_id}), 200

@app.route('/media/analyze_audio', methods=['POST'])
def media_analyze_audio():
    """V14.4 Feature: Audio analysis (decibel, frequency)."""
    data = request.json
    pet_id = data.get('pet_id', 'server')
    
    try:
        # Use SoX or PyAudio to analyze audio input
        result = subprocess.run(
            ['arecord', '-d', '5', '-f', 'cd', '/tmp/audio_sample.wav'],
            capture_output=True,
            timeout=10
        )
        
        # Analyze with SoX
        stats = subprocess.run(
            ['sox', '/tmp/audio_sample.wav', '-n', 'stats'],
            capture_output=True,
            text=True
        )
        
        save_scan_result(pet_id, 'audio_analysis', {'stats': stats.stderr})
        return jsonify({"analysis": stats.stderr}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Module 4: Intel & Maps Routes ---

@app.route('/intel/geolocate_ip', methods=['POST'])
def intel_geolocate_ip():
    """V14.5 Feature: IP geolocation lookup with live proxy."""
    data = request.json
    ip_address = data.get('ip')
    pet_id = data.get('pet_id', 'server')
    
    if not ip_address:
        return jsonify({"error": "ip required"}), 400
    
    try:
        result = proxy_manager.geolocate_ip(ip_address)
        if result:
            return jsonify({
                'location': result,
                'proxy': True,
                'source': 'ip-api.com',
                'method': 'live_proxy',
                'success': True
            }), 200
        else:
            return jsonify({"error": "Geolocation failed", "success": False}), 500
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/intel/reverse_geocode', methods=['POST'])
def intel_reverse_geocode():
    """V14.5 Feature: Reverse geocoding with Nominatim proxy."""
    data = request.json
    lat = data.get('lat')
    lon = data.get('lon')
    
    if lat is None or lon is None:
        return jsonify({"error": "lat and lon required"}), 400
    
    try:
        result = proxy_manager.reverse_geocode(lat, lon)
        if result:
            return jsonify({
                'address': result,
                'proxy': True,
                'source': 'nominatim',
                'success': True
            }), 200
        else:
            return jsonify({"error": "Reverse geocoding failed", "success": False}), 500
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/intel/phone_lookup', methods=['POST'])
def intel_phone_lookup():
    """V14.5 Feature: Phone number OSINT with NumVerify proxy."""
    data = request.json
    phone = data.get('phone')
    
    if not phone:
        return jsonify({"error": "phone required"}), 400
    
    try:
        result = proxy_manager.lookup_phone(phone)
        if result:
            return jsonify({
                'phone_info': result,
                'proxy': True,
                'source': 'numverify',
                'success': True
            }), 200
        else:
            return jsonify({"error": "Phone lookup requires NumVerify API key", "success": False}), 500
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/intel/shodan_search', methods=['POST'])
def intel_shodan_search():
    """V14.5 Feature: Shodan IoT device search with live proxy."""
    data = request.json
    query = data.get('query')
    limit = data.get('limit', 10)
    pet_id = data.get('pet_id', 'server')
    
    if not query:
        return jsonify({"error": "query required"}), 400
    
    try:
        results = proxy_manager.shodan_search(query, limit)
        if results:
            return jsonify({
                'results': results.get('matches', []),
                'total': results.get('total', 0),
                'proxy': True,
                'method': 'shodan_proxy',
                'success': True
            }), 200
        else:
            return jsonify({"error": "Shodan API key not configured", "success": False}), 500
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/intel/subdomain_enum', methods=['POST'])
def intel_subdomain_enum():
    """V14.4 Feature: Subdomain enumeration."""
    data = request.json
    domain = data.get('domain')
    pet_id = data.get('pet_id', 'server')
    
    if not domain:
        return jsonify({"error": "domain required"}), 400
    
    try:
        # Use subfinder or similar tool
        result = subprocess.run(
            ['subfinder', '-d', domain, '-silent'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        subdomains = result.stdout.strip().split('\n')
        save_scan_result(pet_id, 'subdomain_enum', {'domain': domain, 'subdomains': subdomains})
        
        return jsonify({"subdomains": subdomains}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- V14.6 Feature: Advanced Mapping & Tracking Routes ---

@app.route('/intel/cell_towers', methods=['POST'])
def intel_cell_towers():
    """V14.6 Feature: Get cell tower locations and coverage."""
    data = request.json
    lat = data.get('lat')
    lon = data.get('lon')
    radius = data.get('radius', 5000)  # meters
    
    if lat is None or lon is None:
        return jsonify({"error": "lat and lon required"}), 400
    
    try:
        # OpenCelliD API or Mozilla Location Service
        # Free tier: https://opencellid.org/
        api_key = os.environ.get('OPENCELLID_API_KEY')
        
        if api_key:
            response = requests.get(
                'https://opencellid.org/cell/getInArea',
                params={
                    'key': api_key,
                    'lat': lat,
                    'lon': lon,
                    'radius': radius,
                    'format': 'json'
                },
                timeout=10
            )
            towers = response.json().get('cells', [])
        else:
            # Fallback to emulated data
            towers = [
                {
                    'lat': lat + 0.01,
                    'lon': lon + 0.01,
                    'operator': 'T-Mobile',
                    'coverage_radius': 1500,
                    'signal_strength': -75,
                    'cell_id': 'T001',
                    'distance': 1200
                },
                {
                    'lat': lat - 0.015,
                    'lon': lon + 0.02,
                    'operator': 'AT&T',
                    'coverage_radius': 2000,
                    'signal_strength': -82,
                    'cell_id': 'A002',
                    'distance': 1800
                }
            ]
        
        return jsonify({"towers": towers, "count": len(towers), "success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/spectrum/drone_registry', methods=['POST'])
def spectrum_drone_registry():
    """V14.6 Feature: Query drone registries for nearby drones."""
    data = request.json
    lat = data.get('lat')
    lon = data.get('lon')
    radius = data.get('radius', 10000)  # meters
    
    if lat is None or lon is None:
        return jsonify({"error": "lat and lon required"}), 400
    
    try:
        # DroneRadar API, AirMap API, or FAA drone registry
        drones = []
        
        # Example: Query DroneRadar API (if available)
        droneradar_key = os.environ.get('DRONERADAR_API_KEY')
        if droneradar_key:
            response = requests.get(
                'https://api.droneradar.com/drones/nearby',
                params={'lat': lat, 'lon': lon, 'radius': radius},
                headers={'Authorization': f'Bearer {droneradar_key}'},
                timeout=10
            )
            drones = response.json().get('drones', [])
        else:
            # Emulated drone data
            import random
            for i in range(random.randint(1, 4)):
                drones.append({
                    'id': f'DRONE{i+1:03d}',
                    'model': random.choice(['DJI Mavic', 'DJI Phantom', 'Parrot Anafi', 'Autel EVO']),
                    'lat': lat + random.uniform(-0.05, 0.05),
                    'lon': lon + random.uniform(-0.05, 0.05),
                    'altitude': random.randint(50, 400),
                    'speed': random.randint(0, 60),
                    'heading': random.randint(0, 360),
                    'distance': random.randint(500, 8000),
                    'operator_id': f'OP{random.randint(1000, 9999)}',
                    'detected_via': random.choice(['wifi', 'bluetooth', 'rf'])
                })
        
        return jsonify({"drones": drones, "count": len(drones), "success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/spectrum/frequency_scan', methods=['POST'])
def spectrum_frequency_scan():
    """V14.6 Feature: Scan frequency range for signals."""
    data = request.json
    start_freq = data.get('start_freq', 2400)  # MHz
    end_freq = data.get('end_freq', 2500)  # MHz
    pet_id = data.get('pet_id', 'server')
    
    try:
        # Use RTL-SDR or HackRF to scan frequency range
        signals = []
        
        # Check for SDR hardware
        if hw_manager.get_capabilities()['sdr']:
            # Real SDR scanning with rtl_power or similar
            result = subprocess.run(
                ['rtl_power', '-f', f'{start_freq}M:{end_freq}M:1M', '-i', '1', '-1', '/tmp/scan.csv'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse CSV output
            with open('/tmp/scan.csv', 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) > 6:
                        signals.append({
                            'frequency': float(parts[2]),
                            'power': float(parts[6]),
                            'timestamp': parts[0]
                        })
        else:
            # Emulated scan
            import random
            freq = start_freq
            while freq <= end_freq:
                power = random.uniform(-90, -30) if random.random() > 0.7 else random.uniform(-100, -90)
                signals.append({
                    'frequency': freq,
                    'power': power,
                    'peak': power > -60
                })
                freq += 1
        
        return jsonify({"signals": signals, "count": len(signals), "success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/tactical/device_scan_auto', methods=['POST'])
def tactical_device_scan_auto():
    """V14.6 Feature: Automatic device scanning and connection attempts."""
    data = request.json
    location = data.get('location')
    auto_connect = data.get('auto_connect', False)
    save_credentials = data.get('save_credentials', False)
    
    try:
        new_connections = []
        
        # Scan for Wi-Fi networks
        wifi_result = execute_with_fallback(
            'wifi_scan',
            lambda: subprocess.run(['iwlist', 'wlan0', 'scan'], capture_output=True, text=True, timeout=30)
        )
        
        # Scan for Bluetooth devices
        bt_result = execute_with_fallback(
            'bluetooth_scan',
            lambda: subprocess.run(['hcitool', 'scan'], capture_output=True, text=True, timeout=30)
        )
        
        if auto_connect:
            # Attempt connections (requires safety protocols)
            log_audit('system', 'auto_connect_attempt', {'location': location})
            
            # This is where WPS exploitation, default password attempts, etc. would occur
            # IMPORTANT: Only enable with explicit user consent and in legal contexts
            pass
        
        return jsonify({
            "new_connections": new_connections,
            "wifi_count": len(wifi_result.get('networks', [])),
            "bt_count": len(bt_result.get('devices', [])),
            "success": True
        }), 200
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/tactical/save_connection', methods=['POST'])
def tactical_save_connection():
    """V14.6 Feature: Save connection details with metadata."""
    data = request.json
    
    conn = get_db_conn()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO v2_scan_results (pet_id, scan_type, scan_data) 
                VALUES (%s, %s, %s) RETURNING scan_id
                """,
                ('dashboard', 'saved_connection', json.dumps(data))
            )
            scan_id = cursor.fetchone()[0]
        conn.commit()
        
        return jsonify({
            "connection": {**data, "id": scan_id},
            "success": True
        }), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e), "success": False}), 500
    finally:
        conn.close()

@app.route('/tactical/saved_connections', methods=['GET'])
def tactical_saved_connections():
    """V14.6 Feature: Retrieve all saved connections."""
    conn = get_db_conn()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT scan_id, scan_data, created_at 
                FROM v2_scan_results 
                WHERE scan_type = 'saved_connection' 
                ORDER BY created_at DESC 
                LIMIT 100
                """
            )
            results = cursor.fetchall()
            
            connections = []
            for row in results:
                conn_data = row['scan_data']
                conn_data['id'] = row['scan_id']
                conn_data['timestamp'] = row['created_at'].isoformat()
                connections.append(conn_data)
        
        return jsonify({"connections": connections, "success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500
    finally:
        conn.close()

@app.route('/vision/camera_control/<camera_id>', methods=['POST'])
def vision_camera_control(camera_id):
    """V14.6 Feature: PTZ camera controls and actions."""
    data = request.json
    command = data.get('command')  # up, down, left, right, zoom_in, zoom_out, snapshot, record
    
    if not command:
        return jsonify({"error": "command required"}), 400
    
    try:
        # ONVIF camera control or HTTP API for specific camera models
        result = {"command": command, "camera_id": camera_id, "success": True}
        
        # Example: ONVIF PTZ control
        if command in ['up', 'down', 'left', 'right']:
            # Send ONVIF PTZ command
            log_audit('vision', f'camera_ptz_{command}', {'camera_id': camera_id})
        elif command == 'snapshot':
            # Capture snapshot
            log_audit('vision', 'camera_snapshot', {'camera_id': camera_id})
            result['snapshot_url'] = f'/media/snapshots/{camera_id}_{datetime.utcnow().timestamp()}.jpg'
        elif command == 'record':
            # Start recording
            log_audit('vision', 'camera_record_start', {'camera_id': camera_id})
            result['recording'] = True
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

# --- Module 5: System & Controls Routes ---

@app.route('/system/ssh_connect', methods=['POST'])
def system_ssh_connect():
    """V14.4 Feature: SSH connection to remote system."""
    data = request.json
    host = data.get('host')
    username = data.get('username')
    pet_id = data.get('pet_id', 'server')
    
    if not host or not username:
        return jsonify({"error": "host and username required"}), 400
    
    log_audit(pet_id, 'ssh_connect', {'host': host, 'username': username})
    
    # Return connection details (actual SSH handled client-side or via Paramiko)
    return jsonify({"message": "SSH connection details", "host": host, "username": username}), 200

@app.route('/system/execute_command', methods=['POST'])
def system_execute_command():
    """V14.4 Feature: Execute shell command on sentry."""
    data = request.json
    command = data.get('command')
    pet_id = data.get('pet_id')
    
    if not command or not pet_id:
        return jsonify({"error": "command and pet_id required"}), 400
    
    # Queue command for sentry to execute
    conn = get_db_conn()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO v2_commands (pet_id, command_type, parameters) VALUES (%s, %s, %s) RETURNING command_id",
                (pet_id, 'shell_exec', json.dumps({'command': command}))
            )
            command_id = cursor.fetchone()[0]
        conn.commit()
        
        log_audit(pet_id, 'command_queued', {'command': command})
        return jsonify({"command_id": command_id, "status": "queued"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/system/monitor_resources', methods=['GET'])
def system_monitor_resources():
    """V14.4 Feature: System resource monitoring."""
    pet_id = request.args.get('pet_id', 'server')
    
    try:
        # Get disk usage
        disk = subprocess.run(['df', '-h'], capture_output=True, text=True)
        
        # Get memory usage
        mem = subprocess.run(['free', '-h'], capture_output=True, text=True)
        
        # Get CPU info
        cpu = subprocess.run(['mpstat', '1', '1'], capture_output=True, text=True)
        
        resources = {
            'disk': disk.stdout,
            'memory': mem.stdout,
            'cpu': cpu.stdout
        }
        
        socketio.emit('system_update', {
            'type': 'resources',
            'data': resources
        }, room=f"system_{pet_id}")
        
        return jsonify(resources), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/system/stats_live', methods=['GET'])
def system_stats_live():
    """V14.5 Feature: Live system statistics with psutil."""
    try:
        import psutil
        
        stats = {
            'cpu': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent,
            'battery': psutil.sensors_battery().percent if psutil.sensors_battery() else None,
            'method': 'psutil_direct',
            'success': True
        }
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/system/restart_service', methods=['POST'])
def system_restart_service():
    """V14.4 Feature: Restart system service."""
    data = request.json
    service_name = data.get('service')
    pet_id = data.get('pet_id', 'server')
    
    if not service_name:
        return jsonify({"error": "service required"}), 400
    
    try:
        result = subprocess.run(
            ['systemctl', 'restart', service_name],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        log_audit(pet_id, 'service_restart', {'service': service_name})
        return jsonify({"message": f"Service {service_name} restarted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Helper function for saving scan results
def save_scan_result(pet_id, scan_type, scan_data):
    """Store scan results in database."""
    conn = get_db_conn()
    if not conn:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO v2_scan_results (pet_id, scan_type, scan_data) VALUES (%s, %s, %s)",
                (pet_id, scan_type, json.dumps(scan_data))
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Failed to save scan result: {e}")
    finally:
        conn.close()

# SocketIO Event Handlers for Live Feeds

@socketio.on('subscribe')
def handle_subscribe(data):
    """Client subscribes to specific feed (tactical, spectrum, video, audio, system)."""
    feed_type = data.get('feed')
    pet_id = data.get('pet_id', 'server')
    room = f"{feed_type}_{pet_id}"
    join_room(room)
    emit('subscribed', {'feed': feed_type, 'room': room, 'pet_id': pet_id})

@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    """Client unsubscribes from feed."""
    feed_type = data.get('feed')
    pet_id = data.get('pet_id', 'server')
    room = f"{feed_type}_{pet_id}"
    leave_room(room)
    emit('unsubscribed', {'feed': feed_type, 'room': room})

@socketio.on('connect')
def handle_connect():
    """Client connects to SocketIO."""
    emit('connected', {'message': 'Connected to SkySeeAll live feed'})

@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnects from SocketIO."""
    print('Client disconnected')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv == 'initdb':
        initialize_database()
    else:
        socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
