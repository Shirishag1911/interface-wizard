# Interface Wizard - Quick Start Guide

## 🚀 Get Started in 5 Minutes

This guide will get Interface Wizard running quickly.

## Prerequisites Check

✅ XAMPP installed and MySQL running
✅ OpenEMR installed and accessible
✅ Mirth Connect installed and running
✅ Python 3.10+ installed
✅ Node.js 18+ installed

## Step 1: Install Backend (2 minutes)

```cmd
# Double-click this file:
setup-backend.bat

# Or manually:
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Step 2: Install Frontend (2 minutes)

```cmd
# Double-click this file:
setup-frontend.bat

# Or manually:
cd frontend
npm install
```

## Step 3: Configure Mirth Connect (1 minute)

1. Open Mirth Connect Administrator
2. Login: admin / Admin@123
3. Create new channel:
   - Name: "Interface Wizard Listener"
   - Source: MLLP Listener
   - Port: 6661
   - Destination: Choose your target (Database Writer or another system)
4. Click "Deploy"

## Step 4: Start the Application

### Terminal 1 - Start Backend:
```cmd
# Double-click:
run-backend.bat

# Or:
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Wait for: `Application startup complete`

### Terminal 2 - Start Frontend:
```cmd
# Double-click:
run-frontend.bat

# Or:
cd frontend
npm start
```

Browser will open automatically to http://localhost:3000

## Step 5: Test It!

Try these commands in the chat interface:

```
Create a test patient
```

```
Create 5 test patients with random demographics
```

```
Retrieve patient information for MRN 12345
```

## ✅ Verification Checklist

- [ ] Backend running at http://localhost:8000
- [ ] Frontend opened in browser at http://localhost:3000
- [ ] Connection status is GREEN (top right)
- [ ] Mirth Connect channel is STARTED
- [ ] Test command succeeded

## 🎯 Quick Reference

### URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

### Common Commands
```
# Patient Operations
Create a patient named John Doe
Create 50 test patients
Retrieve patient MRN 12345

# Lab Results
Create CBC results for patient 12345
Get latest lab results for patient 67890

# Admission/Discharge
Admit patient MRN 12345 to ICU
Discharge patient MRN 67890
```

### Ports Used
- Frontend: 3000
- Backend: 8000
- MySQL: 3306
- Mirth: 8443
- MLLP: 6661

## 🔧 Troubleshooting

### Backend won't start
```cmd
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend won't start
```cmd
cd frontend
npm install
```

### "Cannot connect to backend"
1. Check backend is running (port 8000)
2. Check `frontend/.env` has correct URL

### "Timeout waiting for ACK"
1. Ensure Mirth Connect is running
2. Check channel is deployed and started
3. Verify port 6661 in Mirth matches MLLP_PORT in backend/.env

## 📚 Next Steps

1. ✅ Application is running
2. 📖 Read [USER_GUIDE.md](USER_GUIDE.md) for detailed commands
3. 🏗️ Check [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
4. 🔍 Try example workflows from the User Guide

## 🆘 Need Help?

1. Check logs: `backend/logs/interface-wizard.log`
2. Review [INSTALLATION.md](INSTALLATION.md) for detailed setup
3. Check API docs: http://localhost:8000/docs
4. Review Mirth Connect channel logs

## 🎉 You're Ready!

Interface Wizard is now running. Start by typing natural language commands in the chat interface!

Example:
```
Create 10 test patients with allergies to penicillin
```

The system will interpret your command, generate appropriate HL7 messages, send them to OpenEMR via Mirth Connect, and show you the results!
