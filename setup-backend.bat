@echo off
echo ====================================
echo Interface Wizard - Backend Setup
echo ====================================
echo.

cd backend

echo Creating virtual environment...
python -m venv venv

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Setup complete!
echo.
echo To run the backend:
echo   1. cd backend
echo   2. venv\Scripts\activate
echo   3. python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
pause
