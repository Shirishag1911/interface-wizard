#!/bin/bash
# Interface Wizard - UI-Compatible Backend Startup Script
# Version: 4.0
# Usage: ./start_ui_backend.sh

echo "================================================================================"
echo "  Interface Wizard - UI-Compatible Backend v4.0"
echo "================================================================================"
echo ""

# Check if we're in the correct directory
if [ ! -f "main_ui_compatible.py" ]; then
    echo "❌ Error: main_ui_compatible.py not found"
    echo "   Please run this script from the actual-code directory"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $PYTHON_VERSION"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

# Install/check dependencies
echo ""
echo "Checking dependencies..."
pip install -q -r requirements.txt

# Check if Mirth is accessible
echo ""
echo "Checking Mirth Connect connectivity..."
nc -z localhost 6661 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Mirth Connect is accessible on port 6661"
else
    echo "⚠️  Mirth Connect not accessible on port 6661"
    echo "   Backend will start, but Mirth transmission will fail"
    echo "   Please ensure Mirth Connect is running"
fi

# Check if port 8000 is available
echo ""
echo "Checking if port 8000 is available..."
lsof -ti:8000 >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "⚠️  Port 8000 is already in use"
    echo ""
    read -p "Do you want to stop the existing process? (y/n): " choice
    if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
        echo "Stopping process on port 8000..."
        lsof -ti:8000 | xargs kill -9
        echo "✅ Process stopped"
    else
        echo "❌ Cannot start - port 8000 is busy"
        exit 1
    fi
fi

# Start the backend
echo ""
echo "================================================================================"
echo "  Starting Backend Server..."
echo "================================================================================"
echo ""
echo "📍 API Base URL: http://localhost:8000"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "📊 Interactive API: http://localhost:8000/redoc"
echo ""
echo "🔐 Default Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📝 Logs: interface_wizard_ui.log"
echo ""
echo "Press CTRL+C to stop the server"
echo "================================================================================"
echo ""

# Start with uvicorn
python3 main_ui_compatible.py

# Cleanup on exit
echo ""
echo "Server stopped"
