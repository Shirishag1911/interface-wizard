# Interface Wizard - Deployment Guide

## ✅ PRE-DEPLOYMENT VERIFICATION

All components have been tested and verified:
- ✅ Backend dependencies installed successfully
- ✅ Frontend dependencies installed successfully
- ✅ Backend starts without errors
- ✅ Frontend builds successfully
- ✅ API health check passes
- ✅ All code issues fixed

See [TESTING_REPORT.md](TESTING_REPORT.md) for full test results.

---

## 🚀 DEPLOYMENT STEPS

### Step 1: Ensure Prerequisites are Running

**Check MySQL:**
```cmd
# Start XAMPP Control Panel
# Click "Start" on MySQL module
# Verify it's running (green indicator)
```

**Check OpenEMR:**
```cmd
# Open browser to: http://localhost/openemr
# Login with: administrator / Admin@123456
# Verify access
```

**Check Mirth Connect:**
```cmd
# Start Mirth Connect Server (if not running)
# Open Mirth Administrator
# Login with: admin / Admin@123
```

### Step 2: Configure Mirth Connect Channel

**CRITICAL: You must create an MLLP listener channel**

1. Open Mirth Administrator
2. Click "Channels" → "New Channel"
3. Configure:
   ```
   Name: Interface Wizard HL7 Listener
   Source Connector Type: MLLP Listener
   Listener Settings:
     - Host: 0.0.0.0
     - Port: 6661

   Destination Connector Type: Database Writer
   (or Channel Writer to forward to OpenEMR)
   ```
4. Click "Deploy Channel"
5. Verify Status shows "Started"

### Step 3: Start Backend

**Option A: Using Script (Recommended)**
```cmd
# Double-click this file:
run-backend.bat

# You should see:
# "Application startup complete"
# "Uvicorn running on http://0.0.0.0:8000"
```

**Option B: Manual Start**
```cmd
cd c:\Users\Sirii\Work\Gen-AI\interface-wizard\backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verification:**
```cmd
# Open browser to: http://localhost:8000/api/v1/health
# Should show: {"status":"healthy","version":"1.0.0",...}
```

### Step 4: Start Frontend

**Option A: Using Script (Recommended)**
```cmd
# Double-click this file:
run-frontend.bat

# Browser will open automatically to http://localhost:3000
```

**Option B: Manual Start**
```cmd
cd c:\Users\Sirii\Work\Gen-AI\interface-wizard\frontend
npm start

# Wait for: "Compiled successfully!"
# Browser opens automatically
```

### Step 5: Verify Application is Running

**Check Backend:**
1. Open: http://localhost:8000
2. Should see: Application info with status "running"

**Check API Documentation:**
1. Open: http://localhost:8000/docs
2. Should see: Swagger UI with available endpoints

**Check Frontend:**
1. Open: http://localhost:3000
2. Should see: Interface Wizard chat interface
3. Status indicator (top right) should be GREEN
4. Welcome message should appear in chat

### Step 6: Test Basic Functionality

**Test 1: Simple Command**
```
In the chat interface, type:
"Create a test patient"

Expected Result:
- Message sent
- Processing indicator appears
- Response appears with patient details
- Status: Success
```

**Test 2: Bulk Command**
```
Type:
"Create 5 test patients with random demographics"

Expected Result:
- Bulk operation completes
- Summary shows: 5 succeeded, 0 failed
- Protocol: HL7V2
```

**Test 3: Query Command** (requires existing data in OpenEMR)
```
Type:
"Retrieve patient information for MRN 12345"

Expected Result:
- If patient exists: Shows patient details
- If not exists: "Patient not found" message
```

---

## 📋 TROUBLESHOOTING

### Issue: Backend won't start

**Error: "ModuleNotFoundError"**
```cmd
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

**Error: "Port 8000 already in use"**
```cmd
# Find and kill process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# Or change port in run command:
python -m uvicorn app.main:app --port 8001
```

### Issue: Frontend won't start

**Error: "npm install failed"**
```cmd
cd frontend
npm cache clean --force
npm install --legacy-peer-deps
```

**Error: "Port 3000 already in use"**
```cmd
# Kill process using port 3000
netstat -ano | findstr :3000
taskkill /PID <PID_NUMBER> /F
```

### Issue: "Cannot connect to backend"

