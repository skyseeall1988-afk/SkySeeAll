# SkySeeAll Hardware Requirements & Emulation Status

## V14.4 Feature: Hardware Detection & Auto-Fallback System

### Overview
The system now automatically detects available hardware and either uses real devices or falls back to realistic emulation. **All features work without physical hardware** for development and testing.

---

## Hardware-Dependent Features Matrix

| Feature | Hardware Required | Emulation Available | Status |
|---------|-------------------|---------------------|---------|
| **Wi-Fi Scanning** | Wi-Fi adapter (managed mode) | ✅ Yes | Auto-fallback |
| **Handshake Capture** | Wi-Fi adapter (monitor mode) | ✅ Yes | Auto-fallback |
| **Deauth Attacks** | Wi-Fi adapter (monitor mode) | ⚠️ Disabled | Hardware only (safety) |
| **Bluetooth Scanning** | Bluetooth adapter | ✅ Yes | Auto-fallback |
| **Nmap Scanning** | Network access | ✅ Yes | Auto-fallback |
| **SDR Spectrum Analysis** | RTL-SDR/HackRF dongle | ✅ Yes | Auto-fallback |
| **ADS-B Aircraft Tracking** | RTL-SDR dongle (1090 MHz) | ✅ Yes | Auto-fallback |
| **Drone Detection** | Wi-Fi/Bluetooth adapters | ✅ Yes | Auto-fallback |
| **Video Streaming** | Camera/Webcam | ✅ Yes (placeholder) | Auto-fallback |
| **Face Recognition** | Camera + processing | ✅ Yes (simulated) | Auto-fallback |
| **Audio Analysis** | Microphone | ✅ Yes | Auto-fallback |
| **GPS Location** | GPS module | ✅ Yes (fake coords) | Auto-fallback |
| **OSINT Tools** | Internet connection | ✅ Yes (cached/sample) | Auto-fallback |
| **System Control** | Remote access | ✅ Yes | Always available |

---

## Hardware Detection Logic

### Automatic Detection on Startup
```python
from hardware_manager import hw_manager, get_hardware_status

# Get current capabilities
status = get_hardware_status()
# Returns: {
#   'capabilities': {
#     'wifi_managed': False,    # Auto-detected
#     'wifi_monitor': False,    # Auto-detected
#     'bluetooth': False,       # Auto-detected
#     'sdr': False,            # Auto-detected
#     'camera': False,         # Auto-detected
#     'microphone': False,     # Auto-detected
#     'gps': False,            # Auto-detected
#     'internet': True         # Auto-detected
#   },
#   'emulation_mode': 'auto',
#   'timestamp': '2025-11-29T...'
# }
```

### Detection Methods

1. **Wi-Fi Adapters**
   - Check: `iwconfig` output for IEEE 802.11 interfaces
   - Monitor mode: `iw list` for monitor capability
   - Fallback: Emulated Wi-Fi scan with realistic SSIDs and signal strengths

2. **Bluetooth**
   - Check: `hcitool dev` for HCI devices
   - Fallback: Emulated device list with common device names

3. **SDR Dongles**
   - Check: `rtl_test -t` for RTL-SDR devices
   - Fallback: Real-time generated FFT data with noise floor and signal peaks

4. **Camera/Video**
   - Check: `/dev/video0` or `/dev/video1` existence
   - Fallback: Placeholder frames (no actual video, but metadata simulated)

5. **Microphone**
   - Check: `arecord -l` for capture devices
   - Fallback: Simulated audio spectrum data

6. **GPS**
   - Check: `/dev/ttyUSB0` or `/dev/ttyACM0` with GPS daemon
   - Fallback: Fake coordinates (random walk around San Francisco)

---

## Emulation Features

### Realistic Data Generation

#### Wi-Fi Networks
- 5-15 random networks with varied SSIDs
- Signal strengths: -90 to -30 dBm (weak to strong)
- Channels: 1, 6, 11 (2.4 GHz) and 36, 40, 44, 149 (5 GHz)
- Security types: WPA2-PSK, WPA3, WEP, Open
- Includes "Hidden Network" entries

#### Bluetooth Devices
- 3-8 random devices
- Device types: phones, audio, computers, peripherals
- MAC addresses: Realistic format
- RSSI values: -90 to -40 dBm

#### Spectrum FFT
- 1024-point FFT array
- Noise floor: ~-90 dBm with ±5 dB variance
- 2-5 signal peaks with Gaussian shape
- Normalized to 0-1 for waterfall display
- Updates in real-time for live visualization

#### Aircraft Tracking (ADS-B)
- 2-8 aircraft in range
- Realistic callsigns: UAL123, DAL456, SWA789
- Altitudes: 5,000-40,000 ft
- Speeds: 200-600 knots
- GPS coordinates: Random positions near reference point

