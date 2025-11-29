# SkySeeAll - Master Design Document

**Version**: 14.4  
**Last Updated**: November 29, 2025  
**Status**: Active Development

---

## System Overview

SkySeeAll is a comprehensive **tactical intelligence and monitoring platform** that combines network reconnaissance, radio frequency analysis, multimedia surveillance, OSINT capabilities, and remote system control into a unified C2 (Command & Control) architecture.

### Core Philosophy
- **Safety-First Design**: Critical operations automatically disable internet connectivity
- **Live Feed Architecture**: Real-time data streaming inspired by Microsoft's interactive OS design
- **Distributed Sensing**: Multiple sentry nodes working collaboratively
- **Interactive HUD**: High-contrast, mission-focused interface

---

## Module 1: Tactical HUD (Network & Active Scanning)

### Purpose
Real-time network reconnaissance and active scanning with safety protocols for secure operations.

### Safety Protocols
- **Internet Kill Switch**: Automatically disables internet connectivity during sensitive operations (WPS audit, deauth attacks)
- **One-Operation-at-Time**: Prevents conflicting network states
- **Audit Logging**: All operations logged to `v2_audit_logs` table

### Features

#### Wi-Fi Intelligence
- **Wi-Fi Radar**: Live 2D/3D visualization of nearby networks with RSSI heatmaps
- **Hotspot Detection**: Identify rogue access points and evil twin attacks
- **SSID Analysis**: Hidden network detection, WPS vulnerability scanning
- **Handshake Capture**: WPA/WPA2 handshake collection for offline analysis
- **Deauthentication Alerts**: Monitor for active deauth attacks in vicinity

#### Network Scanning
- **Nmap Integration**: Port scanning, OS fingerprinting, service detection
- **Bluetooth Scanning**: Device discovery, MAC address collection, service enumeration
- **ARP Scanning**: Local network mapping, duplicate IP detection
- **DNS Enumeration**: Subdomain discovery, zone transfer attempts

#### Security Tools
- **WPS Audit**: Test WPS PIN vulnerabilities (Pixie Dust, brute force)
- **SMB/FTP Browser**: Network share enumeration and file browsing
- **Packet Capture**: Live packet sniffing with Wireshark integration

#### Implementation Endpoints
```python
# Tactical HUD Routes (app.py)
POST /tactical/wifi_scan         # Initiate Wi-Fi scan
POST /tactical/nmap_scan         # Run Nmap with parameters
POST /tactical/bluetooth_scan    # Bluetooth device discovery
POST /tactical/wps_audit         # WPS vulnerability test (kills internet)
GET  /tactical/live_feed         # SocketIO stream for live radar
POST /tactical/capture_handshake # Start handshake capture
```

---

## Module 2: Spectrum & Drones (Radio Frequencies)

### Purpose
Radio frequency analysis and aerial/maritime tracking using SDR (Software Defined Radio).

### Hardware Requirements
- **RTL-SDR USB Dongle** (RTL2832U chipset recommended)
- **Antenna**: Wideband (25MHz-1.7GHz) or specialized (ADS-B, AIS)

### Safety Protocols
- **Single Frequency Lock**: Only one active frequency at a time to prevent interference
- **Power Limiting**: Transmit power capped at safe levels (when using HackRF/BladeRF)
- **Dongle Health Check**: Pre-flight diagnostics before operations

### Features

#### Radio Spectrum Analysis
- **Waterfall Chart**: Live FFT visualization of frequency spectrum
- **Frequency Tuning**: Manual tuning from 24MHz to 1.7GHz
- **Signal Demodulation**: AM/FM/SSB modes for audio recovery
- **Recording**: Save IQ samples for offline analysis

#### Aerial & Maritime Tracking
- **ADS-B (Aircraft)**: Track aircraft position, altitude, speed, callsign
  - Live flight paths overlaid on map
  - Historical trajectory replay
  - Collision alerts for low-flying aircraft
- **AIS (Ships)**: Maritime vessel tracking (MMSI, position, course)
  - Port traffic monitoring
  - Fishing vessel identification

#### Drone Detection
- **Wi-Fi Signature Analysis**: Detect DJI, Parrot, Skydio drones via Wi-Fi beacons
- **Bluetooth LE**: Track drone controllers (RC transmitters)
- **RF Fingerprinting**: Identify custom/DIY drones via 2.4GHz/5.8GHz emissions

