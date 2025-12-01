# SkySeeAll GitHub Copilot Instructions for SkySeeAll

## Architecture Overview (Tactical Intelligence C2 System)
SkySeeAll is a **comprehensive tactical intelligence platform** combining network reconnaissance, radio frequency analysis, multimedia surveillance, and OSINT capabilities. See `MASTER_DESIGN.md` for complete feature specifications.

### 3-Tier C2 Architecture
1. **Tier 1 - Frontend**: React SPA with live feed UI (Microsoft-inspired interactive design)
2. **Tier 2 - Backend**: Flask monolith with SocketIO for real-time bidirectional streaming
3. **Tier 3 - Sentries**: Distributed `collector.py` nodes on remote devices (Termux on Android, Raspberry Pi, etc.)

### 5 Core Modules
1. **Tactical HUD**: Network scanning (Wi-Fi radar, Nmap, Bluetooth, WPS audit)
2. **Spectrum & Drones**: SDR analysis (ADS-B aircraft tracking, drone detection, radio monitoring)
3. **Vision & Audio**: Multimedia (CCTV streaming, face recognition, license plate reader, audio analysis)
4. **Intel & Maps**: OSINT (IP geolocation, phone/email lookup, Shodan integration, 3D mapping)
5. **System & Controls**: Remote admin (SSH, ADB, resource monitoring, service management)

**Critical Data Flow**:
- Sentries POST to `/sentry/checkin` with sensor payloads (Wi-Fi scans, GPS, system stats)
- Real-time feeds via SocketIO: `tactical_update`, `spectrum_fft`, `video_frame`, `audio_stream`
- Commands queued in `v2_commands` table with status machine: `pending` → `sent` → `completed`

## Key Files & Directories
- `app.py`: Flask backend with all API routes (172 lines, monolith pattern)
- `collector.py`: Autonomous sentry agent for remote deployment (runs on Termux/RPi)
- `MASTER_DESIGN.md`: Complete feature specifications for all 5 modules
- `render.yaml`: Unified build pipeline: `pip install` → `npm install` → `npm run build` → `gunicorn`
- `package.json`: React frontend with socket.io-client, leaflet (maps), cesium (3D terrain)
- `build/`: Compiled React SPA served by Flask catch-all route

## Module-Specific Route Patterns
When adding features, namespace routes by module:
- **Tactical HUD**: `/tactical/*` (wifi_scan, nmap_scan, bluetooth_scan, wps_audit)
- **Spectrum**: `/spectrum/*` (start_sdr, tune, waterfall, adsb_track, detect_drones)
- **Media**: `/media/*` (discover_cameras, stream_camera, detect_motion, recognize_face)
- **Intel**: `/intel/*` (geolocate_ip, phone_lookup, shodan_search, subdomain_enum)
- **System**: `/system/*` (ssh_connect, execute_command, restart_service)
- **Sentry**: `/sentry/*` (checkin, get_commands, report_result)

## Critical Implementation Patterns

### Database Interaction (Manual Connection Management)
**Pattern**: Direct `psycopg2.connect(DATABASE_URL)` without connection pooling (current limitation).

```python
# Always use this exact pattern in app.py:
conn = get_db_conn()
if not conn:
    return jsonify({"error": "Database connection failed"}), 500
try:
    with conn.cursor() as cursor:  # or cursor_factory=psycopg2.extras.RealDictCursor
        cursor.execute("SELECT ... WHERE x = %s", (param,))  # ALWAYS parameterized
    conn.commit()
except Exception as e:
    conn.rollback()  # Critical: rollback before finally
    return jsonify({"error": str(e)}), 500
finally:
    conn.close()  # MUST close manually (no pooling)
```

### Schema Design (v2_* Tables)
All tables use `v2_` prefix (historical versioning). Schema lives in `initialize_database()` function (no migrations):
- `v2_users`: Simple user registry (`user_id` PK)
- `v2_pets`: Sentry devices with JSONB telemetry (`pet_id` PK, references `user_id`)
- `v2_commands`: Queue with status machine (`command_id` serial, `status` = 'pending'/'sent')

**When adding fields**: Modify `initialize_database()`, test with `python app.py initdb` (schema is idempotent with `IF NOT EXISTS`).

### Version Comments (V14.x System)
This codebase uses inline version tags for major features. **Always add version tags** for significant changes:
```python
# V14.4 Feature: Tactical HUD - Wi-Fi Radar
# V14.3 Feature: OAuth Integration
# V14.2 ARCHITECTURE: Hybrid-Monolith Setup
```

