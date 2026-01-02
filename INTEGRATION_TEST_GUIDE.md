# Integration Test Guide - UI + Backend

**Date:** January 2, 2026
**Status:** ✅ Ready for Testing
**Integration:** React UI + main_ui_compatible.py Backend

---

## 🎯 Overview

This guide will help you test the complete integrated system:
- **Frontend:** React UI at `/frontend-react`
- **Backend:** `main_ui_compatible.py` at `/actual-code`

**Changes Made for Integration:**
1. ✅ Updated `frontend-react/.env` to point to `http://localhost:8000`
2. ✅ Updated `frontend-react/src/services/api.ts` to use correct base URLs
3. ✅ Updated `frontend-react/src/services/auth.service.ts` to use environment variable
4. ✅ Backend already has all 14 UI-expected endpoints

---

## 🚀 Quick Start (Step-by-Step)

### Step 1: Start Backend Server

```bash
# Navigate to backend directory
cd /Users/nagarajm/Work/SG/interface-wizard/actual-code

# Option A: Use startup script (Linux/Mac)
./start_ui_backend.sh

# Option B: Use startup script (Windows)
start_ui_backend.bat

# Option C: Direct Python
python main_ui_compatible.py
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Verify Backend is Running:**
```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Expected response:
{
  "status": "healthy",
  "version": "4.0",
  "timestamp": "2026-01-02T...",
  "services": {
    "database": "not_configured",
    "mirth": "connected"
  }
}
```

---

### Step 2: Start Frontend UI

**Open a NEW terminal window** (keep backend running):

```bash
# Navigate to React frontend
cd /Users/nagarajm/Work/SG/interface-wizard/frontend-react

# Install dependencies (first time only)
npm install

# Start development server
npm start
```

**Expected Output:**
```
Compiled successfully!

You can now view interface-wizard in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

**Browser will automatically open at:** http://localhost:3000

---

### Step 3: Test Authentication

#### Test 1: Login with Default Credentials

1. **Open browser:** http://localhost:3000
2. **You should see:** Login page
3. **Enter credentials:**
   - Email: `admin`
   - Password: `admin123`
4. **Click:** "Login" button
5. **Expected:** Redirect to chat interface

**If login fails, check:**
- Backend console for error logs
- Browser DevTools Console (F12) for API errors
- Network tab to see if request reached `/auth/login`

#### Test 2: Register New User (Optional)

1. **Click:** "Register" link on login page
2. **Enter:**
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `test123`
3. **Click:** "Register" button
4. **Expected:** Redirect to chat interface

**Note:** User data is stored in-memory only (lost on server restart)

---

### Step 4: Test Chat Interface

#### Test 1: Create New Session

1. **Click:** "New Chat" button in sidebar
2. **Expected:** New empty chat session created
3. **Verify:** Session appears in sidebar with timestamp

#### Test 2: Send Text Message

1. **Type in chat input:** "Hello, what can you do?"
2. **Press:** Enter or click Send button
3. **Expected:** Message appears in chat
4. **Expected:** Backend processes and responds

**Backend will respond with:** Information about capabilities (this is handled by your backend logic)

#### Test 3: Upload CSV File

**Prepare test file:** Create `test_patients.csv`:
```csv
FirstName,LastName,DateOfBirth,Gender,Phone,Email
John,Doe,1980-01-15,Male,555-1234,john@example.com
Jane,Smith,1990-05-20,Female,555-5678,jane@example.com
```

**Steps:**
1. **Click:** Attachment icon (📎) in chat input
2. **Select:** `test_patients.csv`
3. **Expected:** File preview shows below input
4. **Type message:** "Upload these patients"
5. **Click:** Send
6. **Expected:** Confirmation dialog appears showing:
   - Preview ID
   - Total records: 2
   - Patient preview list (John Doe, Jane Smith)
   - Validation warnings (if any)
   - Estimated time

#### Test 4: Confirm Bulk Operation

1. **In confirmation dialog, click:** "Confirm" button
2. **Expected:** Dialog closes
3. **Expected:** Backend processes patients:
   - Maps columns using AI (Ollama/OpenAI)
   - Generates HL7 ADT^A04 messages
   - Sends to Mirth Connect
   - Returns success response
4. **Expected:** Success message in chat showing:
   - Operation ID
   - Records succeeded: 2
   - Records failed: 0

#### Test 5: Session Management

1. **Create multiple chat sessions** (click "New Chat" 3 times)
2. **Send messages in different sessions**
3. **Switch between sessions** by clicking in sidebar
4. **Expected:** Each session maintains its own message history
5. **Delete a session:**
   - Hover over session in sidebar
   - Click delete icon (🗑️)
   - Confirm deletion
   - **Expected:** Session removed from list

---

## 🧪 Verification Checklist

### Backend Verification

