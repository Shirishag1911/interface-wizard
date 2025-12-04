@echo off
echo ========================================
echo Starting Angular Development Server
echo ========================================
echo.

echo Checking if Angular CLI is installed...
call ng version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Angular CLI is not installed!
    echo.
    echo Please run FIX_ANGULAR.bat first to install dependencies.
    echo.
    pause
    exit /b 1
)

echo Angular CLI found!
echo.

cd frontend-angular

echo Checking if node_modules exists...
if not exist node_modules (
    echo ERROR: Dependencies not installed!
    echo.
    echo Please run FIX_ANGULAR.bat first to install dependencies.
    echo.
    cd ..
    pause
    exit /b 1
)

echo Dependencies found!
echo.

echo ========================================
echo Starting Angular Dev Server...
echo ========================================
echo.
echo Server will be available at:
echo   http://localhost:4200
echo.
echo Press Ctrl+C to stop the server
echo.

call ng serve

cd ..