#### Nmap Scans
- 2-5 open ports from common list
- Services: SSH, HTTP, HTTPS, FTP, MySQL, RDP
- OS guesses: Linux, Windows, macOS, FreeBSD
- Realistic XML output format

#### System Stats
- CPU: 10-90% (randomized)
- Memory: 30-80% (randomized)
- Disk: 40-75% (randomized)
- Battery: 20-100% (randomized)
- Temperature: 35-65°C

---

## API Endpoints

### Hardware Status Check
```http
GET /api/hardware/status
```
Returns current hardware detection status.

### Detailed Capabilities
```http
GET /api/hardware/capabilities
```
Returns feature-level availability mapping.

---

## Frontend Integration

### Automatic Feature Disabling

The React frontend automatically queries hardware status on load:

```javascript
useEffect(() => {
  fetch('/api/hardware/capabilities')
    .then(res => res.json())
    .then(data => {
      setHardwareCapabilities(data.capabilities);
      setFeatureAvailability(data.features);
    });
}, []);
```

### UI Indicators

Features show status badges:
- 🟢 **Hardware Available** - Real device detected
- 🟡 **Emulated** - Using simulated data
- 🔴 **Unavailable** - Hardware required, emulation disabled

### Example Usage

```javascript
// Wi-Fi Scan Button
<button 
  className="fluent-button"
  onClick={startWifiScan}
  disabled={!featureAvailability.wifi_scanning}
>
  {featureAvailability.wifi_scanning ? 
    '📡 Wi-Fi Scan' : 
    '📡 Wi-Fi Scan (Hardware Required)'}
</button>
```

---

## Environment Variables

### Emulation Control

```bash
# Force emulation mode (ignore hardware)
export EMULATION_MODE=forced

# Auto-detect and fallback (default)
export EMULATION_MODE=auto

# Hardware-only (no emulation fallback)
export EMULATION_MODE=disabled
```

---

## Safety Features

### Internet Kill Switch
- **Always available** (no hardware dependency)
- Uses `nmcli networking off/on`
- Automatically triggered for:
  - WPS audits
  - Deauth attacks
  - Handshake captures

### Operation Locking
- Prevents concurrent dangerous operations
- Thread-safe with `threading.Lock()`
- Returns 409 Conflict if operation in progress

### Audit Logging
- All operations logged to `v2_audit_logs`
- Includes emulation status
- Tracks internet kill events

---

## Testing Without Hardware

### Quick Start (Emulation Mode)
```bash
# Install dependencies
pip install -r requirements.txt

# Run with emulation
export EMULATION_MODE=auto
python app.py

# All features will work with simulated data!
```

### Verifying Emulation
```bash
# Check hardware status
curl http://localhost:8080/api/hardware/status

# Perform Wi-Fi scan (will use emulation)
curl -X POST http://localhost:8080/tactical/wifi_scan \
  -H "Content-Type: application/json" \
  -d '{"pet_id": "test"}'
```

---

## Production Deployment

### With Real Hardware

1. **Install drivers**
   ```bash
   # Wi-Fi drivers
   sudo apt install wireless-tools aircrack-ng
   
   # Bluetooth
   sudo apt install bluez bluez-tools
   
   # RTL-SDR
   sudo apt install rtl-sdr dump1090
   
   # GPS
   sudo apt install gpsd gpsd-clients
   ```

2. **Run hardware detection**
   ```bash
   python -c "from hardware_manager import hw_manager; \
              print(hw_manager.get_capabilities())"
   ```

3. **Deploy**
   - Hardware will be auto-detected
   - Features automatically enabled
   - Emulation used as fallback only

---

## Feature Availability Summary

### ✅ Always Available (No Hardware)
- System stats monitoring
- Database operations
- SocketIO live feeds
- User interface
- Command queuing
- Audit logging

### 🟡 Auto-Fallback (Emulated if No Hardware)
- Wi-Fi scanning
- Bluetooth scanning
- Spectrum analysis
- Aircraft tracking
- GPS location
- Video streaming metadata
- Audio analysis
- Nmap scanning
- System resource monitoring

### 🔴 Hardware-Only (Safety-Critical)
- Deauth attacks (requires monitor mode)
- Packet injection
- WPS Pixie Dust attacks
- Actual video frames (camera required)

---

## Development Workflow

1. **Develop without hardware** using emulation
2. **Test with real hardware** before deployment
3. **Deploy to production** with auto-detection
4. **Monitor hardware status** via API
5. **Fallback gracefully** if hardware fails

---

**Last Updated**: November 29, 2025  
**Version**: 14.4  
**Feature**: Hardware Detection & Auto-Emulation System
