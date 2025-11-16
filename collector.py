import os
import sys
import json
import time
import requests
import platform
import subprocess
import getpass

# V6: Import Beautiful Soup
try:
    from bs4 import BeautifulSoup
except ImportError:
    print("BeautifulSoup not installed. Run 'pkg install python-beautifulsoup4'")
    sys.exit(1)

# --- Configuration ---
#!!! IMPORTANT!!!
# V7: Pre-filled with your requested username.
USER_ID = "user_skyseeall1988"  # Your registered user_id
PET_ID = "pet_termux_device_01"  # Make this unique for each device
PET_NAME = "Timothy Wells Phone"  # Any name you want

# SERVER_URL = "http://127.0.0.1:8080" # For local testing
# Use your live Render URL for production
SERVER_URL = "https://skyseeall-13.onrender.com"
CHECKIN_INTERVAL = 60  # Check for commands every 60 seconds

# --- Helper Functions ---
def get_system_info():
    """Gathers basic system information to send to the server."""
    return {
        "os_type": platform.system(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "hostname": platform.node(),
        "user": getpass.getuser(),
        "python_version": platform.python_version()
    }

def run_command(command_details):
    """Executes a command from the server and captures its output."""
    command_id = command_details.get('command_id')
    command_type = command_details.get('command_type')
    parameters = command_details.get('parameters', {})
    
    print(f"--- Processing Command ID: {command_id}, Type: {command_type}")
    
    result_payload = {
        "output": "",
        "error": ""
    }
    
    try:
        if command_type == 'run_shell':
            shell_command = parameters.get('command')
            if not shell_command:
                raise ValueError("No 'command' parameter provided for 'run_shell'")
            
            print(f"Executing: {shell_command}")
            # V7: Run Termux API commands
            result = subprocess.run(
                shell_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            result_payload["output"] = result.stdout
            result_payload["error"] = result.stderr
            
            if result.returncode!= 0:
                print(f"Command finished with error. Stderr: {result.stderr}")
            else:
                print(f"Command success. Stdout: {result.stdout}")

        # V6: NEW COMMAND TYPE
        elif command_type == 'scrape_url':
            url = parameters.get('url')
            if not url:
                raise ValueError("No 'url' parameter provided for 'scrape_url'")
            
            print(f"Scraping URL: {url}")
            # Perform a simple web scrape
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an error on bad responses (4xx, 5xx)
            
            # Use BeautifulSoup to get the text
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Break into lines and remove leading/trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Truncate to 5000 characters to avoid huge payloads
            if len(text) > 5000:
                text = text[:5000] + "\n... (truncated)"
                
            result_payload["output"] = text
            print(f"Scraping success, first 100 chars: {text[:100]}...")

        else:
            raise ValueError(f"Unknown command_type: {command_type}")
        
        # Send 'completed' status
        update_command_status(command_id, 'completed', result_payload)

    except Exception as e:
        print(f"!!! Error running command {command_id}: {e}")
        result_payload["error"] = str(e)
        # Send 'failed' status
        update_command_status(command_id, 'failed', result_payload)

# --- Server API Functions ---
def checkin_to_server():
    """Sends system info to the server ('/sentry/checkin')."""
    endpoint = f"{SERVER_URL}/sentry/checkin"
    payload = {
        "user_id": USER_ID,
        "pet_id": PET_ID,
        "pet_name": PET_NAME,
        "pet_data": get_system_info()
    }
    try:
        response = requests.post(endpoint, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"Check-in success: {response.json().get('message')}")
        else:
            print(f"Check-in failed ({response.status_code}): {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Check-in network error: {e}")

def fetch_commands():
    """Asks the server for new commands ('/sentry/get_commands')."""
    endpoint = f"{SERVER_URL}/sentry/get_commands/{PET_ID}"
    try:
        response = requests.get(endpoint, timeout=10)
        if response.status_code == 200:
            data = response.json()
            commands = data.get('commands',)
            if commands:
                print(f"*** Fetched {len(commands)} new command(s) ***")
            else:
                print("No new commands.")
            return commands
        else:
            print(f"Failed to fetch commands ({response.status_code}): {response.text}")
            return
    except requests.exceptions.RequestException as e:
        print(f"Fetch commands network error: {e}")
        return

def update_command_status(command_id, status, result=None):
    """Tells the server the command is done ('/sentry/update_command')."""
    endpoint = f"{SERVER_URL}/sentry/update_command"
    payload = {
        "command_id": command_id,
        "status": status,
        "result": result  # V6: Send the { "output": "...", "error": "..." } payload
    }
    try:
        response = requests.post(endpoint, json=payload, timeout=10)
        if response.status_code!= 200:
            print(f"Failed to update command status ({response.status_code}): {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Update command network error: {e}")

# --- Main Loop ---
def main():
    print(f"--- SkySeeAll Sentry (Collector) V6 ---")
    print(f"Targeting Server: {SERVER_URL}")
    print(f"Registered as User: {USER_ID}")
    print(f"Registered as Pet: {PET_ID}")
    print("---------------------------------------")
    
    if "127.0.0.1" in SERVER_URL:
        print(f"Waiting for User '{USER_ID}' to be registered on the local webpage...")
        print(f"Go to http://127.0.0.1:8080 to register your user.")

    try:
        while True:
            print(f"\n--- {time.ctime()} ---")
            
            # Step 1: Check in
            checkin_to_server()
            
            # Step 2: Fetch commands
            commands = fetch_commands()
            
            # Step 3: Execute commands
            if commands:
                for cmd in commands:
                    run_command(cmd)
                    
            # Step 4: Wait
            print(f"Sleeping for {CHECKIN_INTERVAL} seconds...")
            time.sleep(CHECKIN_INTERVAL)

    except KeyboardInterrupt:
        print("\nSentry shutting down (KeyboardInterrupt).")
    except Exception as e:
        print(f"\nSentry crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
