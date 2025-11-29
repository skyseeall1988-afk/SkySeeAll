# SkySeeAll Setup Guide
## V14.5: Live Proxy & Control Module Configuration

---

## Quick Start

```bash
# 1. Clone repository
git clone https://github.com/yourusername/SkySeeAll.git
cd SkySeeAll

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Node.js dependencies
npm install

# 4. Build React frontend
npm run build

# 5. Configure environment variables (see below)
cp .env.example .env
# Edit .env with your API keys

# 6. Initialize database
python app.py initdb

# 7. Run application
python app.py
```

Application will be available at `http://localhost:8080`

---

## Environment Variables

### Required Configuration

Create `.env` file in project root:

```bash
# Database (NeonDB or PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/database

# Flask Security
SECRET_KEY=your_random_secret_key_here

# Admin Access (for future admin routes)
ADMIN_TOKEN=your_admin_token_here
```

### Optional API Keys (Live Proxies)

Add these to `.env` to enable real-world data sources:

#### 1. Wi-Fi Intelligence (WiGLE)
**Purpose**: Real-world Wi-Fi network database lookup

```bash
WIGLE_API_KEY=username:api_key
```

**Setup**:
1. Register at https://wigle.net/account
2. Go to Account → Show My Token
3. Format: `username:encoded_key`

**Free Tier**: 50 queries per day

#### 2. IoT Search (Shodan)
**Purpose**: Search internet-connected devices, security intelligence

```bash
SHODAN_API_KEY=your_shodan_api_key
```

**Setup**:
1. Register at https://account.shodan.io/register
2. View API key at https://account.shodan.io/
3. Copy API key

**Free Tier**: 100 results per month

#### 3. IP Geolocation (IPGeolocation.io - Optional)
**Purpose**: Enhanced IP geolocation (free tier: ip-api.com is default)

```bash
IPGEO_API_KEY=your_ipgeolocation_api_key
```

**Setup**:
1. Register at https://ipgeolocation.io/signup.html
2. View API key in dashboard
3. Copy API key

**Free Tier**: 1,000 requests per day  
**Default Fallback**: ip-api.com (45 requests/minute, no key required)

#### 4. Reverse Geocoding (OpenCage - Optional)
**Purpose**: Convert coordinates to addresses (free tier: Nominatim is default)

```bash
OPENCAGE_API_KEY=your_opencage_api_key
```

**Setup**:
1. Register at https://opencagedata.com/users/sign_up
2. View API key in dashboard
3. Copy API key

**Free Tier**: 2,500 requests per day  
**Default Fallback**: Nominatim (1 request/second, no key required)

#### 5. Public Webcams (Windy)
**Purpose**: Find public webcam streams worldwide

```bash
WINDY_API_KEY=your_windy_api_key
```

**Setup**:
1. Register at https://api.windy.com/webcams/docs
2. Request API key
3. Copy API key

**Free Tier**: Varies by usage

#### 6. Weather Data (OpenWeatherMap)
**Purpose**: Real-time weather information

```bash
OPENWEATHER_API_KEY=your_openweather_api_key
```

**Setup**:
1. Register at https://home.openweathermap.org/users/sign_up
2. View API key in API keys section
3. Copy API key

**Free Tier**: 1,000 calls per day

#### 7. Phone Lookup (NumVerify)
**Purpose**: Phone number validation and lookup

```bash
NUMVERIFY_API_KEY=your_numverify_api_key
```

**Setup**:
1. Register at https://numverify.com/product
2. View API key in dashboard
3. Copy API key

**Free Tier**: 250 requests per month

---

## Services Without API Keys (Always Available)

These services work immediately without configuration:

### ADS-B Exchange (Aircraft Tracking)
- **What**: Real-time aircraft positions worldwide
- **API**: Public API, no key required
- **Rate Limit**: ~1 request/minute
- **Endpoint**: `/spectrum/aircraft_live`

### ip-api.com (IP Geolocation)
- **What**: IP address geolocation
- **API**: Free tier, no key required
- **Rate Limit**: 45 requests/minute
- **Endpoint**: `/intel/geolocate_ip`

### Nominatim (Reverse Geocoding)
- **What**: Convert coordinates to addresses (OpenStreetMap)
- **API**: Free, no key required
- **Rate Limit**: 1 request/second
- **Endpoint**: `/intel/reverse_geocode`

### Radio Garden
- **What**: Live radio streams from around the world
- **API**: Public API, no key required
- **Endpoint**: Not yet implemented (planned)

---