### Safety-Critical Operations
Some operations require **internet kill switch** to prevent data leaks:
```python
import subprocess

def kill_internet():
    """Disables networking during sensitive operations (WPS audit, deauth)."""
    subprocess.run(['nmcli', 'networking', 'off'], check=True)
    log_audit('internet_kill', {'reason': 'wps_audit_initiated'})

def restore_internet():
    """Re-enables networking after operation completes."""
    subprocess.run(['nmcli', 'networking', 'on'], check=True)
    log_audit('internet_restore', {'reason': 'operation_complete'})

# Use operation locks to prevent concurrent dangerous operations
operation_lock = threading.Lock()

@app.route('/tactical/wps_audit', methods=['POST'])
def wps_audit():
    if not operation_lock.acquire(blocking=False):
        return jsonify({"error": "Another operation in progress"}), 409
    try:
        kill_internet()
        result = run_wps_pixie_dust(target_bssid)
        return jsonify(result), 200
    finally:
        restore_internet()
        operation_lock.release()
```

### Live Feed Pattern (SocketIO Streaming)
Real-time data uses SocketIO with room-based targeting:
```python
@socketio.on('subscribe')
def handle_subscribe(data):
    """Client subscribes to specific feed (tactical, spectrum, video, audio)."""
    feed_type = data.get('feed')  # 'tactical', 'spectrum', 'video', 'audio'
    pet_id = data.get('pet_id')
    room = f"{feed_type}_{pet_id}"
    join_room(room)
    emit('subscribed', {'feed': feed_type, 'room': room})

# Background thread pushes updates to room
def stream_tactical_updates(pet_id):
    while True:
        wifi_data = get_latest_wifi_scan(pet_id)
        socketio.emit('tactical_update', wifi_data, room=f"tactical_{pet_id}")
        socketio.sleep(1)  # 1Hz update rate

# Start background thread when sentry checks in
socketio.start_background_task(stream_tactical_updates, pet_id='pet_01')
```

#  SPA Serving (Catch-All Route)
The React frontend is served via Flask's catch-all pattern (lines 81-94 in `app.py`):
```python
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    # If file exists in build/, serve it; else return index.html for React Router
```
**Implication**: Frontend routes are client-side only. Backend routes must be namespaced (e.g., `/sentry/*`, `/api/*`) to avoid conflicts.

### SocketIO Configuration
```python
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
```
**Critical**: `async_mode='eventlet'` required for Gunicorn deployment. If you add socket handlers, use:
```python
@socketio.on('event_name')
def handler(data):
    emit('response', {"status": "ok"}, room=request.sid)
```

## Development Workflows

### Local Development
```bash
# Backend only (no React compilation)
python app.py  # Starts on port 8080 (or $PORT), runs with socketio.run()

# Initialize/reset database schema
python app.py initdb  # Runs initialize_database(), safe to re-run (idempotent)

# Full stack (compile React + run backend)
npm install && npm run build  # Creates build/ folder
python app.py  # Serves React from build/
```

### Deployment (Render.com)
Defined in `render.yaml`:
1. Build: `pip install → npm install → npm run build`
2. Start: `gunicorn -k eventlet -w 1 app:app` (single worker for SocketIO state)
3. Env vars: `DATABASE_URL` (from NeonDB), `SECRET_KEY` (auto-generated), `ADMIN_TOKEN` (manual)

**Important**: Render's free tier sleeps after inactivity. Sentries will fail check-ins until app wakes.

## Security Implementation

### Environment Variables (All Secrets External)
```python
DATABASE_URL = os.environ.get('DATABASE_URL')  # NeonDB connection string
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN')    # For future admin routes
```
**Never commit** `.env` files. Local dev: use `python-dotenv` to load `.env` (not implemented yet but in requirements.txt).

### HTTPS Enforcement (Flask-Talisman)
```python
Talisman(app, content_security_policy=None, force_https=True)
```
Forces HTTPS in production. **Disable for local dev** if needed: `Talisman(app, force_https=False)` when `DEBUG=True`.

### SQL Injection Prevention
**100% of queries use parameterized statements**:
```python
cursor.execute("SELECT * FROM v2_pets WHERE pet_id = %s", (pet_id,))  # ✅ CORRECT
cursor.execute(f"SELECT * FROM v2_pets WHERE pet_id = '{pet_id}'")     # ❌ NEVER DO THIS
```

## Testing (Not Yet Implemented)
**Aspirational**: Use `pytest` with 70% coverage. When adding tests:
- Mock `get_db_conn()` to return test connections
- Test routes with `app.test_client()`: `client.post('/sentry/checkin', json={...})`
- Name tests: `test_<function>_<scenario>` (e.g., `test_sentry_checkin_missing_user_id_returns_400`)

## Naming Conventions
- Python: `snake_case` (functions/variables), `PascalCase` (classes), `UPPER_SNAKE_CASE` (constants)
- Tables: `v2_<name>` prefix (e.g., `v2_pets`)
- Routes: RESTful paths with namespaces (e.g., `/sentry/checkin`, `/api/v2/users`)

