#!/bin/sh
# run-server.sh - load .env (if present) and start the Flask server
set -e
if [ -f .env ]; then
  echo "Loading .env"
  set -a
  . .env
  set +a
fi
# Install Python deps (optional)
if [ -f requirements.txt ]; then
  pip install -r requirements.txt || true
fi
# If frontend build exists, skip building here (optional)
# Start the Flask app
if command -v gunicorn >/dev/null 2>&1; then
  echo "Starting with gunicorn + eventlet"
  gunicorn -k eventlet -w 1 app:app
else
  echo "Starting with python app.py"
  python app.py
fi