```bash
# Check backend logs
tail -f /Users/nagarajm/Work/SG/interface-wizard/actual-code/interface_wizard_ui.log

# Test all endpoints manually
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/health/detailed
curl -X POST http://localhost:8000/api/v1/sessions
curl http://localhost:8000/api/v1/sessions
```

### Frontend Verification

Open Browser DevTools (F12) and check:

1. **Console Tab:**
   - Should see: `API Request: POST /auth/login`
   - Should see: `API Response: 200 /auth/login`
   - No error messages

2. **Network Tab:**
   - Filter by "XHR" or "Fetch"
   - Should see requests to `localhost:8000`
   - Check request/response payloads
   - All should return 200 status

3. **Application Tab:**
   - Local Storage → `http://localhost:3000`
   - Should see: `access_token` and `current_user`

### Mirth Connect Verification (If Configured)

```bash
# Check Mirth is running
netstat -an | grep 6661

# Check Mirth channel
# Open Mirth Administrator UI
# Verify channel message count increased
```

### OpenEMR Database Verification (If Configured)

```sql
-- Check patients were inserted
SELECT pid, fname, lname, pubpid, DOB, sex, regdate
FROM openemr.patient_data
WHERE regdate >= CURDATE()
ORDER BY pid DESC
LIMIT 10;
```

---

## 🐛 Troubleshooting

### Issue 1: Backend Won't Start

**Error:** `Address already in use` or `Port 8000 already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
lsof -ti:8000 | xargs kill -9

# Or use different port
python main_ui_compatible.py --port 8001
```

**Then update frontend `.env`:**
```bash
REACT_APP_API_URL=http://localhost:8001
```

---

### Issue 2: Frontend Won't Start

**Error:** `Port 3000 already in use`

**Solution:**
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
PORT=3001 npm start
```

---

### Issue 3: Login Fails with 401 Unauthorized

**Check:**
1. Backend is running: `curl http://localhost:8000/api/v1/health`
2. Credentials are correct: `admin` / `admin123`
3. Backend logs for error details

**Test login manually:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -F "username=admin" \
  -F "password=admin123"
```

**Expected response:**
```json
{
  "access_token": "token_admin_...",
  "token_type": "bearer",
  "user": {
    "id": "user_1",
    "username": "admin",
    "email": "admin@example.com"
  }
}
```

---

### Issue 4: CORS Errors in Browser

**Error in console:** `Access to XMLHttpRequest has been blocked by CORS policy`

**Check:**
1. Backend CORS configuration in `main_ui_compatible.py:123`
2. Should allow `http://localhost:3000`

**Current configuration:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (development only)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**If issue persists:** Restart backend server

---

### Issue 5: File Upload Shows No Preview

**Check:**
1. File is valid CSV/Excel format
2. File has proper headers
3. Backend logs show column mapping attempt
4. Preview cache is working

**Test preview manually:**
```bash
curl -X POST http://localhost:8000/api/v1/preview \
  -F "file=@test_patients.csv"
```

**Expected response:**
```json
{
  "preview_id": "...",
  "operation_type": "bulk_patient_registration",
  "total_records": 2,
  "preview_records": [...],
  "validation_warnings": [],
  "estimated_time_seconds": 5
}
```

---

### Issue 6: Confirmation Fails with "Preview Not Found"

**Cause:** Backend restarted between preview and confirm

**Solution:**
1. Upload file again to create new preview
2. Confirm immediately
3. Don't restart backend during testing

**Note:** Preview data is stored in-memory only

---

### Issue 7: HL7 Messages Not Reaching Mirth

**Check:**
1. Mirth Connect is running
2. Channel is deployed and listening on port 6661
3. Backend can connect to Mirth

**Test Mirth connectivity:**
```bash
# Check if Mirth is listening
netstat -an | grep 6661

# Expected: LISTEN on port 6661
```

**Check backend Mirth config:**
```python
# In main_ui_compatible.py, check MIRTH settings
MIRTH_HOST = "localhost"
MIRTH_PORT = 6661
```

---

## 📊 Expected Data Flow

### Complete Upload Flow:

```
1. User selects CSV file in UI
   ↓
2. UI calls POST /api/v1/preview
   - Sends: FormData with file
   ↓
3. Backend (main_ui_compatible.py):
   - Parses CSV using pandas
   - Maps columns with LLM (map_columns_with_llm)
   - Validates all patients
   - Stores in preview_cache with preview_id
   - Returns: PreviewResponse with patient list
   ↓
4. UI displays ConfirmationDialog
   - Shows: preview_id, total_records, patient preview
   ↓
5. User clicks "Confirm"
   ↓
6. UI calls POST /api/v1/confirm
   - Sends: {preview_id, confirmed: true}
   ↓
7. Backend:
   - Retrieves cached preview data
   - Filters valid patients only
   - For each patient:
     * Generates HL7 ADT^A04 message
     * Sends to Mirth via MLLP (build_hl7_message_programmatically)
     * Tracks success/failure
   ↓
8. Backend returns OperationResponse:
   - operation_id
   - status: "success"
   - records_succeeded: 2
   - records_failed: 0
   ↓
9. UI displays success message
   ↓
10. Mirth receives HL7 messages
   ↓
11. Mirth inserts into OpenEMR database
```

