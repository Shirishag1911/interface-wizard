# Interface Wizard - Quick Reference Guide

## System Components

| Component | What It Does | Port/Location |
|-----------|-------------|---------------|
| **Frontend (Angular)** | User interface for chat | http://localhost:4200 |
| **Frontend (React)** | Alternative UI | http://localhost:3000 |
| **Backend (FastAPI)** | API server, creates HL7 messages | http://localhost:8000 |
| **Mirth Connect** | Integration engine, processes HL7 | http://localhost:8443 |
| **OpenEMR** | Electronic health records system | http://localhost/openemr |
| **MySQL Database** | Stores patient data | localhost:3306 |

---

## Quick Start Commands

### Start Backend:
```bash
cd backend
./venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Start Angular Frontend:
```bash
cd frontend-angular
npm start
```

### Start React Frontend:
```bash
cd frontend-react
npm start
```

### Start Mirth Connect:
```bash
# Windows: Run Mirth Connect Administrator
# Then deploy the "Interface Wizard HL7 Listener" channel
```

---

## Message Flow (5 Steps)

```
1. USER → "Create patient John Doe" → Frontend

2. FRONTEND → HTTP POST → Backend API

3. BACKEND → Creates HL7 message → Sends via MLLP to Mirth

4. MIRTH → Extracts patient data → Inserts into database

5. OPENEMR → Patient appears in system
```

---

## Mirth Channel Configuration

### Source Connector:
```
Type: MLLP Listener
Port: 6661
Host: 0.0.0.0
```

### Source Transformer:
```javascript
// Extract from HL7
var firstName = msg['PID']['PID.5']['PID.5.2'];
var lastName = msg['PID']['PID.5']['PID.5.1']['PID.5.1.1'];

// Insert into database
INSERT INTO patient_data (pid, fname, lname, ...) VALUES (...)
```

### Destination:
```
Type: File Writer
Directory: C:/mirth/hl7_messages/
```

---

## Common Issues & Fixes

| Problem | Solution |
|---------|----------|
| **"Connection refused to localhost:6661"** | Start and deploy Mirth channel |
| **"Duplicate entry '0' for key 'pid'"** | Use `SELECT MAX(pid)+1` (already in code) |
| **CORS error in frontend** | Check backend/.env has CORS_ORIGINS with frontend port |
| **Patient not in database** | Check Mirth channel logs for errors |
| **Backend not starting** | Activate venv: `./venv/Scripts/activate` |

---

## Testing the System

### Test 1: Create Patient
```
User input: "Create a test patient named John Doe"

Expected result:
✓ Backend receives command
✓ HL7 message generated
✓ Sent to Mirth (port 6661)
✓ Mirth inserts into database
✓ Patient appears in OpenEMR
```

### Test 2: Check Database
```sql
-- Run in phpMyAdmin or MySQL
SELECT * FROM patient_data ORDER BY pid DESC LIMIT 10;
```

### Test 3: Check Mirth Logs
```
1. Open Mirth Connect Administrator
2. Click on channel
3. Click "View Messages" or "Server Log"
4. Look for "SUCCESS! Inserted 1 row(s)"
```

---

## Key Files

| File | Purpose |
|------|---------|
| `backend/app/services/hl7_service.py` | Creates HL7 messages |
| `backend/app/services/ai_service.py` | Processes user commands |
| `backend/.env` | Configuration (ports, database, API keys) |
| `Mirth Channel` | Processes HL7 and inserts to database |
| `frontend-angular/src/app/chat/` | Angular chat interface |

---

## Database Tables

### patient_data (Main Patient Table)
```sql
pid         -- Patient ID (NOT auto-increment!)
pubpid      -- Medical Record Number (MRN)
fname       -- First Name
lname       -- Last Name
date        -- Record date
regdate     -- Registration date
status      -- 'active' or 'inactive'
```

---

## HL7 Message Example

```
MSH|^~\&|InterfaceWizard|Facility|||20251117101530||ADT^A04|MSG001|P|2.5
PID|1||12345^^^MRN||Doe^John^M||19800101|M|||123 Main St^^Boston^MA^02101
```

**Breakdown:**
- `MSH` = Message Header
- `PID` = Patient Identification
- `ADT^A04` = Register Patient message type
- `Doe^John^M` = Last^First^Middle
- `19800101` = Date of Birth (Jan 1, 1980)
- `M` = Male

---

## Environment Variables (.env)

```bash
# Backend
APP_NAME=Interface Wizard
DB_HOST=localhost
DB_NAME=openemr
OPENEMR_BASE_URL=http://localhost/openemr

# Mirth
MLLP_HOST=localhost
MLLP_PORT=6661

# OpenAI
OPENAI_API_KEY=your-api-key-here

# CORS (add frontend ports)
CORS_ORIGINS=["http://localhost:3000", "http://localhost:4200"]
```

---

## Useful Commands

### Check if port is in use:
```bash
# Windows
netstat -ano | findstr :6661
netstat -ano | findstr :8000

# Kill process
taskkill /PID <process_id> /F
```

### Check Mirth logs:
```bash
# Mirth logs location (Windows)
C:\Program Files\Mirth Connect\logs\

# View in real-time
tail -f mirth.log
```

### Test MLLP connection:
```python
import socket

sock = socket.socket()
sock.connect(('localhost', 6661))
print("Connected to Mirth!")
sock.close()
```

---

## Architecture Diagram

```
┌─────────┐    HTTP     ┌─────────┐    MLLP    ┌───────┐    JDBC    ┌─────────┐
│Frontend │ ──────────> │ Backend │ ─────────> │ Mirth │ ─────────> │ OpenEMR │
│(Angular)│             │(FastAPI)│            │Connect│            │Database │
└─────────┘             └─────────┘            └───────┘            └─────────┘
   :4200                  :8000                  :6661               :3306
```

---

## Default Credentials

| System | Username | Password |
|--------|----------|----------|
| **Mirth Connect** | admin | admin |
| **OpenEMR** | administrator | Admin@123456 |
| **MySQL** | openemr | openemr |

---

## Next Steps

1. ✅ Create patient via chat interface
2. ✅ Verify in OpenEMR database (phpMyAdmin)
3. ⏳ Add diagnosis information (diabetes, cancer, etc.)
4. ⏳ Make patients appear in OpenEMR Messages dashboard
5. ⏳ Add patient search functionality

---

## Support

- **Documentation:** [docs/MIRTH_CONNECT_SETUP_GUIDE.md](MIRTH_CONNECT_SETUP_GUIDE.md)
- **Logs:** Check Mirth Connect logs and backend console
- **Database:** Use phpMyAdmin to inspect data

---

**Last Updated:** 2025-11-17
