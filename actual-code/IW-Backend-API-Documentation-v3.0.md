# Interface Wizard Backend API Documentation

**Version:** 3.0
**Last Updated:** December 29, 2025
**Backend Framework:** FastAPI 0.104+
**Base URL:** `http://localhost:8000`

---

## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Technology Stack](#technology-stack)
4. [System Architecture](#system-architecture)
5. [Quick Start](#quick-start)
6. [API Endpoints](#api-endpoints)
7. [Data Models](#data-models)
8. [CSV File Format](#csv-file-format)
9. [Code Examples](#code-examples)
10. [Error Handling](#error-handling)
11. [Testing Guide](#testing-guide)
12. [Troubleshooting](#troubleshooting)

---

## Overview

**Interface Wizard** is a healthcare integration platform that converts patient data from CSV/Excel files into HL7 v2.5 messages and transmits them to Electronic Health Record (EHR) systems via Mirth Connect using the MLLP protocol.

### Core Purpose
- **Bulk Patient Registration**: Process multiple patient records from CSV/Excel files
- **HL7 Message Generation**: Create standards-compliant ADT^A01 messages
- **Real-Time Processing**: Monitor upload progress via Server-Sent Events (SSE)
- **Data Validation**: 3-tier validation system ensures data quality
- **Preview & Confirmation**: Review parsed data before processing

### Use Cases
- Healthcare system migrations
- Bulk patient data imports
- Integration testing
- Training and demonstrations

---

## Key Features

### 1. **Two-Phase Upload Workflow**
```
Step 1: Upload & Preview
├─ Parse CSV/Excel file
├─ Validate all records
├─ Generate unique UUIDs
└─ Return preview data

Step 2: Confirm & Process
├─ User selects patients
├─ Generate HL7 messages
├─ Send to Mirth Connect
└─ Stream real-time progress
```

### 2. **AI-Powered HL7 Generation**
- **Primary**: OpenAI GPT-4o-mini for intelligent field extraction
- **Fallback**: Rule-based generator when AI unavailable
- **Custom Segments**: ZPI segment with UUID tracking

### 3. **Flexible File Support**
- CSV (.csv)
- Excel (.xlsx, .xls)
- Case-insensitive column mapping
- Multiple date formats supported

### 4. **Real-Time Progress Tracking**
- Server-Sent Events (SSE) for live updates
- Step-by-step progress indicators
- Processing status and error reporting

### 5. **Data Validation**
- **Tier 1 (Critical)**: MRN, First Name, Last Name, DOB, Gender
- **Tier 2 (Important)**: Phone, Email, Address
- **Tier 3 (Optional)**: Race, Ethnicity, Language, SSN

### 6. **CORS Support**
- Pre-configured for React (port 3000)
- Pre-configured for Angular (port 4200)
- Pre-configured for Vite (port 5173)
- Development-friendly wildcard support

---

## Technology Stack

### Backend Components

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | 0.104+ | REST API server |
| **Language** | Python | 3.9+ | Backend implementation |
| **HL7 Library** | python-hl7 | 0.4.5 | HL7 message parsing |
| **AI Engine** | OpenAI API | GPT-4o-mini | Intelligent data extraction |
| **Data Processing** | pandas | 2.0+ | CSV/Excel parsing |
| **Async Runtime** | asyncio | Built-in | Background processing |
| **ASGI Server** | uvicorn | 0.27+ | Production server |

### Integration Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Mirth Connect** | v4.x | HL7 message routing and transformation |
| **MLLP Protocol** | TCP Socket | Healthcare message transport |
| **OpenEMR** | v7.x | Target EHR system |
| **MySQL** | 8.0+ | Patient data storage |

---

## System Architecture

### High-Level Data Flow

```
┌─────────────────────┐
│  Frontend (React)   │
│  Port: 3000         │
└──────────┬──────────┘
           │ HTTP REST API + SSE
           ▼
┌─────────────────────────────────────────┐
│   FastAPI Backend (Port 8000)           │
│  ┌───────────────────────────────────┐  │
│  │ CORS Middleware                   │  │
│  ├───────────────────────────────────┤  │
│  │ API Endpoints                     │  │
│  │  • POST /api/upload               │  │
│  │  • POST /api/upload/confirm       │  │
│  │  • GET  /api/upload/{id}/stream   │  │
│  │  • GET  /api/upload/{id}/results  │  │
│  │  • GET  /api/dashboard/stats      │  │
│  ├───────────────────────────────────┤  │
│  │ Business Logic                    │  │
│  │  • CSV Parser                     │  │
│  │  • Data Validator (3-Tier)        │  │
│  │  • HL7 Generator (AI + Fallback)  │  │
│  │  • Session Manager                │  │
│  ├───────────────────────────────────┤  │
│  │ In-Memory Storage                 │  │
│  │  • upload_sessions{}              │  │
│  │  • dashboard_stats{}              │  │
│  └───────────────────────────────────┘  │
└────────┬─────────────────┬──────────────┘
         │                 │
         │ MLLP (6661)    │ OpenAI API
         ▼                 ▼
┌──────────────────┐  ┌─────────────┐
│ Mirth Connect    │  │  OpenAI     │
│  • MLLP Listener │  │  GPT-4o-mini│
│  • Transformer   │  └─────────────┘
│  • Router        │
└────────┬─────────┘
         │ SQL INSERT
         ▼
┌──────────────────┐
│ MySQL Database   │
│ (OpenEMR)        │
│  patient_data    │
└──────────────────┘
```

### Component Responsibilities

#### Frontend
- File upload interface
- Preview table display
- Patient selection UI
- Real-time progress monitoring
- Results visualization

#### Backend API
- File parsing and validation
- Session management (1-hour expiration)
- HL7 message generation
- MLLP transmission
- SSE streaming

#### Mirth Connect
- MLLP protocol handling
- HL7 message transformation
- Database insertion
- ACK generation

#### OpenEMR Database
- Patient data storage
- Medical record management

---

## Quick Start

### Prerequisites

1. **Python 3.9+** installed
2. **Mirth Connect** running on port 6661
3. **OpenAI API Key** (optional, fallback available)
4. **MySQL/OpenEMR** database

### Installation

```bash
# Navigate to project directory
cd interface-wizard/actual-code

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install fastapi uvicorn pandas openpyxl hl7 openai python-multipart

# Configure OpenAI API Key (optional)
# Edit main_with_fastapi.py line 46
OPENAI_API_KEY = "sk-your-actual-key-here"

# Configure Mirth Connect (if different)
# Edit lines 47-48
MIRTH_HOST = "localhost"
MIRTH_PORT = 6661
```

### Running the Server

```bash
# Start FastAPI server
python main_with_fastapi.py --api

# Server will start on http://localhost:8000
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### Verify CORS Configuration

```javascript
// From frontend (browser console)
fetch('http://localhost:8000/api/dashboard/stats')
  .then(response => response.json())
  .then(data => console.log(data));
// Should work without CORS errors
```

---

## API Endpoints

### Endpoint Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/upload` | Upload file and get preview data |
| POST | `/api/upload/confirm` | Process selected patients |
| GET | `/api/upload/{upload_id}/stream` | Real-time progress (SSE) |
| GET | `/api/upload/{upload_id}/results` | Get final results |
| GET | `/api/dashboard/stats` | Dashboard statistics |
| GET | `/api/dashboard/system-status` | System health check |
| POST | `/api/upload-legacy` | Direct upload without preview |
| GET | `/health` | Basic health check |

---

### 1. Upload File and Get Preview

#### `POST /api/upload`

**Description**: Upload CSV/Excel file, parse all records, validate data, and return preview with all patient records.

**Request**:
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@patients.csv" \
  -F "trigger_event=ADT-A01"
```

**Request Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file` | File | Yes | - | CSV or Excel file (.csv, .xlsx, .xls) |
| `trigger_event` | string | No | ADT-A01 | HL7 trigger event type |
| `use_llm_mapping` | boolean | No | true | Use LLM for intelligent column mapping |

**Response** (200 OK):
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "file_name": "patients.csv",
  "file_type": "csv",
  "total_records": 10,
  "valid_records": 8,
  "invalid_records": 2,
  "patients": [
    {
      "index": 0,
      "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "mrn": "MRN001",
      "firstName": "John",
      "lastName": "Doe",
      "dateOfBirth": "1980-05-15",
      "gender": "Male",
      "phone": "555-1234",
      "email": "john.doe@example.com",
      "address": "123 Main St, City, State 12345",
      "city": "City",
      "state": "State",
      "zip": "12345",
      "validation_status": "valid",
      "validation_messages": []
    },
    {
      "index": 1,
      "uuid": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "mrn": "MRN002",
      "firstName": "",
      "lastName": "Smith",
      "dateOfBirth": "1990-08-20",
      "gender": "Female",
      "phone": null,
      "email": null,
      "address": null,
      "city": null,
      "state": null,
      "zip": null,
      "validation_status": "invalid",
      "validation_messages": [
        "Missing required field: firstName (Tier 1 - Critical)"
      ]
    }
  ],
  "validation_errors": [
    {
      "row": 1,
      "field": "firstName",
      "error": "Missing required field",
      "value": null,
      "severity": "error"
    }
  ],
  "column_mapping": {
    "MRN": "mrn",
    "FirstName": "firstName",
    "LastName": "lastName",
    "DOB": "dateOfBirth",
    "Gender": "gender"
  },
  "expires_at": "2025-12-29T12:30:00Z",
  "timestamp": "2025-12-29T11:30:00Z"
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string (UUID) | Unique session identifier, use for confirmation |
| `file_name` | string | Original filename |
| `file_type` | string | "csv" or "excel" |
| `total_records` | integer | Total number of records parsed |
| `valid_records` | integer | Number of valid patient records |
| `invalid_records` | integer | Number of invalid records |
| `patients` | array | All patient records with validation status |
| `validation_errors` | array | List of validation errors |
| `column_mapping` | object | CSV columns to field mapping |
| `expires_at` | string | Session expiration time (1 hour) |
| `timestamp` | string | Upload timestamp (ISO 8601) |

**Status Codes**:
- `200 OK`: File processed successfully
- `400 Bad Request`: Invalid file format or no file provided
- `500 Internal Server Error`: Processing error

**Code Example (JavaScript)**:

```javascript
// Upload file and get preview
async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('trigger_event', 'ADT-A01');

  const response = await fetch('http://localhost:8000/api/upload', {
    method: 'POST',
    body: formData
  });

  const data = await response.json();

  console.log(`Session ID: ${data.session_id}`);
  console.log(`Total: ${data.total_records}, Valid: ${data.valid_records}`);

  // Display patients in table
  data.patients.forEach(patient => {
    console.log(`${patient.firstName} ${patient.lastName} - ${patient.validation_status}`);
  });

  return data.session_id;
}
```

**Code Example (Python)**:

```python
import requests

# Upload file
with open('patients.csv', 'rb') as f:
    files = {'file': f}
    data = {'trigger_event': 'ADT-A01'}

    response = requests.post(
        'http://localhost:8000/api/upload',
        files=files,
        data=data
    )

preview_data = response.json()
session_id = preview_data['session_id']

print(f"Session ID: {session_id}")
print(f"Valid records: {preview_data['valid_records']}")
print(f"Invalid records: {preview_data['invalid_records']}")

# Show all patients
for patient in preview_data['patients']:
    print(f"{patient['firstName']} {patient['lastName']} - {patient['validation_status']}")
```

---

### 2. Confirm and Process Selected Patients

#### `POST /api/upload/confirm`

**Description**: Confirm patient selection and start processing. Generates HL7 messages and sends to Mirth Connect.

**Request**:
```bash
curl -X POST http://localhost:8000/api/upload/confirm \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "selected_indices": [0, 2, 5],
    "send_to_mirth": true
  }'
```

**Request Body**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "selected_indices": [],
  "send_to_mirth": true
}
```

**Request Fields**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `session_id` | string (UUID) | Yes | - | Session ID from upload response |
| `selected_indices` | array[int] | No | [] | Patient indices to process (empty = all valid) |
| `send_to_mirth` | boolean | No | true | Send to Mirth Connect or dry-run |

**Response** (200 OK):
```json
{
  "upload_id": "upload_1735470600_abc123",
  "status": "processing",
  "total_selected": 3,
  "message": "Processing 3 patient(s)",
  "stream_url": "/api/upload/upload_1735470600_abc123/stream"
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `upload_id` | string | Unique processing job ID |
| `status` | string | Always "processing" initially |
| `total_selected` | integer | Number of patients being processed |
| `message` | string | Human-readable status message |
| `stream_url` | string | SSE endpoint for real-time progress |

**Status Codes**:
- `200 OK`: Processing started successfully
- `400 Bad Request`: Invalid session_id or no patients selected
- `404 Not Found`: Session not found or expired
- `500 Internal Server Error`: Processing error

**Code Example (JavaScript)**:

```javascript
// Confirm and process selected patients
async function confirmUpload(sessionId, selectedIndices = []) {
  const response = await fetch('http://localhost:8000/api/upload/confirm', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      session_id: sessionId,
      selected_indices: selectedIndices,  // Empty = all valid patients
      send_to_mirth: true
    })
  });

  const data = await response.json();

  console.log(`Upload ID: ${data.upload_id}`);
  console.log(`Processing ${data.total_selected} patients`);

  // Connect to SSE stream for real-time updates
  monitorProgress(data.upload_id);

  return data.upload_id;
}
```

**Code Example (Python)**:

```python
import requests

# Confirm upload and process selected patients
confirm_data = {
    'session_id': session_id,
    'selected_indices': [0, 1, 2],  # Process first 3 patients
    'send_to_mirth': True
}

response = requests.post(
    'http://localhost:8000/api/upload/confirm',
    json=confirm_data
)

result = response.json()
upload_id = result['upload_id']

print(f"Upload ID: {upload_id}")
print(f"Processing {result['total_selected']} patients")
print(f"Stream URL: {result['stream_url']}")
```

---

### 3. Monitor Real-Time Progress (SSE)

#### `GET /api/upload/{upload_id}/stream`

**Description**: Stream real-time processing progress via Server-Sent Events (SSE).

**Request**:
```javascript
const eventSource = new EventSource(
  'http://localhost:8000/api/upload/upload_1735470600_abc123/stream'
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Step ${data.step}: ${data.message} (${data.progress}%)`);

  if (data.status === 'completed' || data.status === 'failed') {
    eventSource.close();
  }
};

eventSource.onerror = (error) => {
  console.error('SSE error:', error);
  eventSource.close();
};
```

**Response Stream**:
```
data: {"step": 1, "message": "Initializing processing", "progress": 0, "status": "processing"}

data: {"step": 2, "message": "Generating HL7 messages (1/3)", "progress": 20, "status": "processing"}

data: {"step": 3, "message": "Generating HL7 messages (2/3)", "progress": 40, "status": "processing"}

data: {"step": 4, "message": "Sending to Mirth (1/3)", "progress": 60, "status": "processing"}

data: {"step": 5, "message": "Processing ACKs (2/3)", "progress": 80, "status": "processing"}

data: {"step": 6, "message": "Complete: 3 processed, 3 success, 0 failed", "progress": 100, "status": "completed"}
```

**Event Data Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `step` | integer | Current processing step (1-6) |
| `message` | string | Human-readable progress message |
| `progress` | integer | Progress percentage (0-100) |
| `status` | string | "processing", "completed", or "failed" |

**Processing Steps**:

| Step | Name | Progress | Description |
|------|------|----------|-------------|
| 1 | Initialization | 0% | Setup processing environment |
| 2-3 | HL7 Generation | 20-50% | Create HL7 messages for each patient |
| 4 | Mirth Transmission | 50-70% | Send messages via MLLP |
| 5 | ACK Processing | 70-90% | Process acknowledgments from Mirth |
| 6 | Completion | 100% | Finalize and cleanup |

**Status Codes**:
- `200 OK`: Stream established
- `404 Not Found`: Upload ID not found

**Code Example (React Component)**:

```javascript
import React, { useState, useEffect } from 'react';

function ProgressMonitor({ uploadId }) {
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [status, setStatus] = useState('processing');

  useEffect(() => {
    const eventSource = new EventSource(
      `http://localhost:8000/api/upload/${uploadId}/stream`
    );

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      setProgress(data.progress);
      setMessage(data.message);
      setStatus(data.status);

      if (data.status === 'completed' || data.status === 'failed') {
        eventSource.close();
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
      setStatus('failed');
    };

    return () => eventSource.close();
  }, [uploadId]);

  return (
    <div>
      <h3>Processing Status: {status}</h3>
      <div className="progress-bar">
        <div style={{ width: `${progress}%` }}></div>
      </div>
      <p>{message}</p>
    </div>
  );
}

export default ProgressMonitor;
```

---

### 4. Get Upload Results

#### `GET /api/upload/{upload_id}/results`

**Description**: Retrieve final processing results after completion.

**Request**:
```bash
curl http://localhost:8000/api/upload/upload_1735470600_abc123/results
```

**Response** (200 OK):
```json
{
  "upload_id": "upload_1735470600_abc123",
  "status": "completed",
  "total_processed": 3,
  "successful": 3,
  "failed": 0,
  "results": [
    {
      "patient": "John Doe (MRN: MRN001)",
      "hl7_message": "MSH|^~\\&|InterfaceWizard|IW|Mirth|Mirth|20251229113000||ADT^A01|MSG001|P|2.5\nEVN|A01|20251229113000\nPID|1||MRN001^^^MRN||Doe^John||19800515|M\nPV1|1|O\nZPI|a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "mirth_ack": "MSH|^~\\&|Mirth|Mirth|InterfaceWizard|IW|20251229113001||ACK|ACK001|P|2.5\nMSA|AA|MSG001",
      "status": "success",
      "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    }
  ]
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `upload_id` | string | Processing job ID |
| `status` | string | "completed" or "failed" |
| `total_processed` | integer | Total patients processed |
| `successful` | integer | Successfully processed count |
| `failed` | integer | Failed processing count |
| `results` | array | Detailed results for each patient |

**Status Codes**:
- `200 OK`: Results retrieved
- `404 Not Found`: Upload ID not found

---

### 5. Dashboard Statistics

#### `GET /api/dashboard/stats`

**Description**: Retrieve aggregated statistics for all uploads.

**Request**:
```bash
curl http://localhost:8000/api/dashboard/stats
```

**Response** (200 OK):
```json
{
  "total_processed": 150,
  "hl7_messages_generated": 148,
  "successful_sends": 145,
  "failed_sends": 3,
  "success_rate": 96.67
}
```

---

### 6. System Status

#### `GET /api/dashboard/system-status`

**Description**: Check connectivity and health of integrated systems.

**Request**:
```bash
curl http://localhost:8000/api/dashboard/system-status
```

**Response** (200 OK):
```json
{
  "openemr_connection": {
    "status": "Active",
    "last_sync": "2025-12-29T11:30:00Z"
  },
  "hl7_parser": {
    "status": "Running"
  },
  "message_queue": {
    "status": "Ready",
    "pending": 0
  }
}
```

---

### 7. Health Check

#### `GET /health`

**Description**: Basic server health check.

**Request**:
```bash
curl http://localhost:8000/health
```

**Response**:
```json
{
  "status": "healthy",
  "message": "Interface Wizard API is running"
}
```

---

## Data Models

### PatientRecord

```python
class PatientRecord(BaseModel):
    index: int                          # Row index in CSV (0-based)
    uuid: str                           # Unique identifier (UUID v4)
    mrn: str                            # Medical Record Number
    firstName: str                      # Patient first name
    lastName: str                       # Patient last name
    dateOfBirth: str                    # Date of birth (YYYY-MM-DD)
    gender: str                         # "Male", "Female", "Other"
    phone: Optional[str] = None         # Contact phone number
    email: Optional[str] = None         # Email address
    address: Optional[str] = None       # Full street address
    city: Optional[str] = None          # City
    state: Optional[str] = None         # State/Province
    zip: Optional[str] = None           # ZIP/Postal code
    validation_status: str              # "valid" or "invalid"
    validation_messages: List[str] = [] # List of validation errors
```

### ValidationError

```python
class ValidationError(BaseModel):
    row: int                # CSV row number
    field: str              # Field name with error
    error: str              # Error description
    value: Any              # Invalid value
    severity: str           # "error" or "warning"
```

### UploadResponse

```python
class UploadResponse(BaseModel):
    session_id: str                         # Session UUID
    file_name: str                          # Original filename
    file_type: str                          # "csv" or "excel"
    total_records: int                      # Total records parsed
    valid_records: int                      # Valid patient count
    invalid_records: int                    # Invalid patient count
    patients: List[PatientRecord]           # All patient records
    validation_errors: List[ValidationError] # Validation errors
    column_mapping: Dict[str, str]          # Column to field mapping
    expires_at: str                         # Session expiration (ISO 8601)
    timestamp: str                          # Upload time (ISO 8601)
```

### ConfirmUploadRequest

```python
class ConfirmUploadRequest(BaseModel):
    session_id: str                     # Session UUID from upload
    selected_indices: List[int] = []    # Patient indices (empty = all)
    send_to_mirth: bool = True          # Send to Mirth or dry-run
```

### ConfirmUploadResponse

```python
class ConfirmUploadResponse(BaseModel):
    upload_id: str          # Processing job UUID
    status: str             # "processing"
    total_selected: int     # Number of patients processing
    message: str            # Status message
    stream_url: str         # SSE endpoint URL
```

---

## CSV File Format

### Required Columns (Tier 1 - Critical)

| Column Name | Aliases | Type | Format | Example |
|-------------|---------|------|--------|---------|
| `MRN` | mrn, medical_record_number, patient_id | string | Alphanumeric | MRN001 |
| `FirstName` | first_name, fname, given_name | string | Text | John |
| `LastName` | last_name, lname, surname | string | Text | Doe |
| `DOB` | dob, date_of_birth, birthdate | date | See below | 1980-05-15 |
| `Gender` | gender, sex | string | M, F, Male, Female | Male |

### Supported Date Formats

- `YYYY-MM-DD` (ISO 8601) - **Recommended**
- `MM/DD/YYYY` (US format)
- `DD-MM-YYYY` (European format)
- `YYYY/MM/DD`
- `DD/MM/YYYY`
- `MM-DD-YYYY`

### Sample CSV

```csv
MRN,FirstName,LastName,DOB,Gender,Phone,Email
MRN001,John,Doe,1980-05-15,M,555-1234,john@example.com
MRN002,Jane,Smith,1990-08-20,F,555-5678,jane@example.com
MRN003,Bob,Johnson,1975-12-10,M,555-9012,bob@example.com
```

### Dynamic Column Matching

The backend supports **TWO intelligent mapping strategies** to automatically detect column names:

1. **🤖 LLM-Based Mapping** (Default, Recommended) - Uses OpenAI GPT-4o-mini for true intelligence
2. **🔧 Fuzzy Matching** (Fallback) - Rule-based keyword detection

#### 🤖 LLM-Based Column Mapping (NEW!)

**The truly intelligent approach** - Uses AI to understand column names contextually.

**How It Works:**
- Sends column names to GPT-4o-mini
- LLM analyzes semantics, context, and meaning
- Returns mapping with confidence scores
- Handles any variation, typo, or language
- **No need to maintain keyword lists**

**Advantages:**
✅ **True intelligence** - Understands context (e.g., "Full Name" vs "Last Name")
✅ **Infinite variations** - Works with ANY reasonable column name
✅ **Typo tolerant** - Handles misspellings intelligently
✅ **Multi-language support** - Can understand non-English column names
✅ **Complex reasoning** - Can split compound fields
✅ **Self-improving** - Gets better as LLM models improve
✅ **Confidence scores** - Shows how certain the mapping is
✅ **Warnings** - Flags ambiguous mappings

**Example LLM Mapping:**

Input columns:
```json
["Patient Last Name", "Pateint First Name", "Email Address", "Phone Number"]
```

LLM Output:
```json
{
  "mappings": [
    {"column": "Patient Last Name", "field": "lastName", "confidence": 1.0},
    {"column": "Pateint First Name", "field": "firstName", "confidence": 0.98},
    {"column": "Email Address", "field": "email", "confidence": 1.0},
    {"column": "Phone Number", "field": "phone", "confidence": 1.0}
  ],
  "warnings": ["Detected typo in 'Pateint First Name' - mapped to firstName"],
  "unmapped": []
}
```

**When LLM is Used:**
- By default (`use_llm_mapping=true`)
- When OpenAI API key is configured
- Automatically falls back to fuzzy matching if LLM fails

**How to Disable:**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@patients.xlsx" \
  -F "use_llm_mapping=false"  # Use fuzzy matching instead
```

#### 🔧 Fuzzy Matching (Fallback)

Rule-based approach using keyword detection (used when LLM is disabled or unavailable).

**How It Works**

The system employs a multi-strategy approach:

1. **Exact Match** (fastest): Checks against predefined variations
2. **Fuzzy Keyword Match**: Extracts meaningful keywords and matches them
3. **Substring Match**: Detects keywords within compound words

#### Noise Word Removal

The following words are automatically ignored during matching:
- "patient", "person", "record", "data", "info", "information"
- "field", "column", "value", "the", "a", "an"

#### Examples of Supported Column Names

| Your Column Name | Detected As | How Matched |
|-----------------|-------------|-------------|
| `Patient First Name` | `firstName` | Fuzzy (keyword: "first") |
| `Pateint First Name` | `firstName` | Fuzzy (typo tolerance) |
| `Patient Last Name` | `lastName` | Fuzzy (keyword: "last") |
| `Date of Birth` | `dateOfBirth` | Exact match |
| `DOB` | `dateOfBirth` | Exact match |
| `Email Address` | `email` | Fuzzy (keyword: "email") |
| `Phone Number` | `phone` | Fuzzy (keyword: "phone") |
| `Address 1` | `address` | Fuzzy (keyword: "address") |
| `Zipcode` | `zip` | Fuzzy (substring: "zip") |
| `Medical Record Number` | `mrn` | Predefined alias |

#### Supported Field Keywords

| Field | Matching Keywords |
|-------|------------------|
| `firstName` | first, given, fname |
| `lastName` | last, family, surname, lname |
| `dateOfBirth` | birth, dob, born |
| `gender` | gender, sex |
| `email` | email, e-mail, mail |
| `phone` | phone, tel, mobile, cell |
| `mrn` | mrn |
| `address` | address, street, addr |
| `city` | city, town |
| `state` | state, province, region |
| `zip` | zip, postal, postcode |

#### Matching Process Example

For column `"Patient Last Name"`:

1. **Normalize**: Convert to lowercase → `"patient last name"`
2. **Split**: Extract words → `["patient", "last", "name"]`
3. **Filter Noise**: Remove "patient" → `["last", "name"]`
4. **Match Keywords**: Find "last" matches `lastName` field ✅

#### What This Means For You

✅ **No need to rename columns** - use any reasonable format
✅ **Typo tolerant** - "Pateint" still matches
✅ **Flexible formatting** - Works with spaces, underscores, hyphens
✅ **Compound names** - "Email Address", "Phone Number" work fine
✅ **Prefix variations** - "Patient First Name", "Person First Name", etc.

---

## Code Examples

### Complete Workflow (React)

```javascript
import React, { useState } from 'react';

function PatientUploadWorkflow() {
  const [sessionId, setSessionId] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [selectedIndices, setSelectedIndices] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);

  // Step 1: Upload file
  const handleFileUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('http://localhost:8000/api/upload', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();
    setSessionId(data.session_id);
    setPreviewData(data);

    // Auto-select all valid patients
    const validIndices = data.patients
      .filter(p => p.validation_status === 'valid')
      .map(p => p.index);
    setSelectedIndices(validIndices);
  };

  // Step 2: Confirm and process
  const handleConfirm = async () => {
    setProcessing(true);

    const response = await fetch('http://localhost:8000/api/upload/confirm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        selected_indices: selectedIndices,
        send_to_mirth: true
      })
    });

    const data = await response.json();

    // Step 3: Monitor progress
    const eventSource = new EventSource(
      `http://localhost:8000${data.stream_url}`
    );

    eventSource.onmessage = (event) => {
      const progressData = JSON.parse(event.data);
      setProgress(progressData.progress);

      if (progressData.status === 'completed') {
        eventSource.close();
        setProcessing(false);
        alert('Processing complete!');
      }
    };
  };

  return (
    <div>
      <h2>Patient Upload</h2>

      <input
        type="file"
        accept=".csv,.xlsx"
        onChange={(e) => handleFileUpload(e.target.files[0])}
      />

      {previewData && (
        <div>
          <h3>Preview: {previewData.total_records} records</h3>
          <p>Valid: {previewData.valid_records}, Invalid: {previewData.invalid_records}</p>

          <button onClick={handleConfirm} disabled={processing}>
            {processing ? `Processing... ${progress}%` : 'Confirm & Process'}
          </button>
        </div>
      )}
    </div>
  );
}

export default PatientUploadWorkflow;
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid file, missing parameters |
| 404 | Not Found | Session/upload not found or expired |
| 500 | Internal Server Error | Backend processing error |

### Error Response Format

```json
{
  "detail": "Session not found or expired. Please upload the file again."
}
```

---

## Testing Guide

### Basic Workflow Test

```bash
# 1. Upload file
curl -X POST http://localhost:8000/api/upload \
  -F "file=@patients.csv" \
  > preview.json

# 2. Extract session_id
SESSION_ID=$(cat preview.json | jq -r '.session_id')

# 3. Confirm processing
curl -X POST http://localhost:8000/api/upload/confirm \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"selected_indices\": [], \"send_to_mirth\": true}" \
  > confirm.json

# 4. Extract upload_id
UPLOAD_ID=$(cat confirm.json | jq -r '.upload_id')

# 5. Monitor progress
curl -N http://localhost:8000/api/upload/$UPLOAD_ID/stream

# 6. Get results
curl http://localhost:8000/api/upload/$UPLOAD_ID/results
```

---

## Troubleshooting

### CORS Errors

**Symptom**: `Access to fetch blocked by CORS policy`

**Solution**: ✅ Fixed in v3.0 - CORS middleware configured for React, Angular, Vite

### Mirth Connection Refused

**Symptom**: `Connection refused`

**Solutions**:
- Start Mirth Connect service
- Check port 6661 is listening: `netstat -an | grep 6661`
- Test connection: `telnet localhost 6661`

### Session Expired

**Symptom**: `Session not found or expired`

**Solutions**:
- Re-upload file to create new session
- Sessions expire after 1 hour

---

## Conclusion

This documentation provides a complete guide to the Interface Wizard Backend API. For additional support:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Repository**: https://github.com/Shirishag1911/interface-wizard

---

**Document Version**: 3.0
**Last Updated**: December 29, 2025
**Author**: Shirisha G
