#!/bin/bash
# RO2 Table Converter - Start Web Interface (Virtual Environment)
# This script activates the virtual environment and starts the Flask app

echo "=========================================="
echo " RO2 Table Converter - Starting Web App"
echo "=========================================="
echo

if [ ! -f "venv/bin/activate" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run ./setup_venv.sh first to create the environment."
    echo
    exit 1
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo
echo "Starting Flask web application..."
echo "Open your browser to: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo

python app.py
