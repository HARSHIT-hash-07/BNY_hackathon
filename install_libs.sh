#!/bin/bash
# Exit on error
set -e

# Ensure we are in the correct directory
cd "$(dirname "$0")"

echo "===================================================="
echo "  🛠️ Setting Up Virtual Env & Installing Local Libraries"
echo "===================================================="

# Check if venv exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment 'venv'..."
    python3 -m venv venv
else
    echo "Using existing 'venv' virtual environment."
fi

# Upgrade pip locally if possible
echo "Installing requirements from local directory './local_libs'..."
./venv/bin/pip install --no-index --find-links=local_libs -r requirements.txt

echo "===================================================="
echo "  🚀 Verifying Library Installation"
echo "===================================================="
./venv/bin/python -c "import pandas, numpy, sklearn, xgboost, shap, matplotlib, seaborn, plotly, streamlit, imblearn; print('All imports successful!')"

echo "===================================================="
echo "  ✅ Virtual Environment successfully configured from local copy!"
echo "===================================================="
