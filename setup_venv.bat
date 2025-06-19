@echo off
REM RO2 Table Converter - Setup Virtual Environment
REM This script creates and configures the Python virtual environment

echo ==========================================
echo  RO2 Table Converter - Environment Setup
echo ==========================================
echo.

echo Creating virtual environment...
python -m venv venv
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to create virtual environment
    echo Please ensure Python is installed and accessible
    pause
    exit /b 1
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing required packages...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

echo.
echo ==========================================
echo  Setup completed successfully!
echo ==========================================
echo.
echo To start the web interface:
echo   1. Run: start_web_venv.bat
echo   2. Or manually: venv\Scripts\activate.bat && python app.py
echo.
echo Virtual environment is ready at: .\venv\
echo.
pause