## Git Workflow (Conventional Commits)
```bash
# Branch naming: feat/<desc>, fix/<desc>, chore/<desc>
git checkout -b feat/add-live-video-stream

# Commit format: <type>(<scope>): <description>
git commit -m "feat(sentry): add webcam snapshot capture to collector.py"
git commit -m "fix(database): add missing index on v2_commands.status"
```

## Common Mistakes to Avoid
1. **Forgetting to close connections**: Always use `finally: conn.close()` (no pooling yet)
2. **String formatting in SQL**: Use `%s` placeholders, never f-strings or `.format()` in queries
3. **Conflicting routes**: Backend routes must avoid `/` and single-word paths (reserved for React Router)
4. **SocketIO worker count**: Must use `-w 1` with Gunicorn (multi-worker breaks state sharing)
5. **JSONB column types**: When inserting dicts into JSONB, use `json.dumps(data)` in psycopg2

## Adding New Features

### New Sentry Endpoint (Example: Execute Command)
```python
@app.route('/sentry/report_result', methods=['POST'])
def sentry_report_result():
    data = request.json
    command_id = data.get('command_id')
    result = data.get('result')
    
    conn = get_db_conn()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500
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
```

### New Database Table
1. Add DDL to `initialize_database()` (append to `schema_sql` string)
2. Use `CREATE TABLE IF NOT EXISTS` for idempotency
3. Test with `python app.py initdb`
4. For production: consider manual `ALTER TABLE` if schema already exists

## Dependency Management
**Current stack** (see `requirements.txt`):
- Flask 3.0.0, Flask-SocketIO 5.3.6, psycopg2-binary 2.9.9
- eventlet 0.33.3 (SocketIO async backend), Flask-Talisman 1.1.0 (HTTPS)
- requests 2.31.0, beautifulsoup4 4.12.2 (for collector.py scraping)

**Adding dependencies**: Update `requirements.txt` with exact versions, test locally, redeploy to Render.

## GitHub Copilot Automatic Code Review Setup

### Overview
GitHub Copilot can automatically review pull requests to catch bugs, security issues, and style violations before human review.

### Configuration Options

#### Option 1: Personal Setting (Your PRs Only - Copilot Pro/Pro+ Required)
1. Go to GitHub.com → Profile picture → Copilot settings
2. Locate "Automatic Copilot code review" dropdown
3. Select **Enabled**
4. Copilot will now review all your new pull requests automatically

#### Option 2: Repository-Level (All PRs in SkySeeAll)
Requires repository admin access:
1. Navigate to **SkySeeAll repository** → Settings → Code and automation → Rules → Rulesets
2. Click **New branch ruleset**
3. Configure:
   - **Ruleset name**: `copilot-auto-review`
   - **Enforcement Status**: Active
   - **Target branches**: Include default branch (main) or Include all branches
   - **Branch rules**: Check "Automatically request Copilot code review"
     - ✅ **Review new pushes** (optional: reviews every push, not just initial PR)
     - ✅ **Review draft pull requests** (optional: catch issues early)
4. Click **Create**

#### Option 3: Organization-Level (Multiple Repos)
Requires organization admin access:
1. GitHub.com → Organizations → SkySeeAll → Settings
2. Code, planning, and automation → Repository → Rulesets
3. Click **New branch ruleset**
4. Configure:
   - **Ruleset name**: `org-copilot-reviews`
   - **Enforcement Status**: Active
   - **Target repositories**: Add pattern (e.g., `*` for all, `SkySee*` for prefix match)
   - **Target branches**: Include default branch or all branches
   - **Branch rules**: Check "Automatically request Copilot code review"
5. Click **Create**

### What Copilot Reviews
- **Security**: SQL injection, XSS, hardcoded secrets, insecure dependencies
- **Bugs**: Logic errors, null references, type mismatches, off-by-one errors
- **Style**: Convention violations (e.g., missing `v2_` prefix, non-parameterized queries)
- **Architecture**: Route conflicts with SPA, missing connection cleanup, JSONB handling

### Review Workflow
1. Create PR from feature branch (e.g., `feat/new-command-endpoint`)
2. Copilot automatically comments within minutes with findings
3. Address feedback by pushing new commits (re-reviews if "Review new pushes" enabled)
4. Copilot updates its review status when issues are resolved
5. Request human review after Copilot approval

### Best Practices
- **Enable "Review draft pull requests"** to catch issues before requesting human review
- **Tag PRs** with `[WIP]` prefix during development to signal draft status
- **Reference issue numbers** in PR descriptions for better context (e.g., "Fixes #42")
- **Small PRs**: Keep changes focused (<300 lines) for more accurate reviews

---

**Last Updated**: November 29, 2025 | **Version**: 14.3 | **Maintainer**: skyseeall1988-afk