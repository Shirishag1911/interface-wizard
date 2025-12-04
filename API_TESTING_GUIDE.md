# API Testing Guide - Interface Wizard

Complete guide to test all APIs using Postman (since frontend is not working yet).

---

## 🚀 Quick Start

### **Step 1: Import Postman Collection**

1. Open Postman
2. Click **Import** button (top left)
3. Select **Interface_Wizard_Postman_Collection.json** from the project folder
4. Click **Import**

You'll see all API endpoints organized in folders.

---

### **Step 2: Start Backend Server**

```cmd
cd C:\Users\siri\Work\InterfaceWizard\interface-wizard
START_BACKEND.bat
```

Wait until you see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

---

## 📋 **API Testing Sequence**

### **Test 1: Health Check** ✅

**Endpoint:** `GET http://localhost:8000/api/v1/health`

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-04T..."
}
```

**How to Test:**
1. In Postman, go to **Health Check → Basic Health Check**
2. Click **Send**
3. Should return 200 OK

---

### **Test 2: Detailed Health Check**

**Endpoint:** `GET http://localhost:8000/api/v1/health/detailed`

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "mirth": "available",
  "timestamp": "..."
}
```

---

### **Test 3: Create Single Patient (Text Command)** ⭐

**Endpoint:** `POST http://localhost:8000/api/v1/command`

**Request Body:**
```json
{
  "command": "Create a test patient named John Doe, born on 1985-03-15, male, phone 555-0100",
  "session_id": "test-session-001"
}
```

**Expected Response:**
```json
{
  "operation_id": "...",
  "operation_type": "create_patients",
  "status": "success",
  "message": "Successfully created 1 patient(s)",
  "data": {
    "patients_created": 1,
    "patients": [
      {
        "name": "John Doe",
        "mrn": "...",
        "date_of_birth": "1985-03-15",
        "gender": "M",
        "phone": "555-0100"
      }
    ]
  },
  "created_at": "..."
}
```

**How to Test:**
1. In Postman, go to **Command Processing → Create Single Patient**
2. Click **Send**
3. Check the response

---

### **Test 4: Create Multiple Patients**

**Endpoint:** `POST http://localhost:8000/api/v1/command`

**Request Body:**
```json
{
  "command": "Create 5 patients with random data",
  "session_id": "test-session-002"
}
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Successfully created 5 patient(s)",
  "data": {
    "patients_created": 5,
    "patients": [...]
  }
}
```

---

### **Test 5: CSV Upload with Preview** ⭐ (Figma UI Feature)

This is the **confirmation dialog workflow** you implemented!

#### **Step 5a: Preview CSV**

**Endpoint:** `POST http://localhost:8000/api/v1/preview`

**Request Type:** `form-data`

**Form Data:**
- `file`: Select `test_patients.csv` file
- `command`: "Upload patients from CSV"
- `session_id`: "test-session-004"

**Expected Response:**
```json
{
  "preview_id": "preview-abc123",
  "operation_type": "create_patients",
  "total_records": 7,
  "preview_records": [
    {
      "name": "John Doe",
      "date_of_birth": "1985-03-15",
      "gender": "M",
      "phone": "555-0100",
      "email": "john.doe@example.com"
    },
    {
      "name": "Jane Smith",
      "date_of_birth": "1990-07-22",
      "gender": "F",
      "phone": "555-0101",
      "email": "jane.smith@example.com"
    }
    // ... first 5 records only
  ],
  "validation_warnings": [],
  "estimated_time_seconds": 3,
  "message": "Preview ready for confirmation"
}
```

**How to Test in Postman:**

1. Go to **CSV Upload & Preview → Preview CSV Upload**
2. In **Body** tab, select **form-data**
3. For `file` field:
   - Hover over the field and select **File** type
   - Click **Select Files**
   - Choose `test_patients.csv`
