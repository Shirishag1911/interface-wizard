# API Endpoint Mapping - Quick Reference

**Version:** 4.0
**Purpose:** Quick lookup table for UI-Backend endpoint mapping

---

## Complete Endpoint Mapping Table

| # | UI Endpoint | Method | New Backend File | Status | Notes |
|---|------------|--------|-----------------|--------|-------|
| 1 | `/auth/login` | POST | ✅ `main_ui_compatible.py:235` | Ready | Form data: username, password |
| 2 | `/auth/register` | POST | ✅ `main_ui_compatible.py:264` | Ready | JSON body: username, email, password |
| 3 | `/api/v1/command` | POST | ✅ `main_ui_compatible.py:299` | Ready | Handles both text & files |
| 4 | `/api/v1/preview` | POST | ✅ `main_ui_compatible.py:425` | Ready | File upload for preview |
| 5 | `/api/v1/confirm` | POST | ✅ `main_ui_compatible.py:516` | Ready | Executes previewed operation |
| 6 | `/api/v1/sessions` | GET | ✅ `main_ui_compatible.py:619` | Ready | List all sessions |
| 7 | `/api/v1/sessions` | POST | ✅ `main_ui_compatible.py:627` | Ready | Create new session |
| 8 | `/api/v1/sessions/{id}/messages` | GET | ✅ `main_ui_compatible.py:646` | Ready | Get session messages |
| 9 | `/api/v1/sessions/{id}` | DELETE | ✅ `main_ui_compatible.py:657` | Ready | Delete session |
| 10 | `/api/v1/messages` | POST | ✅ `main_ui_compatible.py:672` | Ready | Send message with file |
| 11 | `/api/v1/session/{id}` | GET | ✅ `main_ui_compatible.py:714` | Ready | Get session info |
| 12 | `/api/v1/operation/{id}` | GET | ✅ `main_ui_compatible.py:736` | Ready | Get operation details |
| 13 | `/api/v1/health` | GET | ✅ `main_ui_compatible.py:747` | Ready | Basic health check |
| 14 | `/api/v1/health/detailed` | GET | ✅ `main_ui_compatible.py:755` | Ready | Detailed health with Mirth status |

---

## Request/Response Format Cheat Sheet

### 1. Authentication

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Response
{
  "access_token": "token_...",
  "token_type": "bearer",
  "user": {"id": "...", "username": "admin", "email": "..."}
}
```

### 2. File Upload Preview

```bash
# Preview
curl -X POST http://localhost:8000/api/v1/preview \
  -F "file=@patients.csv"

# Response
{
  "preview_id": "uuid",
  "operation_type": "bulk_patient_registration",
  "total_records": 10,
  "preview_records": [{...}],
  "validation_warnings": [],
  "estimated_time_seconds": 1,
  "message": "Found 8 valid patients..."
}
```

### 3. Confirm Operation

```bash
# Confirm
curl -X POST http://localhost:8000/api/v1/confirm \
  -H "Content-Type: application/json" \
  -d '{"preview_id":"uuid","confirmed":true}'

# Response
{
  "operation_id": "operation_...",
  "status": "success",
  "message": "Processed 8 patients: 8 succeeded, 0 failed",
  "records_affected": 8,
  "records_succeeded": 8,
  "records_failed": 0
}
```

### 4. Command Processing

```bash
# Upload via command
curl -X POST http://localhost:8000/api/v1/command \
  -F "command=Upload patients" \
  -F "file=@patients.csv"

# Response
{
  "operation_id": "uuid",
  "status": "success",
  "message": "File uploaded successfully...",
  "data": {"preview_id": "uuid", "requires_confirmation": true}
}
```

### 5. Session Management

```bash
# Create session
curl -X POST http://localhost:8000/api/v1/sessions

# Get sessions
curl http://localhost:8000/api/v1/sessions

# Get messages
curl http://localhost:8000/api/v1/sessions/SESSION_ID/messages

# Delete session
curl -X DELETE http://localhost:8000/api/v1/sessions/SESSION_ID
```

### 6. Health Checks

```bash
# Basic health
curl http://localhost:8000/api/v1/health

# Detailed health
curl http://localhost:8000/api/v1/health/detailed
```

---

## UI Frontend Expected Flow

### Workflow 1: File Upload with Confirmation

```
UI Step 1: User selects CSV/Excel file
    ↓
    POST /api/v1/preview
    ↓
Backend: Parse, validate, return preview
    ↓
UI Step 2: User reviews preview, clicks "Confirm"
    ↓
    POST /api/v1/confirm {"preview_id":"...", "confirmed":true}
    ↓
Backend: Process patients, send to Mirth
    ↓
UI Step 3: Display results
```

### Workflow 2: Direct Command (No File)

```
UI Step 1: User types command "Create patient John Doe"
    ↓
    POST /api/v1/command {"command":"..."}
    ↓
