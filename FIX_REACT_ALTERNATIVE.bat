@echo off
echo ========================================
echo Alternative React Setup Method
echo ========================================
echo.

cd frontend-react

echo Checking if we're in the right directory...
if not exist package.json (
    echo ERROR: package.json not found!
    echo Make sure you're running this from the project root.
    cd ..
    pause
    exit /b 1
)

echo Found package.json
echo.

echo Step 1: Clean npm cache...
call npm cache clean --force
echo.

echo Step 2: Set npm registry (in case of network issues)...
call npm config set registry https://registry.npmjs.org/
echo.

echo Step 3: Remove old files...
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del /f package-lock.json
echo.

echo Step 4: Try installing with different approaches...
echo.
echo Attempt 1: Standard install with legacy-peer-deps...
call npm install --legacy-peer-deps

if %errorlevel% equ 0 (
    echo.
    echo SUCCESS! Dependencies installed.
    goto :success
)

echo.
echo Attempt 1 failed. Trying Attempt 2...
echo.
echo Attempt 2: Install with force flag...
call npm install --legacy-peer-deps --force

if %errorlevel% equ 0 (
    echo.
    echo SUCCESS! Dependencies installed.
    goto :success
)

echo.
echo Attempt 2 failed. Trying Attempt 3...
echo.
echo Attempt 3: Install without optional dependencies...
call npm install --legacy-peer-deps --no-optional

if %errorlevel% equ 0 (
    echo.
    echo SUCCESS! Dependencies installed.
    goto :success
)

echo.
echo All attempts failed!
echo.
echo Please try manual installation:
echo 1. Open Command Prompt as Administrator
echo 2. cd C:\Users\siri\Work\InterfaceWizard\interface-wizard\frontend-react
echo 3. npm cache clean --force
echo 4. npm install --legacy-peer-deps --verbose
echo.
echo The --verbose flag will show detailed error information.
echo.
goto :end

:success
echo.
echo ========================================
echo React Setup Complete!
echo ========================================
echo.
echo To start React:
echo    npm start
echo.
echo Server will run on: http://localhost:3000
echo.

:end
cd ..
pause
