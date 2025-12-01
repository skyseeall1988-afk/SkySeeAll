# SkySeeAll Owner's Manual

This manual explains how to install, run, and use every feature in SkySeeAll, how hardware detection and emulation work, and how to safely disable or remove safety-critical features.

## Quick Start (Termux on Android)
1. Prereqs:
   - pkg update && pkg upgrade
   - pkg install git python nodejs openssl
   - pip install --upgrade pip
2. Clone & prepare:
   - git clone https://github.com/skyseeall1988-afk/SkySeeAll.git
   - cd SkySeeAll
   - cp .env.example .env
   - Edit .env with your keys (nano .env). Never commit .env.
3. Install dependencies:
   - pip install -r requirements.txt
   - If frontend exists: npm --prefix ./frontend install && npm --prefix ./frontend run build
4. Start server:
   - Dev: python app.py
   - Prod: gunicorn -k eventlet -w 1 app:app
   - Or use ./run-server.sh (provided)

## Hardware detection & emulation
- hardware_manager.py auto-detects hardware capabilities (wifi_managed, wifi_monitor, bluetooth, sdr, camera, microphone, gps, internet).
- Frontend queries /api/hardware/capabilities to enable/disable UI controls.
- Emulation: when hardware is missing, the emulator returns realistic sample data (Wi-Fi lists, FFTs, ADS-B, camera placeholders).
- When a remote sentry is connected, its real hardware becomes available to the dashboard.

## Live vs Emulated modes
- Live mode uses real hardware or remote sentries.
- Emulated mode provides realistic data for development/testing.
- For services requiring API keys (WiGLE, Shodan, OpenWeather), set the keys in .env.

## Common Features & How to Use Them (step-by-step)
- Wi‑Fi Radar:
  - Click "Wi‑Fi Radar Scan" in Tactical HUD. If hardware is present, live networks stream. If missing, the emulator or WiGLE proxy may provide data.
  - Select a network to view details and available actions.
- SDR / Spectrum:
  - Set frequency and click "Start SDR". If hardware present, uses local SDR. Otherwise emulated FFT or remote SDR sentry.
  - Waterfall displays spectrum history.
- ADS‑B Tracking:
  - Click "Start ADS‑B Tracking". Uses local SDR if present, else ADS‑B Exchange proxy.
- Cameras & Vision:
  - Discover Cameras -> Stream -> Record. If no camera, placeholder frames are used.
- Nmap / OSINT:
  - Enter target in Nmap UI. Shodan and other proxies require API keys in .env.

## Safety-critical features & how to disable
- By default these features are present. To disable without code changes, add flags to your .env:
  - ENABLE_DEAUTH=false
  - ENABLE_HANDSHAKE_CAPTURE=false
  - ENABLE_PACKET_INJECTION=false
  - ENABLE_GPS_SPOOFING=false
- To hard-disable in code (advanced): create a branch, wrap or remove functions (kill_internet, deauth_attack, capture_handshake) and test before merging.

## Owner workflows (backup & restore)
- Backup branch created: main-bu-2025
- To restore main from backup:
  - git checkout main
  - git reset --hard origin/main-bu-2025
  - git push --force origin main

## Remote Sentry setup (Raspberry Pi example)
1. Install collector.py on the remote device and set SERVER_URL to your server.
2. Start the collector; it will check in and appear in the dashboard.
3. The main server will query its reported capabilities and enable UI controls accordingly.

## Troubleshooting
- Feature disabled: check /api/hardware/capabilities and server logs.
- SocketIO issues: ensure server started with eventlet and same origin policy allowed.

## Appendix
- Legal & safety notes: test only on hardware and networks you own. Many actions (jamming, spoofing, deauth) can be illegal and disruptive.