Backend: Process command (NLP not fully implemented)
    ↓
UI Step 2: Display result
```

### Workflow 3: Session-Based Chat

```
UI Step 1: Create session
    ↓
    POST /api/v1/sessions
    ↓
UI Step 2: Send messages
    ↓
    POST /api/v1/messages {"content":"...", "session_id":"..."}
    ↓
UI Step 3: View history
    ↓
    GET /api/v1/sessions/SESSION_ID/messages
```

---

## Data Transformation Examples

### Transform 1: Patient Data

```python
# Internal Format (from main_with_fastapi.py)
{
  "index": 0,
  "uuid": "abc-123",
  "firstName": "John",
  "lastName": "Doe",
  "mrn": "MRN001",
  "dateOfBirth": "1980-05-15",
  "gender": "Male",
  "phone": "555-1234",
  "email": "john@example.com"
}

# ↓ Transforms to ↓

# UI Format (PatientPreview)
{
  "name": "John Doe",  # Combined firstName + lastName
  "mrn": "MRN001",
  "date_of_birth": "1980-05-15",  # Renamed field
  "gender": "Male",
  "phone": "555-1234",
  "email": "john@example.com",
  "address": null
}
```

### Transform 2: Upload Response

```python
# Internal Format
{
  "session_id": "uuid",
  "total_records": 10,
  "valid_records": 8,
  "invalid_records": 2,
  "patients": [...],
  "validation_errors": [...]
}

# ↓ Transforms to ↓

# UI Format (PreviewResponse)
{
  "preview_id": "uuid",  # Renamed from session_id
  "operation_type": "bulk_patient_registration",  # Added
  "total_records": 10,
  "preview_records": [...],  # Transformed patients
  "validation_warnings": [...],  # Flattened errors
  "estimated_time_seconds": 1,  # Calculated
  "message": "Found 8 valid patients out of 10 total records"  # Generated
}
```

### Transform 3: Confirm Response

```python
# Internal Format
{
  "upload_id": "upload_123",
  "status": "processing",
  "total_selected": 8,
  "stream_url": "/api/upload/upload_123/stream"
}

# ↓ Transforms to ↓

# UI Format (OperationResponse)
{
  "operation_id": "operation_123",  # Renamed
  "status": "success",  # Changed to final status
  "message": "Processed 8 patients: 8 succeeded, 0 failed",
  "records_affected": 8,
  "records_succeeded": 8,  # Added
  "records_failed": 0,  # Added
  "created_at": "2025-12-30T12:00:00",
  "completed_at": "2025-12-30T12:00:01"
}
```

---

## Comparison with v3.0 Backend

| Feature | v3.0 (`main_with_fastapi.py`) | v4.0 (`main_ui_compatible.py`) |
|---------|------------------------------|--------------------------------|
| **Upload Endpoint** | `/api/upload` | `/api/v1/preview` |
| **Confirm Endpoint** | `/api/upload/confirm` | `/api/v1/confirm` |
| **Results Endpoint** | `/api/upload/{id}/results` | `/api/v1/operation/{id}` |
| **SSE Streaming** | `/api/upload/{id}/stream` | ❌ Not needed by UI |
| **Authentication** | ❌ None | ✅ `/auth/login`, `/auth/register` |
| **Sessions** | ❌ None | ✅ `/api/v1/sessions/*` |
| **Commands** | ❌ None | ✅ `/api/v1/command` |
| **Messages** | ❌ None | ✅ `/api/v1/messages` |
| **Health** | `/health` | `/api/v1/health`, `/api/v1/health/detailed` |

---

## Testing Checklist

- [ ] Authentication works (login/register)
- [ ] File upload creates preview
- [ ] Preview shows correct patient count
- [ ] Confirm processes patients successfully
- [ ] HL7 messages sent to Mirth
- [ ] Patients inserted in OpenEMR
- [ ] Session creation works
- [ ] Messages can be sent/retrieved
- [ ] Health endpoints return correct status
- [ ] CORS allows UI requests
- [ ] All transformations working correctly

---

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Port 8000 in use | `lsof -ti:8000 \| xargs kill -9` |
| Import error | Run from `actual-code` directory |
| CORS error | Check `allow_origins` in line 123 |
| Preview expired | Upload file again |
| Mirth not connected | Check Mirth running on port 6661 |
| Auth token invalid | Use simplified token (demo only) |

---

## Quick Start Commands

```bash
# 1. Start backend
cd /Users/nagarajm/Work/SG/interface-wizard/actual-code
./start_ui_backend.sh

# 2. Test health
curl http://localhost:8000/api/v1/health

# 3. Test login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# 4. Start UI
cd /Users/nagarajm/Work/SG/interface-wizard/actual-code/application_interface_wizard
npm start
```

---

**Documentation Updated:** December 30, 2025
**Backend Version:** 4.0
**Status:** ✅ Ready for Production Testing
