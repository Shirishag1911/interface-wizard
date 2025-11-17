# Interface Wizard - Installation Guide

## Prerequisites

Before installing Interface Wizard, ensure you have the following installed and running:

### Required Software
- **Python 3.10 or higher** - [Download](https://www.python.org/downloads/)
- **Node.js 18 or higher** - [Download](https://nodejs.org/)
- **XAMPP** - With MySQL running
- **OpenEMR** - Installed and configured
- **Mirth Connect** - Installed and running

### Services Status Check
Make sure these services are running:
- MySQL (via XAMPP)
- OpenEMR (accessible at http://localhost/openemr)
- Mirth Connect (accessible at http://localhost:8443)

## Installation Steps

### 1. Clone or Extract the Project

Extract the Interface Wizard files to your desired location, e.g., `C:\Users\Sirii\Work\Gen-AI\interface-wizard`

### 2. Backend Setup

#### Option A: Using the Setup Script (Recommended)
1. Double-click `setup-backend.bat`
2. Wait for the installation to complete

#### Option B: Manual Setup
1. Open Command Prompt
2. Navigate to the backend directory:
   ```cmd
   cd C:\Users\Sirii\Work\Gen-AI\interface-wizard\backend
   ```
3. Create a virtual environment:
   ```cmd
   python -m venv venv
   ```
4. Activate the virtual environment:
   ```cmd
   venv\Scripts\activate
   ```
5. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

### 3. Frontend Setup

#### Option A: Using the Setup Script (Recommended)
1. Double-click `setup-frontend.bat`
2. Wait for npm to install all dependencies

#### Option B: Manual Setup
1. Open Command Prompt
2. Navigate to the frontend directory:
   ```cmd
   cd C:\Users\Sirii\Work\Gen-AI\interface-wizard\frontend
   ```
3. Install dependencies:
   ```cmd
   npm install
   ```

### 4. Configuration

The `.env` file in the backend directory is already configured with your credentials. If you need to modify any settings:

**Backend Configuration** (`backend/.env`):
```env
# Database (OpenEMR)
DB_HOST=localhost
DB_PORT=3306
DB_NAME=openemr
DB_USER=openemr
DB_PASSWORD=openemr

# OpenEMR
OPENEMR_USERNAME=administrator
OPENEMR_PASSWORD=Admin@123456

# Mirth Connect
MIRTH_HOST=localhost
MIRTH_PORT=8443
MIRTH_USERNAME=admin
MIRTH_PASSWORD=Admin@123

# HL7 MLLP (Configure a channel in Mirth Connect)
MLLP_HOST=localhost
MLLP_PORT=6661

# OpenAI
OPENAI_API_KEY=your-openai-api-key-here
```

**Frontend Configuration** (`frontend/.env`):
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

### 5. Mirth Connect Channel Setup

You need to create an MLLP Listener channel in Mirth Connect:

1. Open Mirth Connect Administrator
2. Log in with credentials (admin / Admin@123)
3. Create a new channel:
   - Name: "Interface Wizard HL7 Listener"
   - Source Connector: MLLP Listener
   - Host: 0.0.0.0
   - Port: 6661
   - Destination: Database Writer or HL7 Sender (depending on your needs)
4. Deploy the channel

## Running the Application

### Option A: Using Run Scripts (Recommended)

1. **Start Backend:**
   - Double-click `run-backend.bat`
   - Wait for "Application startup complete" message
   - Backend will be available at http://localhost:8000

2. **Start Frontend:**
   - Double-click `run-frontend.bat`
   - Your browser will automatically open to http://localhost:3000

### Option B: Manual Start

**Terminal 1 - Backend:**
```cmd
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```cmd
cd frontend
npm start
```

## Verification

1. Open your browser to http://localhost:3000
2. You should see the Interface Wizard interface
3. Check the connection status indicator (should be green)
4. Try a test command: "Create a test patient"

## API Documentation

Once the backend is running, you can access:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/api/v1/health

## Troubleshooting

### Backend Issues

**"Module not found" errors:**
```cmd
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

**"Cannot connect to database":**
- Ensure MySQL is running in XAMPP
- Verify OpenEMR database credentials

**"Cannot connect to Mirth":**
- Ensure Mirth Connect is running
- Check Mirth credentials in `.env`

### Frontend Issues

**"npm install" fails:**
```cmd
cd frontend
npm cache clean --force
npm install
```

**Cannot connect to backend:**
- Ensure backend is running on port 8000
- Check `frontend/.env` configuration

### HL7 Communication Issues

**"Timeout waiting for ACK":**
- Ensure Mirth Connect channel is deployed and started
- Verify MLLP_PORT (6661) matches your Mirth channel
- Check firewall settings

**"Connection refused":**
- Verify Mirth Connect is running
- Check that the MLLP listener channel is active

## Default Ports

- Backend API: 8000
- Frontend: 3000
- MySQL: 3306
- Mirth Connect: 8443
- MLLP Listener: 6661 (configurable)

## Next Steps

After successful installation:
1. Read the [User Guide](USER_GUIDE.md)
2. Try example commands
3. Review the [Architecture Documentation](ARCHITECTURE.md)

## Support

For issues or questions:
1. Check the logs in `backend/logs/interface-wizard.log`
2. Review API documentation at http://localhost:8000/docs
3. Check Mirth Connect channel logs