---

## 🔍 API Endpoint Mapping Reference

| UI Calls | Backend Endpoint | File | Method |
|----------|-----------------|------|--------|
| `/auth/login` | `/auth/login` | main_ui_compatible.py:313 | POST |
| `/auth/register` | `/auth/register` | main_ui_compatible.py:343 | POST |
| `/api/v1/command` | `/api/v1/command` | main_ui_compatible.py:382 | POST |
| `/api/v1/preview` | `/api/v1/preview` | main_ui_compatible.py:515 | POST |
| `/api/v1/confirm` | `/api/v1/confirm` | main_ui_compatible.py:607 | POST |
| `/api/v1/sessions` | `/api/v1/sessions` | main_ui_compatible.py:693 | GET |
| `/api/v1/sessions` | `/api/v1/sessions` | main_ui_compatible.py:702 | POST |
| `/api/v1/sessions/{id}/messages` | `/api/v1/sessions/{id}/messages` | main_ui_compatible.py:722 | GET |
| `/api/v1/sessions/{id}` | `/api/v1/sessions/{id}` | main_ui_compatible.py:734 | DELETE |
| `/api/v1/messages` | `/api/v1/messages` | main_ui_compatible.py:751 | POST |
| `/api/v1/session/{id}` | `/api/v1/session/{id}` | main_ui_compatible.py:804 | GET |
| `/api/v1/operation/{id}` | `/api/v1/operation/{id}` | main_ui_compatible.py:826 | GET |
| `/api/v1/health` | `/api/v1/health` | main_ui_compatible.py:840 | GET |
| `/api/v1/health/detailed` | `/api/v1/health/detailed` | main_ui_compatible.py:849 | GET |

**All 14 endpoints implemented and mapped correctly!** ✅

---

## ✅ Success Criteria

After testing, you should have:

- ✅ Backend running on port 8000
- ✅ Frontend running on port 3000
- ✅ Successful login with admin/admin123
- ✅ New chat sessions created
- ✅ Text messages sent and received
- ✅ CSV file uploaded with preview dialog
- ✅ Bulk operation confirmed and executed
- ✅ HL7 messages sent to Mirth (if configured)
- ✅ Patients inserted in OpenEMR database (if configured)
- ✅ Session management working (create/delete/switch)
- ✅ No CORS errors in browser console
- ✅ No errors in backend logs

---

## 📝 Test Results Template

Use this template to document your test results:

```
# Test Session: [Date/Time]

## Environment
- Backend: http://localhost:8000 [Running: Yes/No]
- Frontend: http://localhost:3000 [Running: Yes/No]
- Mirth: Port 6661 [Connected: Yes/No]
- Database: OpenEMR [Connected: Yes/No]

## Authentication Tests
- [✅/❌] Login with admin/admin123
- [✅/❌] Register new user
- [✅/❌] Logout and re-login

## Chat Interface Tests
- [✅/❌] Create new session
- [✅/❌] Send text message
- [✅/❌] Switch between sessions
- [✅/❌] Delete session

## File Upload Tests
- [✅/❌] Upload CSV file
- [✅/❌] Preview dialog appears
- [✅/❌] Patient data displayed correctly
- [✅/❌] Confirm operation
- [✅/❌] Success message received

## Backend Integration Tests
- [✅/❌] HL7 messages generated
- [✅/❌] Messages sent to Mirth
- [✅/❌] Mirth received messages
- [✅/❌] Patients in OpenEMR database

## Issues Found
[List any issues encountered]

## Notes
[Additional observations]
```

---

## 🎉 Next Steps After Successful Testing

Once testing is complete and successful:

1. **Production Preparation:**
   - Upgrade authentication (proper JWT with secrets)
   - Add password hashing (bcrypt)
   - Replace in-memory storage with database
   - Configure production CORS origins
   - Set up proper logging with rotation
   - Add rate limiting

2. **Documentation:**
   - Document any issues found
   - Update user guides
   - Create deployment guide

3. **Deployment:**
   - Set up production environment
   - Configure environment variables
   - Set up reverse proxy (nginx)
   - Enable HTTPS/TLS
   - Set up monitoring

---

**Created:** January 2, 2026
**Version:** 1.0
**Status:** ✅ Ready for Testing
**Backend:** main_ui_compatible.py (Port 8000)
**Frontend:** frontend-react (Port 3000)