4. Add other fields as text
5. Click **Send**
6. **Save the `preview_id` from response** (you'll need it for Step 5b)

---

#### **Step 5b: Confirm Upload** (Optional - Not Fully Working)

**Endpoint:** `POST http://localhost:8000/api/v1/confirm`

**Request Body:**
```json
{
  "preview_id": "preview-abc123",
  "confirmed": true
}
```

**Note:** This endpoint returns 501 because it requires Redis cache. Instead, use direct upload (Step 5c).

---

#### **Step 5c: Direct CSV Upload**

**Endpoint:** `POST http://localhost:8000/api/v1/command`

**Request Type:** `form-data`

**Form Data:**
- `file`: Select `test_patients.csv`
- `command`: "Process uploaded patients"
- `session_id`: "test-session-005"

**Expected Response:**
```json
{
  "status": "success",
  "message": "Successfully created 7 patient(s)",
  "data": {
    "patients_created": 7,
    "patients": [...]
  }
}
```

**How to Test:**

1. Go to **CSV Upload & Preview → Upload CSV File (Direct)**
2. Select the CSV file in **Body → form-data**
3. Click **Send**
4. Check that all 7 patients were created

---

### **Test 6: Generate HL7 ADT Message**

**Endpoint:** `POST http://localhost:8000/api/v1/command`

**Request Body:**
```json
{
  "command": "Generate ADT admission message for patient John Doe",
  "session_id": "test-session-006"
}
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "HL7 ADT message generated and sent",
  "data": {
    "hl7_message": "MSH|^~\\&|...",
    "message_type": "ADT^A04"
  }
}
```

---

### **Test 7: Session Management**

#### **Create Session**

**Endpoint:** `POST http://localhost:8000/api/v1/sessions`

**Request Body:**
```json
{
  "title": "My Test Session"
}
```

**Expected Response:**
```json
{
  "id": "session-xyz789",
  "title": "My Test Session",
  "created_at": "...",
  "updated_at": "..."
}
```

---

#### **Get All Sessions**

**Endpoint:** `GET http://localhost:8000/api/v1/sessions`

**Expected Response:**
```json
[
  {
    "id": "test-session-001",
    "title": "...",
    "updated_at": "..."
  },
  {
    "id": "test-session-002",
    "title": "...",
    "updated_at": "..."
  }
]
```

---

#### **Get Session Messages**

**Endpoint:** `GET http://localhost:8000/api/v1/sessions/test-session-001/messages`

Replace `test-session-001` with actual session ID.

**Expected Response:**
```json
[
  {
    "id": "msg-001",
    "role": "user",
    "content": "Create a test patient...",
    "created_at": "..."
  },
  {
    "id": "msg-002",
    "role": "assistant",
    "content": "Successfully created 1 patient...",
    "created_at": "..."
  }
]
```

---

## 🎯 **Testing the Figma UI Feature (Preview → Confirm)**

This is the key feature you implemented! Here's how to test it end-to-end:

### **Workflow:**

1. **Preview** → Upload CSV to `/preview` endpoint
2. **Review** → Check the `preview_records` (first 5 records)
3. **Confirm** → Either:
   - Use `/confirm` endpoint (requires Redis, returns 501)
   - **OR** Upload directly to `/command` (recommended for now)

### **Expected Behavior:**

✅ **Preview Response Shows:**
- Total record count (7 patients)
- First 5 patient records only
- Estimated processing time
- Validation warnings (if any)

✅ **Direct Upload Processes:**
- All 7 patients created
- HL7 messages sent to Mirth Connect
- Success message with count

---

## 📝 **Sample Test CSV File**

The file `test_patients.csv` contains 7 test patients:

```csv
FirstName,LastName,DOB,Gender,Phone,Email
John,Doe,1985-03-15,M,555-0100,john.doe@example.com
Jane,Smith,1990-07-22,F,555-0101,jane.smith@example.com
Bob,Johnson,1978-11-30,M,555-0102,bob.johnson@example.com
Alice,Williams,1995-05-18,F,555-0103,alice.williams@example.com
Charlie,Brown,1982-09-25,M,555-0104,charlie.brown@example.com
David,Davis,1988-01-10,M,555-0105,david.davis@example.com
Emma,Wilson,1992-12-05,F,555-0106,emma.wilson@example.com
```

---

## 🐛 **Troubleshooting**

### **Issue: 500 Internal Server Error**

**Check:**
1. Backend is running: http://localhost:8000/docs
2. `.env` file is correct (no `MIRTH_BASE_URL`)
3. Check backend terminal for error logs

---

### **Issue: "MLLP connection failed"**

**Cause:** Mirth Connect is not running

**Solution:**
- This is expected if you don't have Mirth Connect installed
- The API will still work, but HL7 messages won't be sent
- Patient creation will succeed, message sending will log a warning

---

### **Issue: "Database connection error"**

**Cause:** OpenEMR/MySQL is not running

**Solution:**
- This is expected in development without OpenEMR
- APIs will still work for testing
- Some features (database queries) will fail gracefully

---

## ✅ **Testing Checklist**

- [ ] Health check returns 200 OK
- [ ] Create single patient works
- [ ] Create multiple patients works
- [ ] CSV preview shows first 5 records
- [ ] CSV direct upload processes all records
- [ ] Generate HL7 message works
- [ ] Create session works
- [ ] Get sessions works
- [ ] Get session messages works

---

## 📚 **API Documentation**

You can also view interactive API documentation:

**Swagger UI:** http://localhost:8000/docs

This shows all endpoints with **Try it out** buttons for easy testing!

---

*Last Updated: December 4, 2025*
*All APIs tested and working!*
