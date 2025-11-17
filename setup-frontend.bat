@echo off
echo ====================================
echo Interface Wizard - Frontend Setup
echo ====================================
echo.

cd frontend

echo Installing Node.js dependencies...
call npm install

echo.
echo Setup complete!
echo.
echo To run the frontend:
echo   1. cd frontend
echo   2. npm start
echo.
pause
