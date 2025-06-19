@echo off
REM RO2 Table Converter - Windows Setup Script
REM Community tool for converting RO2 CT files to Excel format

echo.
echo ========================================
echo  RO2 Table Converter - Community Tool
echo ========================================
echo.

if "%1"=="install" goto install
if "%1"=="run" goto run
if "%1"=="help" goto help
if "%1"=="" goto help

:help
echo USAGE:
echo   setup.bat install    Install dependencies
echo   setup.bat run        Start the web interface
echo   setup.bat help       Show this help
echo.
echo REPOSITORY:
echo   https://github.com/JordanRO2/RO2-Table-Converter
echo.
echo This is a community-driven tool for Ragnarok Online 2
goto end

:install
echo Installing dependencies...
python -m pip install -r requirements.txt
if %errorlevel% == 0 (
    echo.
    echo ✅ Dependencies installed successfully!
    echo 💡 Run "setup.bat run" to start the web interface
) else (
    echo.
    echo ❌ Failed to install dependencies
    echo 💡 Make sure Python 3.8+ is installed and in PATH
)
goto end

:run
echo Starting RO2 Table Converter...
echo Web interface: http://localhost:5000
echo Press Ctrl+C to stop
echo.
python app.py
goto end

:end
pause
