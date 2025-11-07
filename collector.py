import subprocess
import json
import time
import requests

API_ENDPOINT = "http://127.0.0.1:5000/api/report"

def run_termux_command(command):
    """Runs a Termux:API command and returns the JSON output."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=15)
        if result.stderr:
            print(f"Error running {command[0]}: {result.stderr}")
            return None
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Exception with {command[0]}: {e}")
        return None

def post_data(data_type, payload):
    """Sends collected data to the main 'app.py' server."""
    try:
        data = {"type": data_type, "payload": payload}
        response = requests.post(API_ENDPOINT, json=data, timeout=10)
        if response.status_code == 200:
            print(f"Successfully reported {len(payload)} {data_type} devices.")
        else:
            print(f"Error reporting data: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Error posting data: {e}")

def scan_wifi():
    """Scans for Wi-Fi networks."""
    print("Scanning for Wi-Fi...")
    command = ['termux-wifi-scaninfo']
    data = run_termux_command(command)
    if data:
        post_data('wifi', data)

def scan_bluetooth():
    """Scans for Bluetooth devices."""
    print("Scanning for Bluetooth...")
    # Note: True Bluetooth scanning requires 'termux-bluetooth -c'
    # This is a placeholder for what 'termux-api' can provide
    command = ['termux-bluetooth-scaninfo']
    data = run_termux_command(command)
    if data:
        post_data('bluetooth', data)

# --- Main Sentry Loop ---
if __name__ == "__main__":
    print("Starting SkySeeAll Sentry (Collector)...")
    while True:
        scan_wifi()
        time.sleep(10)

        scan_bluetooth()
        time.sleep(10)

        print("--- Loop complete, sleeping for 30 seconds ---")
        time.sleep(30)

