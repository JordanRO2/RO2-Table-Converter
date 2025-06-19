@echo off
REM RO2 Table Converter - Start Web Interface (Virtual Environment)
REM This script activates the virtual environment and starts the Flask app

echo ==========================================
echo  RO2 Table Converter - Starting Web App
echo ==========================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup_venv.bat first to create the environment.
    echo.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting Flask web application...
echo Open your browser to: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python app.py
