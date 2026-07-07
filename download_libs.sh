#!/bin/bash
# Exit on error
set -e

# Ensure we are in the correct directory
cd "$(dirname "$0")"

echo "===================================================="
echo "  📥 Downloading Python Libraries Locally"
echo "===================================================="

# Create local_libs directory if it doesn't exist
mkdir -p local_libs

# Use the virtual environment's pip to download packages to local_libs
if [ -d "venv" ]; then
    echo "Using venv pip to download libraries..."
    ./venv/bin/pip download -r requirements.txt -d local_libs
else
    echo "venv not found, using system python3/pip..."
    python3 -m pip download -r requirements.txt -d local_libs
fi

echo "===================================================="
echo "  ✅ All libraries successfully downloaded to './local_libs'"
echo "===================================================="
