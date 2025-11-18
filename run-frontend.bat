@echo off
echo ========================================
echo Interface Wizard - Frontend Launcher
echo ========================================
echo.
echo Which frontend would you like to run?
echo.
echo 1. Angular Frontend (Port 4200)
echo 2. React Frontend (Port 3000)
echo.
set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    call run-frontend-angular.bat
) else if "%choice%"=="2" (
    call run-frontend-react.bat
) else (
    echo Invalid choice. Please run the script again and choose 1 or 2.
    pause
)
