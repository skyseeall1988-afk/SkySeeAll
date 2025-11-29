# SkySeeAll API Documentation

## V14.5: Live Proxy & Control Module API

---

## Master Control API

### Get Complete System Status
```http
GET /api/control/status
```

**Response:**
```json
{
  "controllers": {
    "tactical": {"feature": "Tactical HUD", "enabled": true, "status": "ready"},
    "spectrum": {"feature": "Spectrum & Drones", "enabled": true, "status": "ready"},
    "intel": {"feature": "Intel & Maps", "enabled": true, "status": "ready"},
    "vision": {"feature": "Vision & Audio", "enabled": true, "status": "ready"},
    "system": {"feature": "System & Controls", "enabled": true, "status": "ready"}
  },
  "hardware": {"wifi_managed": false, "wifi_monitor": false, ...},
  "proxies": {"wigle": false, "shodan": true, ...},
  "timestamp": "2025-11-29T12:00:00"
}
```

### Execute Command
```http
POST /api/control/execute
Content-Type: application/json

{
  "module": "tactical",
  "action": "wifi_scan",
  "parameters": {
    "use_proxy": true,
    "location": {"lat": 37.7749, "lon": -122.4194}
  }
}
```

**Response:**
```json
{
  "networks": [...],
  "count": 12,
  "method": "wigle_proxy",
  "proxy": true,
  "success": true
}
```

### Enable/Disable Module
```http
POST /api/control/module/{module}/enable
POST /api/control/module/{module}/disable
```

Modules: `tactical`, `spectrum`, `intel`, `vision`, `system`

---

## Tactical HUD API (Live Proxy Enabled)

### Wi-Fi Scan with WiGLE Proxy
```http
POST /tactical/wifi_scan
Content-Type: application/json

{
  "pet_id": "pet_01",
  "use_proxy": true,
  "location": {
    "lat": 37.7749,
    "lon": -122.4194
  }
}
```

**Real-World Data Source:** WiGLE.net WiFi database

**Response:**
```json
{
  "networks": [
    {
      "ssid": "Starbucks WiFi",
      "bssid": "00:11:22:33:44:55",
      "signal": -65,
      "channel": 6,
      "security": "WPA2-PSK",
      "lat": 37.7750,
      "lon": -122.4195,
      "source": "wigle",
      "proxy": true
    }
  ],
  "count": 8,
  "proxy": true
}
```

---

## Intel & Maps API (Live Proxies)

### IP Geolocation
```http
POST /intel/geolocate_ip
Content-Type: application/json

{
  "ip": "8.8.8.8",
  "pet_id": "pet_01"
}
```

**Real-World Data Source:** ip-api.com (free tier, 45 req/min)

**Response:**
```json
{
  "location": {
    "ip": "8.8.8.8",
    "city": "Mountain View",
    "region": "California",
    "country": "United States",
    "lat": 37.386,
    "lon": -122.0838,
    "isp": "Google LLC",
    "org": "Google Public DNS",
    "timezone": "America/Los_Angeles"
  },
  "proxy": true,
  "source": "ip-api.com",
  "method": "live_proxy"
}
```

### Shodan Search
```http
POST /intel/shodan_search
Content-Type: application/json

{
  "query": "apache country:US",
  "limit": 10,
  "pet_id": "pet_01"
}
```

**Real-World Data Source:** Shodan.io API (requires API key)

**Response:**
```json
{
  "results": [
    {
      "ip": "192.0.2.1",
      "port": 80,
      "org": "Example Org",
      "location": {"city": "San Francisco", "country_name": "United States"},
      "hostnames": ["example.com"],
      "os": "Linux 3.x",
      "vulns": ["CVE-2021-1234"],
      "source": "shodan",
      "proxy": true
    }
  ],
  "total": 1234567,
  "proxy": true,
  "method": "shodan_proxy"
}
```

### Reverse Geocoding
```http
POST /intel/reverse_geocode
Content-Type: application/json

{
  "lat": 37.7749,
  "lon": -122.4194
}
```

**Real-World Data Source:** OpenStreetMap Nominatim (free)

**Response:**
```json
{
  "address": {
    "house_number": "1",
    "road": "Market Street",
    "city": "San Francisco",
    "state": "California",
    "postcode": "94102",
    "country": "United States"
  },
  "proxy": true,
  "source": "nominatim"
}
```

---

## Spectrum API (Live Aircraft Data)

### Live Aircraft Tracking
```http
POST /spectrum/aircraft_live
Content-Type: application/json

{
  "lat": 37.7749,
  "lon": -122.4194,
  "radius": 250,
  "pet_id": "pet_01"
}
```

**Real-World Data Source:** ADS-B Exchange (public API, no key required)

