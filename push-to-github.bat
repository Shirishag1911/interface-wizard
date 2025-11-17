@echo off
echo ============================================================
echo GitHub Push Script - Interface Wizard
echo ============================================================
echo.

REM Check if remote exists
git remote get-url origin >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] No remote configured yet.
    echo.
    echo Please provide your GitHub repository URL.
    echo Example: https://github.com/Shirishag1911/interface-wizard.git
    echo.
    set /p REPO_URL="Enter GitHub repository URL: "

    echo.
    echo [INFO] Adding remote 'origin'...
    git remote add origin !REPO_URL!

    if %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] Remote added successfully!
    ) else (
        echo [ERROR] Failed to add remote.
        pause
        exit /b 1
    )
)

echo.
echo [INFO] Current remote configuration:
git remote -v
echo.

REM Rename branch to main if it's master
for /f "tokens=2" %%i in ('git branch --show-current') do set BRANCH=%%i
git branch -M main 2>nul

echo [INFO] Pushing to GitHub...
echo.
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo [SUCCESS] Code pushed to GitHub successfully!
    echo ============================================================
    echo.
    echo Your code is now on GitHub at:
    git remote get-url origin
    echo.
) else (
    echo.
    echo ============================================================
    echo [ERROR] Push failed.
    echo ============================================================
    echo.
    echo Common solutions:
    echo 1. Make sure you're logged in to GitHub
    echo 2. Check if the repository exists on GitHub
    echo 3. Try authenticating with: gh auth login
    echo.
)

echo.
pause