## Database Setup

### Option 1: NeonDB (Recommended for Production)

1. Register at https://neon.tech
2. Create new project
3. Copy connection string
4. Add to `.env`:
   ```bash
   DATABASE_URL=postgresql://user:password@host.neon.tech/database?sslmode=require
   ```

### Option 2: Local PostgreSQL

```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE skyseeall;
CREATE USER skyseeall_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE skyseeall TO skyseeall_user;
\q

# Add to .env
DATABASE_URL=postgresql://skyseeall_user:your_password@localhost:5432/skyseeall
```

### Initialize Schema

```bash
python app.py initdb
```

This creates 6 tables:
- `v2_users`: User registry
- `v2_pets`: Sentry devices (Termux/RPi agents)
- `v2_commands`: Command queue for remote sentries
- `v2_scan_results`: Scan data storage
- `v2_audit_logs`: Security audit logs
- `v2_media_streams`: Video/audio stream metadata

---

## Hardware Detection

SkySeeAll automatically detects available hardware:

### Supported Hardware

- **Wi-Fi Adapters**: Managed mode (scanning), Monitor mode (packet injection)
- **Bluetooth**: HCI devices (scanning, tracking)
- **SDR Devices**: RTL-SDR dongles (spectrum analysis, ADS-B decoding)
- **Cameras**: V4L2 devices, RTSP cameras
- **Microphones**: ALSA audio input
- **GPS**: USB GPS receivers

### Check Hardware Status

```bash
# Via API
curl http://localhost:8080/api/hardware/status

# Or through Control Module
curl http://localhost:8080/api/control/status
```

### Hardware Requirements by Feature

| Feature | Hardware Required | Live Proxy Alternative |
|---------|------------------|----------------------|
| Wi-Fi Scanning | Wi-Fi adapter | WiGLE API ✅ |
| Packet Injection | Monitor mode adapter | N/A |
| Bluetooth Scanning | Bluetooth adapter | N/A |
| Spectrum Analysis | RTL-SDR dongle | N/A |
| Aircraft Tracking | RTL-SDR (ADS-B) | ADS-B Exchange ✅ |
| IP Geolocation | Internet | ip-api.com ✅ |
| Webcam Streams | Local camera | Windy API ✅ |
| Phone Lookup | Internet | NumVerify API ✅ |

---

## Deployment

### Render.com (Recommended)

1. **Fork Repository** on GitHub

2. **Connect to Render**:
   - Go to https://dashboard.render.com
   - New → Web Service
   - Connect your GitHub repository

3. **Configure Build**:
   - Build Command: `pip install -r requirements.txt && npm install && npm run build`
   - Start Command: `gunicorn -k eventlet -w 1 app:app`

4. **Environment Variables** (Render Dashboard):
   ```
   DATABASE_URL=<your_neondb_url>
   SECRET_KEY=<generate_random_key>
   ADMIN_TOKEN=<your_admin_token>
   WIGLE_API_KEY=<optional>
   SHODAN_API_KEY=<optional>
   # ... other API keys
   ```

5. **Deploy**: Render will auto-deploy on push to `main`

### Manual Deployment (VPS/Cloud)

```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip nodejs npm postgresql-client

# Clone and setup
git clone https://github.com/yourusername/SkySeeAll.git
cd SkySeeAll
pip install -r requirements.txt
npm install
npm run build

# Configure environment
cp .env.example .env
nano .env  # Add your configuration

# Initialize database
python app.py initdb

# Run with Gunicorn
gunicorn -k eventlet -w 1 -b 0.0.0.0:8080 app:app
```

### Systemd Service (Auto-start on boot)

Create `/etc/systemd/system/skyseeall.service`:

```ini
[Unit]
Description=SkySeeAll Tactical Intelligence Platform
After=network.target

[Service]
Type=simple
User=skyseeall
WorkingDirectory=/opt/SkySeeAll
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/opt/SkySeeAll/.env
ExecStart=/usr/local/bin/gunicorn -k eventlet -w 1 -b 0.0.0.0:8080 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable skyseeall
sudo systemctl start skyseeall
sudo systemctl status skyseeall
```

---

## Remote Sentry Setup (Termux on Android)

Deploy `collector.py` on remote devices for distributed intelligence gathering:

### Termux Installation

```bash
# Install Termux from F-Droid (not Google Play)
# Inside Termux:

# Update packages
pkg update && pkg upgrade

# Install Python and dependencies
pkg install python git

# Install Python packages
pip install requests beautifulsoup4

# Clone repository
git clone https://github.com/yourusername/SkySeeAll.git
cd SkySeeAll

# Configure collector
nano collector.py
# Edit SERVER_URL to your SkySeeAll instance URL

# Run collector
python collector.py
```

