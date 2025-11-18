@echo off
echo ========================================
echo Clean Restart - Interface Wizard
echo ========================================
echo.

echo [1/5] Stopping any running servers...
echo Please make sure you've stopped the backend and frontend servers (Ctrl+C)
pause

echo.
echo [2/5] Cleaning Python cache files...
cd backend
for /r %%i in (__pycache__) do (
    if exist "%%i" (
        echo Removing %%i
        rmdir /s /q "%%i"
    )
)
del /s /q *.pyc 2>nul
echo Python cache cleaned!

echo.
echo [3/5] Pulling latest code from git...
cd ..
git pull origin main

echo.
echo [4/5] Reinstalling backend dependencies...
cd backend
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install --force-reinstall -r requirements.txt

echo.
echo [5/5] Starting backend server...
echo.
echo ========================================
echo Backend server starting with clean cache
echo Watch for request logs below
echo ========================================
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