**Check:**
1. Is backend running? (http://localhost:8000/api/v1/health)
2. Is frontend .env correct? (Should have: REACT_APP_API_URL=http://localhost:8000/api/v1)
3. Check browser console for CORS errors

**Fix:**
```cmd
# Restart backend
# Clear browser cache
# Hard refresh (Ctrl+Shift+R)
```

### Issue: "Timeout waiting for ACK"

**This means HL7 message was sent but no response from Mirth**

**Check:**
1. Is Mirth Connect running?
2. Is MLLP channel deployed and started?
3. Is channel listening on port 6661?
4. Check Mirth channel logs for errors

**Fix:**
```cmd
# In Mirth Administrator:
1. Go to Channels
2. Find "Interface Wizard HL7 Listener"
3. Click "Start" if stopped
4. Check "Channel Log" for errors
5. Verify port 6661 in Listener Settings
```

### Issue: "OpenAI API Error"

**Check:**
```
1. Is API key valid in backend/.env?
2. Is there internet connectivity?
3. Check OpenAI account status
```

---

## 🔍 VERIFICATION CHECKLIST

Before considering deployment complete, verify:

**Prerequisites:**
- [ ] XAMPP MySQL is running
- [ ] OpenEMR is accessible
- [ ] Mirth Connect is running
- [ ] MLLP channel created and deployed

**Backend:**
- [ ] Dependencies installed (no errors)
- [ ] Server starts successfully
- [ ] Health endpoint responds (200 OK)
- [ ] API docs accessible
- [ ] No errors in console/logs

**Frontend:**
- [ ] Dependencies installed (no errors)
- [ ] Application builds successfully
- [ ] App loads in browser
- [ ] Connection status is GREEN
- [ ] Welcome message appears

**Integration:**
- [ ] Test command succeeds
- [ ] HL7 message appears in Mirth logs
- [ ] ACK received successfully
- [ ] Data appears in OpenEMR (if configured)

---

## 📊 MONITORING

### Backend Logs
```
Location: backend\logs\interface-wizard.log

Monitor for:
- API requests
- HL7 messages sent
- ACK responses
- Errors and warnings
```

### Frontend Console
```
Open browser Developer Tools (F12) → Console

Monitor for:
- API calls
- WebSocket connections (if any)
- JavaScript errors
```

### Mirth Connect Logs
```
In Mirth Administrator:
1. Select channel
2. Click "View Messages"
3. Check for:
   - Received HL7 messages
   - ACK responses sent
   - Any transformation errors
```

---

## 🎯 TYPICAL USE CASES

### Use Case 1: Populate Test Data
```
1. "Create 100 test patients with random demographics"
2. Wait for completion (may take 30-60 seconds)
3. Verify in OpenEMR database
```

### Use Case 2: Test HL7 Interface
```
1. "Create a patient named John Doe, DOB 1990-01-15"
2. Check Mirth Connect for message
3. Verify ACK response
4. Check OpenEMR for new patient
```

### Use Case 3: Query Patient Data
```
1. "Retrieve patient information for MRN 12345"
2. System queries FHIR API
3. Displays patient demographics
```

---

## 🔐 SECURITY NOTES

**IMPORTANT:**
- This is configured for a TEST ENVIRONMENT only
- DO NOT use with real patient data
- DO NOT expose to the internet
- API has NO authentication (by design for testing)
- All communication is unencrypted (HTTP)

**For Production:**
- Implement authentication (JWT/OAuth)
- Enable HTTPS/TLS
- Use environment-specific credentials
- Implement rate limiting
- Add audit logging
- Database persistence instead of in-memory

---

## 📞 SUPPORT

### If You Encounter Issues:

1. **Check Logs:**
   - Backend: `backend\logs\interface-wizard.log`
   - Browser console (F12)
   - Mirth Connect channel logs

2. **Review Documentation:**
   - [QUICKSTART.md](QUICKSTART.md)
   - [INSTALLATION.md](INSTALLATION.md)
   - [USER_GUIDE.md](USER_GUIDE.md)
   - [TESTING_REPORT.md](TESTING_REPORT.md)

3. **Common Issues:**
   - All documented in TROUBLESHOOTING section above
   - Check that all prerequisites are running
   - Verify port availability

---

## ✅ SUCCESS CRITERIA

**You know deployment is successful when:**

1. ✅ Both terminals (backend + frontend) show no errors
2. ✅ http://localhost:3000 loads the chat interface
3. ✅ Status indicator is GREEN
4. ✅ Test command "Create a test patient" succeeds
5. ✅ Mirth Connect shows received HL7 message
6. ✅ ACK response is received
7. ✅ Operation shows "success" status

---

## 🎉 YOU'RE READY!

If all checks pass, Interface Wizard is successfully deployed and ready to use!

Try these commands to get started:
```
"Create 10 test patients"
"Create a patient named Alice Smith with allergy to penicillin"
"Retrieve patient MRN 12345"
```

Enjoy using Interface Wizard!

---

**Last Updated:** November 14, 2024
**Version:** 1.0.0
