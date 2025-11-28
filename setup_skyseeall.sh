#!/bin/bash
# SKYSEEALL V14.6 "BLUE DOG" MASTER INSTALLER

# 1. Create the 7-Folder Structure
echo " Constructing Neural Pathways..."
mkdir -p ~/storage/shared/SkySeeAll_Root/01_APP_DECK_UI/assets
mkdir -p ~/storage/shared/SkySeeAll_Root/01_APP_DECK_UI/css
mkdir -p ~/storage/shared/SkySeeAll_Root/01_APP_DECK_UI/overlays
mkdir -p ~/storage/shared/SkySeeAll_Root/02_APP_CORE_LOGIC/drivers
mkdir -p ~/storage/shared/SkySeeAll_Root/02_APP_CORE_LOGIC/sockets
mkdir -p ~/storage/shared/SkySeeAll_Root/03_APP_MODULES_TOOLS
mkdir -p ~/storage/shared/SkySeeAll_Root/04_APP_DRIVERS_EXT
mkdir -p ~/storage/shared/SkySeeAll_Root/05_DATA_INTEL_PRIVATE/financial_raw
mkdir -p ~/storage/shared/SkySeeAll_Root/06_DATA_INTEL_PUBLIC
mkdir -p ~/storage/shared/SkySeeAll_Root/07_SYSTEM_AUTO

# 2. Install Core Tools (Repositories)
echo " Awakening The Sentry..."
pkg update -y
pkg install -y termux-api python nodejs git aircrack-ng nmap bettercap openssh ffmpeg

# 3. Clone Specific Live Modules
cd ~/storage/shared/SkySeeAll_Root/03_APP_MODULES_TOOLS
git clone https://github.com/devnied/EMV-NFC-Paycard-Enrollment.git
git clone https://github.com/opendroneid/receiver-android.git
git clone https://github.com/osmocom/rtl-sdr.git
git clone https://github.com/bettercap/bettercap.git

# 4. Inject Visual Identity (Blue Dog Theme)
echo "
:root {
    --primary: #00BCD4; /* Blue Dog Cyan */
    --accent: #E91E63; /* Pink Harness */
    --bg: #121212; /* Glass Black */
}
" > ~/storage/shared/SkySeeAll_Root/01_APP_DECK_UI/css/blue_dog.css

# 5. Inject Auto-Commit Logic
echo '
function finish {
    cd ~/storage/shared/SkySeeAll_Root/
    git add.
    git commit -m "Auto-Sync: $(date)"
    git push origin master
}
trap finish EXIT
' >> ~/.bashrc

echo " Initialization Complete. Systems Online."
