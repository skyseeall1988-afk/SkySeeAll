#!/bin/bash

# Go to the project directory
cd ~/storage/shared/SkySeeAll || exit

echo "--- Starting SkySeeAll Services ---"

# Activate the secret keys
source ~/.bashrc

# Stop any old sessions
tmux kill-session -t skyseall_server 2>/dev/null
tmux kill-session -t skyseall_sentry 2>/dev/null
echo "Stopped old sessions."

# Start the Back-End API Server
echo "Starting Back-End Server in 'skyseall_server' session..."
tmux new-session -d -s skyseall_server 'python app.py'

# Start the Sentry Collector
echo "Starting Sentry Collector in 'skyseall_sentry' session..."
tmux new-session -d -s skyseall_sentry 'python collector.py'

echo "--- All Services Started! ---"
echo "Access your dashboard at http://127.0.0.1:5000"

sleep 2
termux-open-url http://127.0.0.1:5000

