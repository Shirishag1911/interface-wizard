@echo off
REM ============================================================================
REM Interface Wizard - Virtual Machine Setup Script
REM ============================================================================

echo ============================================================
echo Interface Wizard - VM Quick Setup
echo ============================================================
echo.

REM Check Python
echo [1/3] Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed!
    echo.
    echo Please install Python 3.9, 3.10, or 3.11 from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: During installation, check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

python --version
echo [OK] Python is installed
echo.

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo Python version: %PYVER%
echo.

REM Check Node.js
echo [2/3] Checking Node.js installation...
node --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Node.js is not installed
    echo.
    echo To run the frontend, install Node.js 20.10+ from:
    echo https://nodejs.org/
    echo.
) else (
    node --version
    echo [OK] Node.js is installed
)
echo.

REM Check Git
echo [3/3] Checking Git installation...
git --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Git is not installed
    echo.
    echo To clone the repository, install Git from:
    echo https://git-scm.com/download/win
    echo.
) else (
    git --version
    echo [OK] Git is installed
)
echo.

echo ============================================================
echo Setup Summary
echo ============================================================
echo.
echo Next steps:
echo.
echo 1. If not done yet, clone the repository:
echo    git clone https://github.com/Shirishag1911/interface-wizard.git
echo    cd interface-wizard
echo.
echo 2. Setup backend:
echo    setup-backend.bat
echo.
echo 3. Configure .env file:
echo    cd backend
echo    copy .env.example .env
echo    notepad .env
echo    (Add your OPENAI_API_KEY)
echo.
echo 4. Run backend:
echo    cd ..
echo    run-backend.bat
echo.
echo 5. Setup frontend (in new terminal):
echo    setup-frontend.bat
echo    run-frontend-angular.bat  (or run-frontend-react.bat)
echo.
echo ============================================================
echo.

pause
