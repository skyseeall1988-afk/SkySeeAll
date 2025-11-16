#!/bin.bash

# Go to the project directory
cd ~/storage/shared/SkySeeAll || exit

echo "--- SkySeeAll Auto-Update Starting at $(date) ---"

# Pull from GitHub (origin)
echo "Pulling from GitHub..."
git pull origin main

# Install any new python plugins
echo "Installing new Python packages..."
pip install -r requirements.txt

echo "--- SkySeeAll Auto-Update Finished ---"

