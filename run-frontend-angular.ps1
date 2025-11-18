Write-Host "========================================"
Write-Host "Starting Interface Wizard - Angular Frontend"
Write-Host "========================================"
Write-Host ""

Write-Host "Checking for Node.js installation..."
$nodeCheck = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodeCheck) {
    Write-Host "ERROR: Node.js is not installed!" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/"
    Write-Host "Recommended version: 18.x or higher"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Node.js found:" -ForegroundColor Green
node --version
npm --version
Write-Host ""

Write-Host "Navigating to Angular frontend directory..."
Set-Location frontend-angular
Write-Host ""

Write-Host "Checking if node_modules exists..."
if (-not (Test-Path "node_modules")) {
    Write-Host "node_modules not found. Installing dependencies..."
    npm install
} else {
    Write-Host "node_modules found. Updating dependencies..."
    npm install
}
Write-Host ""

Write-Host "Starting Angular development server..."
Write-Host "Server will be available at http://localhost:4200"
Write-Host ""
npm start