#### Sensor Monitoring
- **TPMS (Tire Pressure)**: Monitor vehicle tire sensors (315MHz/433MHz)
- **Weather Stations**: Decode personal weather station data (433MHz/915MHz)
- **Smart Meters**: Electric/gas/water meter telemetry (900MHz ISM band)
- **Gas Leak Detectors**: Industrial sensor monitoring

#### Live Audio Feeds
- **Police/Fire Radios**: Scan public safety frequencies (requires legal clearance)
- **Ham Radio**: Monitor amateur bands (HF, VHF, UHF)
- **NOAA Weather Radio**: Automated weather broadcasts (162.400-162.550 MHz)

#### Satellite Overlays
- **NOAA Satellites**: APT image decoding from NOAA 15/18/19
- **Meteor-M2**: LRPT high-resolution weather imagery
- **ISS SSTV**: Decode images from International Space Station

#### Implementation Endpoints
```python
# Spectrum & Drones Routes (app.py)
POST /spectrum/start_sdr          # Initialize SDR with frequency
POST /spectrum/tune               # Change frequency/mode
GET  /spectrum/waterfall          # SocketIO stream for FFT data
POST /spectrum/adsb_track         # Start ADS-B decoder (dump1090)
POST /spectrum/ais_track          # Start AIS decoder
POST /spectrum/detect_drones      # Scan for drone signatures
GET  /spectrum/live_audio         # Stream demodulated audio
POST /spectrum/decode_noaa        # Process NOAA APT recording
```

---

## Module 3: Vision & Audio (Media)

### Purpose
Multimedia surveillance, recording, and analysis with AI-powered detection.

### Safety Protocols
- **Speaker Mute**: Automatically mutes speakers during covert audio capture
- **Recording Indicator**: LED/UI indicator when recording active (transparency mode)
- **Storage Quota**: Auto-delete old recordings when disk space < 10%

### Features

#### Video Surveillance
- **CCTV Streaming**: Connect to IP cameras (RTSP, HTTP, ONVIF protocols)
- **Camera Discovery**: Scan network for exposed cameras (Shodan integration)
- **Video Recording**: H.264/H.265 encoding with configurable bitrates
- **Motion Detection**: OpenCV-based motion alerts with zone configuration
- **Face Recognition**: dlib/face_recognition for person identification
- **License Plate Reader**: ALPR using Tesseract OCR + custom models
- **Night Vision**: IR camera support with auto-switching

#### Audio Analysis
- **Decibel Meter**: Real-time SPL measurement (A-weighted)
- **Infrasound Detection**: <20Hz monitoring for earthquakes, explosions
- **Ultrasound Detection**: >20kHz monitoring for pest repellers, covert comms
- **Voice Recording**: Multi-channel audio capture with noise reduction
- **Sound Playback**: Trigger pre-recorded sounds (alarms, warnings)
- **Audio Fingerprinting**: Shazam-like identification for audio sources

#### Implementation Endpoints
```python
# Vision & Audio Routes (app.py)
POST /media/discover_cameras      # Scan for IP cameras
POST /media/stream_camera         # Start RTSP stream
POST /media/start_recording       # Begin video/audio capture
POST /media/detect_motion         # Enable motion detection zones
POST /media/recognize_face        # Run face recognition on frame
POST /media/read_license_plate    # OCR on vehicle plate
GET  /media/decibel_meter         # SocketIO stream for SPL data
POST /media/ultrasound_scan       # Monitor >20kHz frequencies
POST /media/play_sound            # Trigger audio playback (mutes speakers first)
```

---

## Module 4: Intel & Maps (OSINT)

### Purpose
Open-source intelligence gathering, geospatial analysis, and reconnaissance.

### Features

#### Geospatial Intelligence
- **3D Mapping**: Cesium.js-based terrain visualization
- **IP Geolocation**: Plot IP addresses on map (MaxMind GeoIP2)
- **Heatmap Overlays**: Wi-Fi RSSI, device density, threat levels
- **Route Planning**: Calculate optimal paths between waypoints
- **Geofencing**: Alert when devices enter/leave zones

#### Database Lookups
- **Phone Number OSINT**: Reverse lookup via Truecaller API
- **Email Intelligence**: Hunter.io, Have I Been Pwned checks
- **MAC Address Vendor**: IEEE OUI database lookups
- **User Profiling**: Social media aggregation (Sherlock, Maltego)
- **Domain WHOIS**: Ownership, registration date, nameservers

