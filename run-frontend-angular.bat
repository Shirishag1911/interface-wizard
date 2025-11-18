@echo off
echo ========================================
echo Starting Interface Wizard - Angular Frontend
echo ========================================

echo Checking for Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    echo Recommended version: 18.x or higher
    pause
    exit /b 1
)

echo Node.js found:
node --version
npm --version

echo.
echo Navigating to Angular frontend directory...
cd frontend-angular

echo.
echo Checking if node_modules exists...
if not exist "node_modules\" (
    echo node_modules not found. Installing dependencies...
    npm install
) else (
    echo node_modules found. Updating dependencies...
    npm install
)

echo.
echo Starting Angular development server...
echo Server will be available at http://localhost:4200
echo.
npm start
