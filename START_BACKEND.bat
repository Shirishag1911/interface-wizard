@echo off
echo ========================================
echo Starting Backend Server
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo Please install Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

cd backend

echo Checking virtual environment...
if not exist venv (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        cd ..
        pause
        exit /b 1
    )
    echo Virtual environment created!
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Checking if dependencies are installed...
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo Dependencies not found. Installing...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        cd ..
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo Starting FastAPI Backend Server...
echo ========================================
echo.
echo Server will be available at:
echo   http://localhost:8000
echo   http://localhost:8000/docs (API Documentation)
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn app.main:app --reload

cd ..