#### Security Checks
- **SSL/TLS Analysis**: Certificate validation, cipher suite checks
- **Router Credential Check**: Default password database (192.168.1.1 admin/admin)
- **Subdomain Enumeration**: Subfinder, Amass for DNS discovery
- **Shodan Integration**: Search for exposed services, CVEs
- **Vulnerability Scanning**: Nessus/OpenVAS integration for known exploits

#### Implementation Endpoints
```python
# Intel & Maps Routes (app.py)
POST /intel/geolocate_ip          # Get lat/lon from IP
POST /intel/phone_lookup          # OSINT on phone number
POST /intel/email_check           # Verify email, check breaches
POST /intel/mac_vendor            # Lookup MAC OUI
GET  /intel/map_overlay           # Serve 3D map with layers
POST /intel/subdomain_enum        # Discover subdomains
POST /intel/shodan_search         # Query Shodan API
POST /intel/ssl_audit             # Analyze HTTPS certificate
POST /intel/router_default_creds  # Check default password DB
```

---

## Module 5: System & Controls

### Purpose
Remote system administration and sentry node management.

### Features

#### Remote Access
- **SSH/SFTP**: Secure shell and file transfer
- **ADB Shell**: Android Debug Bridge for mobile devices
- **VNC/RDP**: Graphical desktop access
- **Command Execution**: Run arbitrary commands on sentries

#### System Monitoring
- **Disk Space**: Real-time storage usage alerts
- **Battery Level**: Monitor device power status
- **CPU/RAM Usage**: System resource graphs
- **Network Traffic**: RX/TX bandwidth monitoring
- **Temperature**: CPU/GPU thermal readings

#### Service Management
- **Restart Services**: Apache, Nginx, PostgreSQL, etc.
- **System Updates**: apt/yum package updates
- **Process Management**: Kill/restart processes
- **Cron Jobs**: Schedule recurring tasks

#### UI Features
- **Night Mode**: Red/amber UI for low-light operations
- **HUD Profiles**: Save/load custom dashboard layouts
- **Dongle Check**: Verify RTL-SDR, HackRF, WiFi adapters

#### Implementation Endpoints
```python
# System & Controls Routes (app.py)
POST /system/ssh_connect          # Establish SSH tunnel
POST /system/execute_command      # Run command on sentry
GET  /system/resource_monitor     # SocketIO stream for CPU/RAM
POST /system/restart_service      # systemctl restart <service>
POST /system/update_system        # Run system updates
POST /system/toggle_night_mode    # Switch UI theme
POST /system/check_dongle         # Verify SDR hardware
```

---

## Live Feed Architecture (Microsoft-Inspired)

### Real-Time Data Flow
SkySeeAll uses **SocketIO** for bidirectional, low-latency communication between sentries and the server.

#### Feed Types
1. **Tactical Feed**: Wi-Fi radar, network scans (1-second updates)
2. **Spectrum Feed**: FFT waterfall data (10 FPS)
3. **Video Feed**: MJPEG/WebRTC camera streams (15-30 FPS)
4. **Audio Feed**: Live audio demodulation (44.1kHz sample rate)
5. **Telemetry Feed**: System metrics (5-second intervals)

#### SocketIO Events
```javascript
// Client subscribes to feeds
socket.emit('subscribe', {feed: 'tactical', pet_id: 'pet_01'});

// Server pushes live data
socket.on('tactical_update', (data) => {
  // Update radar visualization
  updateWiFiRadar(data.networks);
});

// Spectrum waterfall
socket.on('spectrum_fft', (data) => {
  // Render FFT bins to canvas
  drawWaterfall(data.frequencies, data.magnitudes);
});
```

---

## Database Schema Extensions

### New Tables for Features