**Response:**
```json
{
  "aircraft": [
    {
      "callsign": "UAL123",
      "icao": "A12345",
      "altitude": 35000,
      "speed": 450,
      "heading": 270,
      "lat": 37.8049,
      "lon": -122.4294,
      "squawk": "1200",
      "registration": "N12345",
      "type": "B738",
      "distance_km": 12.5,
      "source": "adsbexchange",
      "proxy": true,
      "timestamp": "2025-11-29T12:00:00"
    }
  ],
  "count": 8,
  "proxy": true,
  "method": "adsbexchange_proxy"
}
```

---

## Vision API (Public Webcams)

### Find Public Webcams
```http
POST /vision/public_webcams
Content-Type: application/json

{
  "lat": 37.7749,
  "lon": -122.4194,
  "radius": 50
}
```

**Real-World Data Source:** Windy Webcams API

**Response:**
```json
{
  "webcams": [
    {
      "id": "12345",
      "title": "Golden Gate Bridge View",
      "lat": 37.8199,
      "lon": -122.4783,
      "image": "https://images.webcams.travel/preview/12345.jpg",
      "player": "https://www.webcams.travel/webcam/12345",
      "source": "windy",
      "proxy": true
    }
  ],
  "count": 5,
  "proxy": true
}
```

---

## System API

### Live System Statistics
```http
GET /system/stats_live
```

**Real-World Data Source:** psutil (direct system monitoring)

**Response:**
```json
{
  "cpu": 45.2,
  "memory": 67.8,
  "disk": 72.1,
  "battery": 85.0,
  "method": "psutil_direct",
  "success": true
}
```

---

## Environment Variables for Live Proxies

### Required API Keys

```bash
# Wi-Fi Intelligence (WiGLE)
export WIGLE_API_KEY="username:api_key"

# IoT Search (Shodan)
export SHODAN_API_KEY="your_shodan_api_key"

# IP Geolocation (optional, falls back to free ip-api.com)
export IPGEO_API_KEY="your_ipgeolocation_api_key"

# Reverse Geocoding (optional, falls back to free Nominatim)
export OPENCAGE_API_KEY="your_opencage_api_key"

# Public Webcams (Windy)
export WINDY_API_KEY="your_windy_api_key"

# Weather Data (OpenWeatherMap)
export OPENWEATHER_API_KEY="your_openweather_api_key"

# Phone Number Lookup (NumVerify)
export NUMVERIFY_API_KEY="your_numverify_api_key"
```

### Free Tier Services (No Key Required)

- **ADS-B Exchange**: Live aircraft tracking (public API)
- **ip-api.com**: IP geolocation (45 requests/minute)
- **Nominatim**: Reverse geocoding (1 request/second)
- **Radio Garden**: Radio streaming (public API)

---

## Complete Usage Example

```python
import requests

BASE_URL = "http://localhost:8080"

# 1. Check system status
status = requests.get(f"{BASE_URL}/api/control/status").json()
print(f"System ready: {status['controllers']}")

# 2. Get Wi-Fi networks from WiGLE (real-world data)
wifi_result = requests.post(
    f"{BASE_URL}/tactical/wifi_scan",
    json={
        "use_proxy": True,
        "location": {"lat": 37.7749, "lon": -122.4194}
    }
).json()
print(f"Found {wifi_result['count']} networks via WiGLE")

# 3. Track live aircraft
aircraft = requests.post(
    f"{BASE_URL}/spectrum/aircraft_live",
    json={
        "lat": 37.7749,
        "lon": -122.4194,
        "radius": 250
    }
).json()
print(f"Tracking {aircraft['count']} aircraft via ADS-B Exchange")

# 4. Geolocate an IP
ip_info = requests.post(
    f"{BASE_URL}/intel/geolocate_ip",
    json={"ip": "8.8.8.8"}
).json()
print(f"IP located in {ip_info['location']['city']}")

# 5. Search Shodan
shodan_results = requests.post(
    f"{BASE_URL}/intel/shodan_search",
    json={"query": "apache", "limit": 5}
).json()
print(f"Shodan found {shodan_results['total']} results")
```

---

## Response Indicators

All responses include:
- **`proxy: true/false`** - Whether data came from live proxy
- **`method`** - Data source (e.g., "wigle_proxy", "adsbexchange_proxy", "hardware")
- **`source`** - Specific service name (e.g., "wigle", "shodan", "ip-api.com")
- **`success`** - Operation success status

---

## Rate Limits

### Free Tier Services
- ip-api.com: 45 requests/minute
- Nominatim: 1 request/second
- ADS-B Exchange: ~1 request/minute (public API)

### Paid Services (with API keys)
- WiGLE: Varies by plan
- Shodan: Varies by plan
- IPGeolocation: Varies by plan

---

**Last Updated**: November 29, 2025  
**Version**: 14.5  
**Feature**: Live Proxy Integration & Master Control Module