### Raspberry Pi Setup

```bash
# SSH into Raspberry Pi
ssh pi@raspberrypi.local

# Update system
sudo apt update && sudo apt upgrade

# Clone repository
git clone https://github.com/yourusername/SkySeeAll.git
cd SkySeeAll

# Install dependencies
pip install -r requirements.txt

# Run collector
python collector.py
```

---

## Testing

### API Testing

```bash
# Test control status
curl http://localhost:8080/api/control/status

# Test proxy status
curl http://localhost:8080/api/proxy/status

# Test Wi-Fi scan with WiGLE
curl -X POST http://localhost:8080/tactical/wifi_scan \
  -H "Content-Type: application/json" \
  -d '{"use_proxy": true, "location": {"lat": 37.7749, "lon": -122.4194}}'

# Test aircraft tracking
curl -X POST http://localhost:8080/spectrum/aircraft_live \
  -H "Content-Type: application/json" \
  -d '{"lat": 37.7749, "lon": -122.4194, "radius": 250}'

# Test IP geolocation
curl -X POST http://localhost:8080/intel/geolocate_ip \
  -H "Content-Type: application/json" \
  -d '{"ip": "8.8.8.8"}'
```

### Frontend Testing

1. Open browser to `http://localhost:8080`
2. Navigate through 5 modules:
   - Tactical HUD
   - Spectrum & Drones
   - Vision & Audio
   - Intel & Maps
   - System & Controls
3. Check hardware status badges (🟢 Hardware, 🟡 Emulated, 🔴 Unavailable)
4. Test live feeds via SocketIO

---

## Troubleshooting

### Database Connection Failed

**Problem**: `Database connection failed` error

**Solution**:
```bash
# Check DATABASE_URL is set
echo $DATABASE_URL

# Test connection manually
psql $DATABASE_URL -c "SELECT 1"

# Reinitialize schema
python app.py initdb
```

### API Keys Not Working

**Problem**: 401 Unauthorized or API errors

**Solution**:
```bash
# Check environment variables are loaded
python -c "import os; print(os.environ.get('WIGLE_API_KEY'))"

# Test API manually
curl -H "Authorization: Basic YOUR_WIGLE_KEY" \
  "https://api.wigle.net/api/v2/network/search?onlymine=false&latrange1=37.7&latrange2=37.8&longrange1=-122.5&longrange2=-122.4"
```

### Hardware Not Detected

**Problem**: All features show 🔴 Unavailable

**Solution**:
```bash
# Check hardware manually
iwconfig  # Wi-Fi
hciconfig  # Bluetooth
rtl_test  # SDR
v4l2-ctl --list-devices  # Cameras

# Install missing tools
sudo apt install wireless-tools bluez rtl-sdr v4l-utils
```

### SocketIO Not Connecting

**Problem**: Live feeds not updating

**Solution**:
- Check browser console for SocketIO errors
- Ensure `eventlet` is installed: `pip install eventlet`
- Verify Gunicorn uses correct worker: `-k eventlet -w 1`

---

## Security Notes

### Production Checklist

- [ ] Enable HTTPS (Flask-Talisman auto-enforces)
- [ ] Use strong `SECRET_KEY` (generate with `openssl rand -hex 32`)
- [ ] Rotate `ADMIN_TOKEN` regularly
- [ ] Use PostgreSQL SSL mode (NeonDB includes by default)
- [ ] Restrict database access to application IP
- [ ] Enable firewall rules (allow only 8080/443)
- [ ] Keep API keys in `.env`, never commit to Git
- [ ] Use `ADMIN_TOKEN` for future admin routes
- [ ] Monitor audit logs (`v2_audit_logs` table)

### Rate Limiting

Consider adding rate limiting for public deployments:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/tactical/wifi_scan')
@limiter.limit("10 per minute")
def tactical_wifi_scan():
    # ...
```

---

## Support

- **Documentation**: See `MASTER_DESIGN.md` for feature specifications
- **API Reference**: See `API_DOCUMENTATION.md`
- **Hardware Guide**: See `HARDWARE_EMULATION.md`
- **GitHub Issues**: https://github.com/yourusername/SkySeeAll/issues

---

**Last Updated**: November 29, 2025  
**Version**: 14.5  
**Maintainer**: skyseeall1988-afk
