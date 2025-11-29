import requests
import time
import os
import platform

# V14 Configuration
SERVER_URL = "https://skyseeall-v14.onrender.com" # Update this after Render deploy
DEVICE_ID = "termux_sentry_01"

def checkin():
    print(f"--- Contacting Command Center: {SERVER_URL} ---")
    try:
        # Simple health check / log push
        payload = {
            "device_id": DEVICE_ID,
            "log_data": {"status": "online", "battery": "unknown"}
        }
        # In a real scenario, this would post to an endpoint
        print("Check-in packet sent.")
    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    while True:
        checkin()
        time.sleep(60) # Sleep to avoid 'Phantom Process' kill
