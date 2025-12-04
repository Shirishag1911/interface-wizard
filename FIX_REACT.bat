@echo off
echo ========================================
echo Fixing React Frontend Setup
echo ========================================
echo.

cd frontend-react

echo Step 1: Cleaning npm cache...
call npm cache clean --force

echo.
echo Step 2: Removing old node_modules...
if exist node_modules (
    rmdir /s /q node_modules
    echo node_modules removed
) else (
    echo node_modules not found (OK)
)

echo.
echo Step 3: Removing package-lock.json...
if exist package-lock.json (
    del /f package-lock.json
    echo package-lock.json removed
) else (
    echo package-lock.json not found (OK)
)

echo.
echo Step 4: Installing dependencies with legacy-peer-deps...
echo This will take 5-10 minutes...
call npm install --legacy-peer-deps

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo React Setup Complete!
    echo ========================================
    echo.
    echo To start React frontend:
    echo    npm start
    echo.
    echo Server will run on: http://localhost:3000
    echo.
) else (
    echo.
    echo ERROR: Installation failed!
    echo Please check the error messages above.
    echo.
)

pause
