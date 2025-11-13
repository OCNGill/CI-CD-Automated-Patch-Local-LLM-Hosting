@echo off
cd /d "%~dp0"

echo "Setting up Python environment and installing dependencies..."
pip install -r requirements.txt

echo "Launching Atlas-GUI..."
streamlit run app.py
