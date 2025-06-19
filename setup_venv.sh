#!/bin/bash
# RO2 Table Converter - Setup Virtual Environment
# This script creates and configures the Python virtual environment

echo "=========================================="
echo " RO2 Table Converter - Environment Setup"
echo "=========================================="
echo

echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    echo "Please ensure Python 3 is installed and accessible"
    exit 1
fi

echo
echo "Activating virtual environment..."
source venv/bin/activate

echo
echo "Upgrading pip..."
python -m pip install --upgrade pip

echo
echo "Installing required packages..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install requirements"
    exit 1
fi

echo
echo "=========================================="
echo " Setup completed successfully!"
echo "=========================================="
echo
echo "To start the web interface:"
echo "  1. Run: ./start_web_venv.sh"
echo "  2. Or manually: source venv/bin/activate && python app.py"
echo
echo "Virtual environment is ready at: ./venv/"
echo
