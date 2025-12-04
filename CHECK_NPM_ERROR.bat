@echo off
echo Checking npm installation...
echo.

where npm
if %errorlevel% neq 0 (
    echo ERROR: npm not found in PATH
    echo.
    echo Please add Node.js to your PATH:
    echo 1. Press Win + R
    echo 2. Type: sysdm.cpl
    echo 3. Go to Advanced -^> Environment Variables
    echo 4. Add to PATH: C:\Program Files\nodejs\
    pause
    exit /b 1
)

echo npm found at:
where npm
echo.

echo Node.js version:
node --version
echo.

echo npm version:
npm --version
echo.

echo npm configuration:
npm config get registry
echo.

echo Testing npm install in temporary directory...
cd %TEMP%
mkdir npm_test_dir 2>nul
cd npm_test_dir
echo {"name":"test","version":"1.0.0"} > package.json
npm install react@18.2.0 --legacy-peer-deps

if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: npm is working correctly!
    echo The issue might be specific to your project.
    echo.
) else (
    echo.
    echo ERROR: npm installation failed even in test directory
    echo This suggests a system-wide npm issue.
    echo.
)

cd %~dp0
pause
