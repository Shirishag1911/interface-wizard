@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Starting Interface Wizard - Angular Frontend
echo ========================================
echo.

echo [1/4] Checking for Node.js installation...
where node >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    echo Recommended version: 18.x or higher
    pause
    exit /b 1
)

echo [OK] Node.js is installed
node --version
npm --version
echo.

echo [2/4] Navigating to Angular frontend directory...
if not exist "frontend-angular" (
    echo [ERROR] frontend-angular directory not found!
    pause
    exit /b 1
)
cd frontend-angular
echo [OK] Changed to frontend-angular directory
echo.

echo [3/4] Installing/updating dependencies...
if not exist "node_modules" (
    echo node_modules not found. Running npm install...
    call npm install
    if errorlevel 1 (
        echo [ERROR] npm install failed!
        pause
        exit /b 1
    )
) else (
    echo node_modules exists. Checking for updates...
    call npm install
)
echo [OK] Dependencies ready
echo.

echo [4/4] Starting Angular development server...
echo.
echo ========================================
echo Server will be available at:
echo http://localhost:4200
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

call npm start
