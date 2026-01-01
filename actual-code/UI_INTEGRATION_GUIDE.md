# Interface Wizard UI Integration Guide

**Version:** 4.0
**Date:** December 30, 2025
**Purpose:** Complete guide for integrating the React UI with the new backend API

---

## Table of Contents

1. [Overview](#overview)
2. [What Changed](#what-changed)
3. [New Backend File](#new-backend-file)
4. [API Endpoint Mapping](#api-endpoint-mapping)
5. [Request/Response Transformations](#requestresponse-transformations)
6. [Quick Start](#quick-start)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)
9. [Migration from v3.0](#migration-from-v30)

---

## Overview

### Problem
The React UI frontend expects different API endpoints and response formats than what the existing backend (v3.0) provides.

### Solution
Created **`main_ui_compatible.py`** - a new backend file that:
- ✅ Implements all UI-expected endpoints
- ✅ Transforms data between UI format and existing backend logic
- ✅ Maintains backward compatibility with v3.0
- ✅ Requires **ZERO UI changes**

### Architecture

```
┌─────────────────────┐
│   React UI          │
│   (No changes!)     │
└──────────┬──────────┘
           │ HTTP Requests
           ▼
┌─────────────────────────────────────┐
│  main_ui_compatible.py (NEW!)       │
│  ┌───────────────────────────────┐  │
│  │ UI-Expected Endpoints         │  │
│  │ - /api/v1/command             │  │
│  │ - /api/v1/preview             │  │
│  │ - /api/v1/confirm             │  │
│  │ - /auth/login                 │  │
│  │ - /api/v1/sessions            │  │
│  └─────────────┬─────────────────┘  │
│                │                     │
│  ┌─────────────▼─────────────────┐  │
│  │ Transformation Layer          │  │
│  │ - Converts formats            │  │
│  │ - Wraps existing logic        │  │
│  └─────────────┬─────────────────┘  │
│                │                     │
│  ┌─────────────▼─────────────────┐  │
│  │ Existing Backend Logic        │  │
│  │ (from main_with_fastapi.py)   │  │
│  │ - CSV parsing                 │  │
│  │ - Column mapping (LLM)        │  │
│  │ - HL7 generation              │  │
│  │ - Mirth transmission          │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

---

## What Changed

### New File: `main_ui_compatible.py`

**Location:** `/Users/nagarajm/Work/SG/interface-wizard/actual-code/main_ui_compatible.py`

**Purpose:** Provides UI-compatible API endpoints while reusing existing backend logic.

**Key Features:**
1. All 14 endpoints the UI expects
2. Authentication system (simplified JWT)
3. Session management for chat-like interface
4. Command processing endpoint
5. Preview/Confirm workflow with UI-expected formats
6. Data transformation between UI and backend formats

### Existing File: `main_with_fastapi.py`

**Status:** **Unchanged** - Still works exactly as before

**Backward Compatibility:** All v3.0 endpoints (`/api/upload`, `/api/upload/confirm`, etc.) still work

---

## API Endpoint Mapping

### Complete Endpoint List

| UI Expects | New Backend Provides | Status |
|------------|---------------------|--------|
| `POST /auth/login` | ✅ Implemented | Ready |
| `POST /auth/register` | ✅ Implemented | Ready |
| `POST /api/v1/command` | ✅ Implemented | Ready |
| `POST /api/v1/preview` | ✅ Implemented | Ready |
| `POST /api/v1/confirm` | ✅ Implemented | Ready |
| `GET /api/v1/sessions` | ✅ Implemented | Ready |
| `POST /api/v1/sessions` | ✅ Implemented | Ready |
| `GET /api/v1/sessions/{id}/messages` | ✅ Implemented | Ready |
| `DELETE /api/v1/sessions/{id}` | ✅ Implemented | Ready |
| `POST /api/v1/messages` | ✅ Implemented | Ready |
| `GET /api/v1/session/{id}` | ✅ Implemented | Ready |
| `GET /api/v1/operation/{id}` | ✅ Implemented | Ready |
| `GET /api/v1/health` | ✅ Implemented | Ready |
| `GET /api/v1/health/detailed` | ✅ Implemented | Ready |

---

## Request/Response Transformations

### 1. Authentication

#### `POST /auth/login`

**UI Sends:**
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123
```

**Backend Returns:**
```json
{
  "access_token": "token_admin_1735559400",
  "token_type": "bearer",
  "user": {
    "id": "user_1",
    "username": "admin",
    "email": "admin@example.com"
  }
}
```

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

---

### 2. File Upload Preview

#### `POST /api/v1/preview`

**UI Sends:**
```http
POST /api/v1/preview
Content-Type: multipart/form-data

file: [CSV/Excel file]
command: "Upload patients"
session_id: "optional-session-id"
```

**What Happens Internally:**
1. File is parsed using existing CSV/Excel logic
2. Columns are mapped using LLM (OpenAI or fuzzy matching)
3. All patients are validated
4. Data is cached with a `preview_id`
5. Response is transformed to UI-expected format

**Backend Returns:**
```json
{
  "preview_id": "550e8400-e29b-41d4-a716-446655440000",
  "operation_type": "bulk_patient_registration",
  "total_records": 10,
  "preview_records": [
    {
      "name": "John Doe",
      "mrn": "MRN001",
      "date_of_birth": "1980-05-15",
      "gender": "Male",
      "phone": "555-1234",
      "email": "john@example.com",
      "address": "123 Main St"
    },
    {
      "name": "Jane Smith",
      "mrn": "MRN002",
      "date_of_birth": "1990-08-20",
      "gender": "Female",
      "phone": "555-5678",
      "email": "jane@example.com",
      "address": null
    }
  ],
  "validation_warnings": [
    "Row 2: Missing required field in field 'firstName'",
    "Detected typo in 'Pateint First Name' - mapped to firstName"
  ],
  "estimated_time_seconds": 1,
  "message": "Found 8 valid patients out of 10 total records"
}
```

**Data Transformation:**

```python
# Original backend format (from main_with_fastapi.py)
{
  "session_id": "uuid",
  "total_records": 10,
  "valid_records": 8,
  "patients": [
    {
      "index": 0,
      "uuid": "uuid",
      "firstName": "John",
      "lastName": "Doe",
      "mrn": "MRN001",
      ...
    }
  ]
}

# ↓ Transformed to ↓

# UI-expected format
{
  "preview_id": "uuid",
  "preview_records": [
    {
      "name": "John Doe",  # Combined firstName + lastName
      "mrn": "MRN001",
      ...
    }
  ]
}
```

---

### 3. Confirm Operation

#### `POST /api/v1/confirm`

**UI Sends:**
```json
{
  "preview_id": "550e8400-e29b-41d4-a716-446655440000",
  "confirmed": true
}
```

**What Happens Internally:**
1. Retrieves cached preview data using `preview_id`
2. Filters for valid patients only
3. Generates HL7 messages programmatically
4. Sends to Mirth Connect via MLLP
5. Tracks success/failure for each patient

**Backend Returns:**
```json
{
  "operation_id": "operation_1735559400_abc123",
  "status": "success",
  "message": "Processed 8 patients: 8 succeeded, 0 failed",
  "data": null,
  "errors": null,
  "warnings": null,
  "protocol_used": "hl7v2",
  "records_affected": 8,
  "records_succeeded": 8,
  "records_failed": 0,
  "created_at": "2025-12-30T12:30:00",
  "completed_at": "2025-12-30T12:30:01"
}
```

**Data Transformation:**

```python
# Original backend format
{
  "upload_id": "upload_123",
  "status": "processing",
  "total_selected": 8,
  "stream_url": "/api/upload/upload_123/stream"
}

# ↓ Transformed to ↓

# UI-expected format
{
  "operation_id": "operation_123",
  "status": "success",
  "records_affected": 8,
  "records_succeeded": 8,
  "records_failed": 0
}
```

---

### 4. Command Processing

#### `POST /api/v1/command`

**UI Sends (Text Command):**
```json
{
  "command": "Create patient John Doe",
  "session_id": "optional-session-id"
}
```

**UI Sends (File Upload):**
```http
POST /api/v1/command
Content-Type: multipart/form-data

command: "Upload patients"
file: [CSV/Excel file]
session_id: "optional-session-id"
```

**Backend Returns:**
```json
{
  "operation_id": "uuid",
  "status": "success",
  "message": "File uploaded successfully. Found 8 valid patients. Use /api/v1/confirm to process.",
  "data": {
    "preview_id": "uuid",
    "requires_confirmation": true
  },
  "records_affected": 10,
  "records_succeeded": 8,
  "records_failed": 2
}
```

**Note:** For file uploads, this endpoint automatically creates a preview and returns a `preview_id` for confirmation.

---

### 5. Session Management

#### `GET /api/v1/sessions`

**Backend Returns:**
```json
[
  {
    "id": "session_uuid_1",
    "title": "Session 1",
    "updated_at": "2025-12-30T12:00:00",
    "messages": []
  },
  {
    "id": "session_uuid_2",
    "title": "Session 2",
    "updated_at": "2025-12-30T13:00:00",
    "messages": []
  }
]
```

#### `POST /api/v1/sessions`

**Backend Returns:**
```json
{
  "id": "new_session_uuid",
  "title": "Session 3",
  "updated_at": "2025-12-30T14:00:00",
  "messages": []
}
```

#### `GET /api/v1/sessions/{id}/messages`

**Backend Returns:**
```json
[
  {
    "id": "msg_1",
    "role": "user",
    "content": "Upload patients.csv",
    "created_at": "2025-12-30T12:00:00"
  },
  {
    "id": "msg_2",
    "role": "assistant",
    "content": "Found 8 valid patients",
    "created_at": "2025-12-30T12:00:01"
  }
]
```

---

### 6. Health Checks

#### `GET /api/v1/health`

**Backend Returns:**
```json
{
  "status": "healthy",
  "version": "4.0",
  "timestamp": "2025-12-30T12:00:00"
}
```

#### `GET /api/v1/health/detailed`

**Backend Returns:**
```json
{
  "status": "healthy",
  "version": "4.0",
  "timestamp": "2025-12-30T12:00:00",
  "services": {
    "mirth_connect": {
      "status": "connected",
      "host": "localhost",
      "port": 6661
    },
    "sessions": {
      "active_count": 2
    },
    "operations": {
      "total_count": 5
    }
  }
}
```

---

## Quick Start

### Step 1: Install Dependencies

```bash
cd /Users/nagarajm/Work/SG/interface-wizard/actual-code

# Dependencies already installed from requirements.txt
# No additional packages needed!
```

### Step 2: Start the New Backend

**Option A: Direct Python**
```bash
python main_ui_compatible.py
```

**Option B: Using uvicorn**
```bash
uvicorn main_ui_compatible:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
================================================================================
Starting Interface Wizard UI-Compatible API v4.0
================================================================================
API Documentation: http://localhost:8000/docs
Base URL: http://localhost:8000
Mirth Connect: localhost:6661
================================================================================
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 3: Verify Backend is Running

```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Expected response:
# {"status":"healthy","version":"4.0","timestamp":"2025-12-30T12:00:00"}
```

### Step 4: Start the React UI

```bash
cd /Users/nagarajm/Work/SG/interface-wizard/actual-code/application_interface_wizard

# Install dependencies (if not already done)
npm install

# Start React app
npm start
```

**UI will open at:** http://localhost:3000

### Step 5: Test End-to-End

1. **Login to UI**
   - Username: `admin`
   - Password: `admin123`

2. **Upload a CSV/Excel file**
   - UI will call `/api/v1/preview`
   - You'll see a preview dialog

3. **Confirm Upload**
   - UI will call `/api/v1/confirm`
   - Patients will be processed

4. **Check Results**
   - Verify in Mirth Connect
   - Query OpenEMR database

---

## Testing

### Test 1: Authentication

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Expected response:
{
  "access_token": "token_admin_1735559400",
  "token_type": "bearer",
  "user": {
    "id": "user_1",
    "username": "admin",
    "email": "admin@example.com"
  }
}
```

### Test 2: Preview Upload

```bash
# Upload CSV for preview
curl -X POST http://localhost:8000/api/v1/preview \
  -F "file=@Patient_Records.xlsx"

# Save preview_id from response for next step
```

### Test 3: Confirm and Process

```bash
# Confirm (replace PREVIEW_ID with actual ID from step 2)
curl -X POST http://localhost:8000/api/v1/confirm \
  -H "Content-Type: application/json" \
  -d '{
    "preview_id": "PREVIEW_ID",
    "confirmed": true
  }'
```

### Test 4: Session Management

```bash
# Create session
curl -X POST http://localhost:8000/api/v1/sessions

# Get all sessions
curl http://localhost:8000/api/v1/sessions

# Get session messages (replace SESSION_ID)
curl http://localhost:8000/api/v1/sessions/SESSION_ID/messages
```

### Test 5: Command Processing

```bash
# Upload file via command endpoint
curl -X POST http://localhost:8000/api/v1/command \
  -F "command=Upload patients" \
  -F "file=@patients.csv"
```

---

## Troubleshooting

### Issue 1: "Module 'main_with_fastapi' not found"

**Cause:** New backend can't import from existing backend file.

**Solution:**
```bash
# Make sure you're in the correct directory
cd /Users/nagarajm/Work/SG/interface-wizard/actual-code

# Run from this directory
python main_ui_compatible.py
```

### Issue 2: "Address already in use (port 8000)"

**Cause:** Another process is using port 8000.

**Solution:**
```bash
# Option 1: Stop existing process
lsof -ti:8000 | xargs kill -9

# Option 2: Use different port
uvicorn main_ui_compatible:app --port 8001
```

Then update UI to use `http://localhost:8001`.

### Issue 3: CORS Errors in UI

**Cause:** CORS middleware not allowing UI origin.

**Solution:** Already configured to allow all origins (`allow_origins=["*"]`). For production, update to specific origin:

```python
# In main_ui_compatible.py, line 123
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 4: "Preview not found or expired"

**Cause:** Preview data is stored in memory and cleared on server restart.

**Solution:** Upload file again to create new preview.

### Issue 5: Authentication Token Issues

**Note:** Current implementation uses simplified JWT (for demo purposes).

**For Production:** Replace with proper JWT implementation:

```bash
# Install python-jose
pip install python-jose[cryptography]

# Then update authentication logic in main_ui_compatible.py
```

---

## Migration from v3.0

### Can I Use Both Backends?

**Yes!** Both can run simultaneously on different ports:

```bash
# Terminal 1: v3.0 backend (original)
python main_with_fastapi.py --api  # Port 8000

# Terminal 2: v4.0 backend (UI-compatible)
uvicorn main_ui_compatible:app --port 8001  # Port 8001
```

### Endpoint Comparison

| Feature | v3.0 Backend | v4.0 Backend |
|---------|-------------|-------------|
| **CSV Upload** | `/api/upload` | `/api/v1/preview` |
| **Confirm** | `/api/upload/confirm` | `/api/v1/confirm` |
| **Results** | `/api/upload/{id}/results` | `/api/v1/operation/{id}` |
| **SSE Stream** | `/api/upload/{id}/stream` | ❌ Not needed by UI |
| **Authentication** | ❌ None | ✅ `/auth/login` |
| **Sessions** | ❌ None | ✅ `/api/v1/sessions` |
| **Commands** | ❌ None | ✅ `/api/v1/command` |

### Should I Replace v3.0?

**Recommendation:**
- **For React UI**: Use v4.0 (`main_ui_compatible.py`)
- **For Direct API Access**: Continue using v3.0 (`main_with_fastapi.py`)
- **For Testing**: Both work independently

---

## Production Considerations

### Security

**Current State:** Demo/Development only

**Required for Production:**

1. **Replace Simplified JWT**
   ```bash
   pip install python-jose[cryptography] passlib[bcrypt]
   ```

2. **Hash Passwords**
   ```python
   from passlib.context import CryptContext
   pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
   ```

3. **Use Environment Variables**
   ```bash
   export SECRET_KEY="your-super-secret-key-here"
   export OPENAI_API_KEY="your-openai-key"
   ```

4. **Enable HTTPS**

5. **Use Persistent Storage**
   - Replace in-memory dicts with Redis/PostgreSQL
   - Session data
   - Preview cache
   - Operation results

### Performance

**Current Limitations:**
- In-memory storage (data lost on restart)
- No rate limiting
- No caching layer
- Synchronous file processing

**Improvements for Production:**
- Add Redis for caching
- Use background workers (Celery)
- Implement request rate limiting
- Add database for persistence

---

## Summary

✅ **What You Got:**
- New backend file (`main_ui_compatible.py`) with all UI-expected endpoints
- Zero changes needed to React UI
- Backward compatibility with v3.0
- Complete request/response transformations
- Session management
- Authentication system
- Comprehensive documentation

✅ **What Works:**
- File upload preview/confirm workflow
- Command processing
- Session/message tracking
- Health monitoring
- All existing CSV/Excel processing logic
- LLM column mapping
- HL7 message generation
- Mirth transmission

✅ **Next Steps:**
1. Start new backend: `python main_ui_compatible.py`
2. Start React UI: `npm start`
3. Test login with admin/admin123
4. Upload a CSV/Excel file
5. Verify in Mirth and OpenEMR

---

**Questions or Issues?**
Check the `/docs` endpoint at http://localhost:8000/docs for interactive API documentation.