```sql
-- Module 1: Tactical HUD
CREATE TABLE v2_wifi_scans (
    scan_id SERIAL PRIMARY KEY,
    pet_id VARCHAR(255) REFERENCES v2_pets(pet_id),
    networks JSONB,  -- Array of {ssid, bssid, rssi, channel, encryption}
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE v2_audit_logs (
    log_id SERIAL PRIMARY KEY,
    pet_id VARCHAR(255),
    operation VARCHAR(100),  -- 'wps_audit', 'deauth', etc.
    internet_killed BOOLEAN,
    details JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Module 2: Spectrum & Drones
CREATE TABLE v2_adsb_tracks (
    track_id SERIAL PRIMARY KEY,
    pet_id VARCHAR(255),
    icao24 VARCHAR(6),  -- Aircraft hex code
    callsign VARCHAR(10),
    latitude FLOAT,
    longitude FLOAT,
    altitude INT,
    velocity INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE v2_drone_detections (
    detection_id SERIAL PRIMARY KEY,
    pet_id VARCHAR(255),
    drone_type VARCHAR(50),  -- 'DJI', 'Parrot', 'Unknown'
    mac_address VARCHAR(17),
    rssi INT,
    latitude FLOAT,
    longitude FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Module 3: Vision & Audio
CREATE TABLE v2_recordings (
    recording_id SERIAL PRIMARY KEY,
    pet_id VARCHAR(255),
    media_type VARCHAR(10),  -- 'video', 'audio'
    file_path TEXT,
    duration INT,  -- seconds
    filesize BIGINT,  -- bytes
    metadata JSONB,  -- {resolution, codec, fps, etc.}
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE v2_face_detections (
    detection_id SERIAL PRIMARY KEY,
    recording_id INT REFERENCES v2_recordings(recording_id),
    person_id VARCHAR(255),  -- Links to known persons DB
    confidence FLOAT,
    bounding_box JSONB,  -- {x, y, width, height}
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Module 4: Intel & Maps
CREATE TABLE v2_osint_queries (
    query_id SERIAL PRIMARY KEY,
    pet_id VARCHAR(255),
    query_type VARCHAR(50),  -- 'phone', 'email', 'ip', etc.
    query_value TEXT,
    results JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE v2_geofences (
    geofence_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    center_lat FLOAT,
    center_lon FLOAT,
    radius_meters INT,
    alert_on_enter BOOLEAN,
    alert_on_exit BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Security & Safety Protocols

### Internet Kill Switch Implementation
```python
def kill_internet():
    """Disables internet connectivity for safety-critical operations."""
    subprocess.run(['nmcli', 'networking', 'off'], check=True)
    # Log operation
    log_audit('internet_kill', {'reason': 'wps_audit_initiated'})

def restore_internet():
    """Re-enables internet after operation completes."""
    subprocess.run(['nmcli', 'networking', 'on'], check=True)
    log_audit('internet_restore', {'reason': 'operation_complete'})
```

### Operation Locks
```python
# Global lock to prevent concurrent dangerous operations
operation_lock = threading.Lock()

@app.route('/tactical/wps_audit', methods=['POST'])
def wps_audit():
    if not operation_lock.acquire(blocking=False):
        return jsonify({"error": "Another operation in progress"}), 409
    try:
        kill_internet()
        # Perform WPS audit
        result = run_wps_pixie_dust(target_bssid)
        return jsonify(result), 200
    finally:
        restore_internet()
        operation_lock.release()
```

---

## Deployment Checklist

### Prerequisites
- [ ] RTL-SDR dongle connected and recognized (`lsusb | grep RTL`)
- [ ] Termux API installed on Android sentries (`pkg install termux-api`)
- [ ] PostgreSQL with JSONB support (v12+)
- [ ] Flask-SocketIO with eventlet
- [ ] OpenCV, dlib, face_recognition for video analysis
- [ ] Nmap, aircrack-ng, reaver for network tools

### Configuration
1. Update `collector.py` with server URL
2. Set environment variables: `DATABASE_URL`, `ADMIN_TOKEN`, `SHODAN_API_KEY`
3. Initialize database: `python app.py initdb`
4. Test SDR: `rtl_test -t` (should see no errors)
5. Verify camera access: `ffmpeg -list_devices true -f dshow -i dummy` (Windows) or `v4l2-ctl --list-devices` (Linux)

---

## Roadmap

### V14.4 (Current)
- [ ] Implement Tactical HUD routes
- [ ] Add Wi-Fi radar visualization
- [ ] Integrate Nmap scanning

### V14.5 (Q1 2026)
- [ ] SDR spectrum waterfall
- [ ] ADS-B tracking with live map
- [ ] Drone detection algorithm

### V14.6 (Q2 2026)
- [ ] CCTV streaming
- [ ] Face recognition pipeline
- [ ] License plate reader

### V15.0 (Q3 2026)
- [ ] Full OSINT module
- [ ] 3D mapping with Cesium
- [ ] Geofencing alerts

---

**End of Master Design Document**
