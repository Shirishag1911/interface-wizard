@echo off
echo ========================================
echo Fixing Angular Frontend Setup
echo ========================================
echo.

echo Step 1: Check if Angular CLI is installed globally...
call ng version >nul 2>&1
if %errorlevel% neq 0 (
    echo Angular CLI not found. Installing globally...
    call npm install -g @angular/cli
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Failed to install Angular CLI globally.
        echo Please run this script as Administrator.
        echo.
        pause
        exit /b 1
    )
    echo Angular CLI installed successfully!
) else (
    echo Angular CLI is already installed.
)
echo.

echo Step 2: Verify Angular CLI installation...
call ng version
echo.

echo Step 3: Navigate to Angular project...
cd frontend-angular

if not exist package.json (
    echo ERROR: package.json not found!
    echo Make sure you're running this from the project root.
    cd ..
    pause
    exit /b 1
)
echo Found package.json
echo.

echo Step 4: Clean npm cache...
call npm cache clean --force
echo.

echo Step 5: Remove old installations...
if exist node_modules (
    echo Removing node_modules...
    rmdir /s /q node_modules
    echo node_modules removed
) else (
    echo node_modules not found (OK)
)

if exist package-lock.json (
    echo Removing package-lock.json...
    del /f package-lock.json
    echo package-lock.json removed
) else (
    echo package-lock.json not found (OK)
)
echo.

echo Step 6: Installing Angular dependencies...
echo This will take 5-10 minutes. Please wait...
echo.
call npm install

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Angular Setup Complete!
    echo ========================================
    echo.
    echo Dependencies installed successfully!
    echo.
    echo To start Angular development server:
    echo    cd frontend-angular
    echo    ng serve
    echo.
    echo Or simply:
    echo    npm start
    echo.
    echo Server will run on: http://localhost:4200
    echo.
) else (
    echo.
    echo ERROR: Installation failed!
    echo.
    echo Trying alternative method with --legacy-peer-deps...
    echo.
    call npm install --legacy-peer-deps

    if %errorlevel% equ 0 (
        echo.
        echo ========================================
        echo Angular Setup Complete!
        echo ========================================
        echo.
        echo Dependencies installed with legacy peer deps.
        echo.
        echo To start Angular:
        echo    cd frontend-angular
        echo    ng serve
        echo.
    ) else (
        echo.
        echo ERROR: Both installation methods failed!
        echo.
        echo Please try:
        echo 1. Run Command Prompt as Administrator
        echo 2. npm cache clean --force
        echo 3. npm install --verbose
        echo.
        echo Check the error messages above for details.
        echo.
    )
)

cd ..
pause
