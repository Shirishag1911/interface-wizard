@echo off
REM Interface Wizard - UI-Compatible Backend Startup Script (Windows)
REM Version: 4.0

echo ================================================================================
echo   Interface Wizard - UI-Compatible Backend v4.0
echo ================================================================================
echo.

REM Check if we're in the correct directory
if not exist "main_ui_compatible.py" (
    echo ERROR: main_ui_compatible.py not found
    echo Please run this script from the actual-code directory
    pause
    exit /b 1
)

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    echo Please install Python 3.9 or higher
    pause
    exit /b 1
)

echo Python version:
python --version

REM Check if virtual environment exists
if not exist "venv" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Checking dependencies...
pip install -q -r requirements.txt

REM Check if port 8000 is available
echo.
echo Checking if port 8000 is available...
netstat -ano | find ":8000" | find "LISTENING" >nul
if not errorlevel 1 (
    echo WARNING: Port 8000 is already in use
    echo Please stop the existing process or use a different port
    pause
)

REM Start the backend
echo.
echo ================================================================================
echo   Starting Backend Server...
echo ================================================================================
echo.
echo API Base URL: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Interactive API: http://localhost:8000/redoc
echo.
echo Default Credentials:
echo    Username: admin
echo    Password: admin123
echo.
echo Logs: interface_wizard_ui.log
echo.
echo Press CTRL+C to stop the server
echo ================================================================================
echo.

REM Start with Python
python main_ui_compatible.py

REM Cleanup
echo.
echo Server stopped
pause
