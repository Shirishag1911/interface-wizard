@echo off
echo ========================================
echo Interface Wizard - Windows Setup Script
echo ========================================
echo.

REM Check Node.js installation
echo Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed!
    echo Please download and install Node.js from: https://nodejs.org/
    pause
    exit /b 1
)

echo Node.js found!
node --version
npm --version
echo.

REM Install Angular CLI globally
echo ========================================
echo Installing Angular CLI globally...
echo ========================================
call npm install -g @angular/cli
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Angular CLI
    pause
    exit /b 1
)
echo.

REM Setup Backend
echo ========================================
echo Setting up Python Backend...
echo ========================================
cd backend
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        echo Make sure Python is installed: python --version
        cd ..
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    cd ..
    pause
    exit /b 1
)

cd ..
echo Backend setup complete!
echo.

REM Setup Angular Frontend
echo ========================================
echo Setting up Angular Frontend...
echo ========================================
cd frontend-angular

echo Cleaning cache...
call npm cache clean --force

echo Installing dependencies...
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Angular dependencies
    cd ..
    pause
    exit /b 1
)

cd ..
echo Angular frontend setup complete!
echo.

REM Setup React Frontend
echo ========================================
echo Setting up React Frontend...
echo ========================================
cd frontend-react

echo Cleaning cache...
call npm cache clean --force

echo Installing dependencies...
call npm install --legacy-peer-deps
if %errorlevel% neq 0 (
    echo ERROR: Failed to install React dependencies
    cd ..
    pause
    exit /b 1
)

cd ..
echo React frontend setup complete!
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the application:
echo.
echo 1. Backend:
echo    cd backend
echo    venv\Scripts\activate
echo    uvicorn app.main:app --reload
echo.
echo 2. Angular Frontend (in new terminal):
echo    cd frontend-angular
echo    ng serve
echo.
echo 3. React Frontend (in new terminal):
echo    cd frontend-react
echo    npm start
echo.
echo Access URLs:
echo - Backend API: http://localhost:8000/docs
echo - Angular: http://localhost:4200
echo - React: http://localhost:3000
echo.
pause
