# Interface Wizard Backend API Documentation v3.0

## Document Information
- **Version**: 3.0.0
- **Date**: December 29, 2025
- **Application**: Interface Wizard - Smart HL7 Message Generator
- **Backend Framework**: FastAPI 0.104+
- **API Base URL**: `http://localhost:8000`

---

## Table of Contents
1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Technology Stack](#technology-stack)
4. [System Architecture](#system-architecture)
5. [Quick Start Guide](#quick-start-guide)
6. [API Endpoints Reference](#api-endpoints-reference)
7. [Data Models & Interfaces](#data-models--interfaces)
8. [CSV/Excel File Format](#csvexcel-file-format)
9. [Code Architecture](#code-architecture)
10. [Validation System](#validation-system)
11. [Error Handling](#error-handling)
12. [Testing Guide](#testing-guide)
13. [Troubleshooting](#troubleshooting)

---

## Overview

**Interface Wizard** is a sophisticated healthcare integration platform that converts patient data from CSV/Excel files into HL7 v2.5 messages and transmits them to Electronic Health Record (EHR) systems via Mirth Connect using the MLLP (Minimal Lower Layer Protocol).

### Purpose
- Streamline bulk patient registration workflows
- Generate standards-compliant HL7 ADT^A04 messages
- Provide real-time processing progress via Server-Sent Events (SSE)
- Enable preview and confirmation workflow for data validation
- Track patient records with UUID for data integrity

### Target Users
- Healthcare IT administrators
- Integration engineers
- Clinical system implementers
- EHR migration teams

---

## Key Features

### 1. **Multi-Format File Support**
- CSV (Comma-Separated Values)
- Excel (.xlsx, .xls)
- Flexible column name mapping (case-insensitive)
- Support for various date formats (YYYY-MM-DD, MM/DD/YYYY, DD-MM-YYYY, etc.)

### 2. **Preview & Confirmation Workflow** 🆕
- **Two-phase upload process**:
  1. **Preview Phase**: Upload file → System validates → Returns preview with patient records
  2. **Confirmation Phase**: User reviews → Confirms selection → System processes
- **UUID Tracking**: Each patient record assigned unique identifier
- **Session Management**: 1-hour expiration for upload sessions
- **Selective Processing**: Choose which patients to process
- **Pagination Support**: Handle large datasets efficiently

### 3. **AI-Powered HL7 Generation**
- **Primary Engine**: OpenAI GPT-4o-mini for intelligent field extraction
- **Fallback Mechanism**: Rule-based generator when AI unavailable
- **Custom ZPI Segment**: UUID tracking in HL7 messages

### 4. **3-Tier Validation System**
- **Tier 1 (Critical)**: MRN, First Name, Last Name, DOB, Gender
- **Tier 2 (Important)**: Phone, Email, Address
- **Tier 3 (Optional)**: Race, Ethnicity, Language, Emergency Contact

### 5. **Real-Time Progress Tracking**
- Server-Sent Events (SSE) for live updates
- 6-step workflow visualization:
  1. Initialization
  2. File parsing
  3. HL7 message generation
  4. Mirth transmission
  5. ACK processing
  6. Completion

### 6. **Dashboard & Monitoring**
- System statistics (total processed, success/failure counts)
- Health check endpoints
- System status monitoring (Mirth connectivity, OpenAI availability)

### 7. **CORS Support** 🆕
- Pre-configured for React (port 3000), Angular (port 4200), Vite (port 5173)
- Development-friendly with wildcard origin support

---

## Technology Stack

### Backend
| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | FastAPI | 0.104+ |
| **Language** | Python | 3.9+ |
| **HL7 Library** | python-hl7 | 0.4.5 |
| **AI Engine** | OpenAI API | GPT-4o-mini |
| **Data Processing** | pandas | 2.0+ |
| **Async Runtime** | asyncio | Built-in |
| **ASGI Server** | uvicorn | 0.27+ |

### Integration
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Mirth Connect** | v4.x | HL7 message routing |
| **MLLP Protocol** | TCP Socket | Healthcare message transport |
| **OpenEMR** | v7.x | Target EHR system |
| **MySQL** | 8.0+ | Patient data storage |

### Frontend (Separate)
- **React**: 18.x with MUI
- **Angular**: 17+ with Material Design

---

## System Architecture

### High-Level Architecture

```
┌─────────────────┐
│   Frontend      │
│  (React/Angular)│
│  Port: 3000/4200│
└────────┬────────┘
         │ HTTP/REST + SSE
         ▼
┌─────────────────────────────────────┐
│   FastAPI Backend (Port 8000)       │
│  ┌──────────────────────────────┐   │
│  │ CORS Middleware              │   │
│  ├──────────────────────────────┤   │
│  │ API Endpoints                │   │
│  │ - Upload Preview             │   │
│  │ - Confirm Upload             │   │
│  │ - Stream Progress (SSE)      │   │
│  │ - Dashboard Stats            │   │
│  ├──────────────────────────────┤   │
│  │ Business Logic               │   │
│  │ - CSV Parser                 │   │
│  │ - Validator (3-Tier)         │   │
│  │ - HL7 Generator (AI/Fallback)│   │
│  │ - Session Manager            │   │
│  ├──────────────────────────────┤   │
│  │ In-Memory Storage            │   │
│  │ - upload_sessions{}          │   │
│  │ - dashboard_stats{}          │   │
│  └──────────────────────────────┘   │
└────────┬───────────────────┬────────┘
         │                   │
         │ MLLP (Port 6661)  │ OpenAI API
         ▼                   ▼
┌─────────────────┐   ┌──────────────┐
│ Mirth Connect   │   │  OpenAI      │
│  - HL7 Router   │   │  GPT-4o-mini │
│  - Transformer  │   └──────────────┘
└────────┬────────┘
         │ SQL INSERT
         ▼
┌─────────────────┐
│  MySQL Database │
│  (OpenEMR)      │
│  patient_data   │
└─────────────────┘
```

### Data Flow

#### Preview & Confirmation Workflow 🆕
```
1. User uploads CSV/Excel file
   ↓
2. Backend: parse_csv_with_preview()
   - Parses file
   - Validates each row
   - Assigns UUID to each patient
   - Creates UploadSession
   ↓
3. Backend returns UploadPreviewResponse
   - session_id
   - total_records
   - valid_count, invalid_count
   - List of PatientRecord objects
   ↓
4. Frontend displays preview table
   - User reviews patient data
   - User selects patients to process
   ↓
5. User confirms selection
   ↓
6. Backend: process_confirmed_patients()
   - Retrieves session by session_id
   - Filters selected UUIDs
   - Generates HL7 for each patient
   - Sends to Mirth via MLLP
   - Streams progress via SSE
   ↓
7. Frontend receives real-time updates
   - Displays progress bar
   - Shows step-by-step status
   ↓
8. Completion: Upload results available
   - Processed count
   - Success/failure breakdown
```

#### Direct Upload Workflow (Legacy)
```
1. User uploads CSV/Excel
   ↓
2. Backend processes immediately
   - Parses → Validates → Generates HL7 → Sends to Mirth
   ↓
3. Real-time progress via SSE
   ↓
4. Results returned
```

---

## Quick Start Guide

### Prerequisites
1. **Python 3.9+** installed
2. **OpenAI API Key** (optional, fallback available)
3. **Mirth Connect** running on port 6661
4. **MySQL/OpenEMR** database accessible

### Installation

```bash
# Clone repository
git clone https://github.com/Shirishag1911/interface-wizard.git
cd interface-wizard/actual-code

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install fastapi uvicorn pandas openpyxl hl7 openai python-multipart

# Configure OpenAI API Key (optional)
# Edit main_with_fastapi.py line 46:
OPENAI_API_KEY = "sk-your-actual-api-key-here"

# Configure Mirth Connect (if different)
# Edit lines 47-48:
MIRTH_HOST = "localhost"
MIRTH_PORT = 6661
```

### Running the Server

```bash
# Start FastAPI server
python main_with_fastapi.py --api

# Server starts on http://localhost:8000
# Swagger UI available at http://localhost:8000/docs
```

### Testing CORS Fix

```bash
# From frontend (React/Angular)
fetch('http://localhost:8000/api/dashboard/stats')
  .then(response => response.json())
  .then(data => console.log(data));

# Should now work without CORS errors
```

---

## API Endpoints Reference

### Base URL
```
http://localhost:8000
```

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

### 1. Health Check

#### `GET /health`

**Description**: Basic health check endpoint to verify server is running.

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

**Status Codes**:
- `200 OK`: Server is healthy

---

### 2. Dashboard Statistics

#### `GET /api/dashboard/stats`

**Description**: Retrieve aggregated statistics for processed uploads.

**Request**:
```bash
curl http://localhost:8000/api/dashboard/stats
```

**Response**:
```json
{
  "total_processed": 150,
  "hl7_messages_generated": 148,
  "successful_sends": 145,
  "failed_sends": 3,
  "success_rate": 96.67
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `total_processed` | integer | Total patient records processed |
| `hl7_messages_generated` | integer | Number of HL7 messages created |
| `successful_sends` | integer | Successfully sent to Mirth |
| `failed_sends` | integer | Failed transmissions |
| `success_rate` | float | Percentage of successful sends |

**Status Codes**:
- `200 OK`: Statistics retrieved successfully

---

### 3. System Status

#### `GET /api/dashboard/system-status`

**Description**: Check connectivity to external systems (Mirth, OpenAI).

**Request**:
```bash
curl http://localhost:8000/api/dashboard/system-status
```

**Response**:
```json
{
  "mirth_connection": "connected",
  "mirth_host": "localhost",
  "mirth_port": 6661,
  "openai_available": true,
  "openai_model": "gpt-4o-mini",
  "backend_status": "operational",
  "timestamp": "2025-12-29T10:30:00Z"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `mirth_connection` | string | "connected" or "disconnected" |
| `mirth_host` | string | Mirth server hostname |
| `mirth_port` | integer | Mirth MLLP port |
| `openai_available` | boolean | Whether OpenAI SDK is loaded |
| `openai_model` | string | AI model name |
| `backend_status` | string | Overall backend health |
| `timestamp` | string | ISO 8601 timestamp |

**Status Codes**:
- `200 OK`: System status retrieved

---

### 4. Upload Preview (New Workflow) 🆕

#### `POST /api/upload-preview`

**Description**: Upload CSV/Excel file for preview without processing. Creates a session with validated patient records.

**Request**:
```bash
curl -X POST http://localhost:8000/api/upload-preview \
  -F "file=@patients.csv"
```

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Yes | CSV or Excel file (.csv, .xlsx, .xls) |

**Response**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_records": 10,
  "valid_count": 8,
  "invalid_count": 2,
  "patients": [
    {
      "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "mrn": "MRN001",
      "first_name": "John",
      "last_name": "Doe",
      "dob": "1980-05-15",
      "gender": "M",
      "phone": "555-1234",
      "email": "john.doe@example.com",
      "address": "123 Main St, City, State 12345",
      "race": "White",
      "ethnicity": "Not Hispanic or Latino",
      "language": "English",
      "ssn": "123-45-6789",
      "validation_status": "valid",
      "validation_errors": []
    },
    {
      "uuid": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "mrn": "MRN002",
      "first_name": "",
      "last_name": "Smith",
      "dob": "1990-08-20",
      "gender": "F",
      "validation_status": "invalid",
      "validation_errors": [
        {
          "field": "first_name",
          "tier": 1,
          "message": "Missing required field: first_name (Tier 1 - Critical)"
        }
      ]
    }
  ],
  "session_expires_at": "2025-12-29T11:30:00Z"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string (UUID) | Unique session identifier |
| `total_records` | integer | Total rows in uploaded file |
| `valid_count` | integer | Number of valid patient records |
| `invalid_count` | integer | Number of invalid records |
| `patients` | array | Array of PatientRecord objects |
| `session_expires_at` | string | Session expiration timestamp (1 hour) |

**PatientRecord Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `uuid` | string | Unique patient record identifier |
| `mrn` | string | Medical Record Number |
| `first_name` | string | Patient first name |
| `last_name` | string | Patient last name |
| `dob` | string | Date of birth (YYYY-MM-DD) |
| `gender` | string | Gender (M/F/O/U) |
| `phone` | string | Contact phone |
| `email` | string | Email address |
| `address` | string | Full address |
| `race` | string | Race |
| `ethnicity` | string | Ethnicity |
| `language` | string | Preferred language |
| `ssn` | string | Social Security Number |
| `validation_status` | string | "valid" or "invalid" |
| `validation_errors` | array | List of ValidationError objects |

**Status Codes**:
- `200 OK`: File processed successfully
- `400 Bad Request`: Invalid file format or no file uploaded
- `500 Internal Server Error`: Processing failed

**Example with cURL**:
```bash
curl -X POST http://localhost:8000/api/upload-preview \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/patients.csv"
```

---

### 5. Confirm Upload (Process Selected Patients) 🆕

#### `POST /api/confirm-upload`

**Description**: Process selected patients from a preview session. Generates HL7 messages and sends to Mirth.

**Request**:
```bash
curl -X POST http://localhost:8000/api/confirm-upload \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "selected_patient_uuids": [
      "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "c3d4e5f6-a7b8-9012-cdef-123456789012"
    ]
  }'
```

**Request Body**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "selected_patient_uuids": [
    "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  ]
}
```

**Request Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string (UUID) | Yes | Session ID from preview response |
| `selected_patient_uuids` | array[string] | Yes | List of patient UUIDs to process |

**Response**:
```json
{
  "upload_id": "upload_1735470600_abc123",
  "status": "processing",
  "total_selected": 2,
  "message": "Processing 2 patients",
  "stream_url": "/api/upload/upload_1735470600_abc123/stream"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `upload_id` | string | Unique upload job identifier |
| `status` | string | "processing" initially |
| `total_selected` | integer | Number of patients to process |
| `message` | string | Human-readable status message |
| `stream_url` | string | SSE endpoint for real-time progress |

**Status Codes**:
- `200 OK`: Processing started successfully
- `400 Bad Request`: Invalid session_id or empty patient list
- `404 Not Found`: Session expired or not found
- `500 Internal Server Error`: Processing initiation failed

**Next Steps**:
After receiving the response, connect to the `stream_url` to monitor progress:
```javascript
const eventSource = new EventSource(
  'http://localhost:8000/api/upload/upload_1735470600_abc123/stream'
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.step, data.message, data.progress);
};
```

---

### 6. Get Upload Preview (Paginated) 🆕

#### `GET /api/upload/{session_id}/preview`

**Description**: Retrieve preview data for a session with pagination support.

**Request**:
```bash
curl "http://localhost:8000/api/upload/550e8400-e29b-41d4-a716-446655440000/preview?page=1&page_size=10"
```

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string (UUID) | Yes | Session identifier from preview upload |

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | No | 1 | Page number (1-indexed) |
| `page_size` | integer | No | 10 | Records per page |

**Response**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_records": 100,
  "valid_count": 95,
  "invalid_count": 5,
  "page": 1,
  "page_size": 10,
  "total_pages": 10,
  "patients": [
    {
      "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "mrn": "MRN001",
      "first_name": "John",
      "last_name": "Doe",
      "validation_status": "valid"
    }
  ],
  "session_expires_at": "2025-12-29T11:30:00Z"
}
```

**Status Codes**:
- `200 OK`: Preview data retrieved
- `404 Not Found`: Session not found or expired
- `400 Bad Request`: Invalid page/page_size parameters

---

### 7. Direct Upload (Legacy Mode)

#### `POST /api/upload`

**Description**: Upload and process CSV/Excel file immediately without preview.

**Request**:
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@patients.csv" \
  -F "trigger_event=A04"
```

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Yes | CSV or Excel file |
| `trigger_event` | string | No | HL7 trigger event (default: A04) |

**Response**:
```json
{
  "upload_id": "upload_1735470123_xyz789",
  "status": "processing",
  "message": "File uploaded successfully, processing started",
  "stream_url": "/api/upload/upload_1735470123_xyz789/stream"
}
```

**Status Codes**:
- `200 OK`: Upload started
- `400 Bad Request`: No file or invalid format
- `500 Internal Server Error`: Processing failed

---

### 8. Stream Upload Progress (Server-Sent Events)

#### `GET /api/upload/{upload_id}/stream`

**Description**: Real-time progress updates via Server-Sent Events (SSE).

**Request**:
```javascript
// JavaScript example
const eventSource = new EventSource(
  'http://localhost:8000/api/upload/upload_1735470123_xyz789/stream'
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Step ${data.step}: ${data.message} (${data.progress}%)`);

  if (data.step === 6) {
    eventSource.close(); // Processing complete
  }
};

eventSource.onerror = (error) => {
  console.error('SSE error:', error);
  eventSource.close();
};
```

**Response Stream Format**:
```
data: {"step": 1, "message": "Initializing upload", "progress": 0, "status": "processing"}

data: {"step": 2, "message": "Parsing CSV file", "progress": 16, "status": "processing"}

data: {"step": 3, "message": "Generating HL7 messages (1/10)", "progress": 33, "status": "processing"}

data: {"step": 4, "message": "Sending to Mirth (1/10)", "progress": 50, "status": "processing"}

data: {"step": 5, "message": "Processing ACKs (1/10)", "progress": 66, "status": "processing"}

data: {"step": 6, "message": "Upload complete: 10 processed, 9 successful, 1 failed", "progress": 100, "status": "completed"}
```

**Event Data Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `step` | integer | Current step (1-6) |
| `message` | string | Human-readable progress message |
| `progress` | integer | Overall progress percentage (0-100) |
| `status` | string | "processing", "completed", "failed" |

**Workflow Steps**:
1. **Initialization** (0% - 16%)
2. **File Parsing** (16% - 33%)
3. **HL7 Generation** (33% - 50%)
4. **Mirth Transmission** (50% - 66%)
5. **ACK Processing** (66% - 83%)
6. **Completion** (83% - 100%)

**Status Codes**:
- `200 OK`: Stream started
- `404 Not Found`: Upload ID not found

---

### 9. Get Upload Status

#### `GET /api/upload/{upload_id}/status`

**Description**: Get current status of an upload job (snapshot, not real-time).

**Request**:
```bash
curl http://localhost:8000/api/upload/upload_1735470123_xyz789/status
```

**Response**:
```json
{
  "upload_id": "upload_1735470123_xyz789",
  "status": "completed",
  "current_step": 6,
  "progress": 100,
  "message": "Upload complete: 10 processed, 9 successful, 1 failed"
}
```

**Status Codes**:
- `200 OK`: Status retrieved
- `404 Not Found`: Upload ID not found

---

### 10. Get Upload Results

#### `GET /api/upload/{upload_id}/results`

**Description**: Retrieve detailed results after upload completes.

**Request**:
```bash
curl http://localhost:8000/api/upload/upload_1735470123_xyz789/results
```

**Response**:
```json
{
  "upload_id": "upload_1735470123_xyz789",
  "status": "completed",
  "total_processed": 10,
  "successful": 9,
  "failed": 1,
  "results": [
    {
      "patient": "John Doe (MRN: MRN001)",
      "hl7_message": "MSH|^~\\&|InterfaceWizard|...",
      "mirth_ack": "MSA|AA|...",
      "status": "success"
    },
    {
      "patient": "Jane Smith (MRN: MRN002)",
      "error": "Connection timeout to Mirth",
      "status": "failed"
    }
  ]
}
```

**Status Codes**:
- `200 OK`: Results retrieved
- `404 Not Found`: Upload ID not found or results not ready

---

### 11. Upload Excel File

#### `POST /api/upload-excel`

**Description**: Specialized endpoint for Excel files (functionally identical to `/api/upload`).

**Request**:
```bash
curl -X POST http://localhost:8000/api/upload-excel \
  -F "file=@patients.xlsx"
```

**Response**: Same as `/api/upload`

**Status Codes**: Same as `/api/upload`

---

### 12. Get Supported Events

#### `GET /api/supported-events`

**Description**: List all supported HL7 trigger events.

**Request**:
```bash
curl http://localhost:8000/api/supported-events
```

**Response**:
```json
{
  "supported_events": [
    "A04",
    "A08",
    "A28"
  ],
  "default_event": "A04",
  "descriptions": {
    "A04": "Register a Patient (ADT^A04)",
    "A08": "Update Patient Information (ADT^A08)",
    "A28": "Add Person Information (ADT^A28)"
  }
}
```

**Status Codes**:
- `200 OK`: Events retrieved

---

## Data Models & Interfaces

### PatientRecord Model 🆕

```python
class PatientRecord(BaseModel):
    uuid: str                          # Unique identifier for this record
    mrn: str                            # Medical Record Number
    first_name: str
    last_name: str
    dob: str                            # YYYY-MM-DD format
    gender: str                         # M, F, O, U
    phone: Optional[str] = ""
    email: Optional[str] = ""
    address: Optional[str] = ""
    race: Optional[str] = ""
    ethnicity: Optional[str] = ""
    language: Optional[str] = "English"
    ssn: Optional[str] = ""
    validation_status: str              # "valid" or "invalid"
    validation_errors: List[ValidationError] = []
```

### ValidationError Model

```python
class ValidationError(BaseModel):
    field: str                          # Field name
    tier: int                           # 1 (Critical), 2 (Important), 3 (Optional)
    message: str                        # Error description
```

### UploadSession Model 🆕

```python
class UploadSession(BaseModel):
    session_id: str                     # UUID
    patients: List[PatientRecord]
    total_records: int
    valid_count: int
    invalid_count: int
    created_at: datetime
    expires_at: datetime                # created_at + 1 hour
```

### UploadPreviewResponse Model 🆕

```python
class UploadPreviewResponse(BaseModel):
    session_id: str
    total_records: int
    valid_count: int
    invalid_count: int
    patients: List[PatientRecord]
    session_expires_at: str             # ISO 8601 timestamp
```

### ConfirmUploadRequest Model 🆕

```python
class ConfirmUploadRequest(BaseModel):
    session_id: str
    selected_patient_uuids: List[str]
```

### ConfirmUploadResponse Model 🆕

```python
class ConfirmUploadResponse(BaseModel):
    upload_id: str
    status: str                         # "processing"
    total_selected: int
    message: str
    stream_url: str
```

### UploadResponse Model

```python
class UploadResponse(BaseModel):
    upload_id: str
    status: str                         # "processing", "completed", "failed"
    message: str
    stream_url: Optional[str] = None
```

---

## CSV/Excel File Format

### Required Columns (Tier 1 - Critical)

| Column Name | Aliases | Type | Format | Example |
|-------------|---------|------|--------|---------|
| `MRN` | mrn, medical_record_number, patient_id | string | Alphanumeric | MRN001 |
| `FirstName` | first_name, fname, given_name | string | Text | John |
| `LastName` | last_name, lname, surname, family_name | string | Text | Doe |
| `DOB` | dob, date_of_birth, birthdate, birth_date | date | YYYY-MM-DD, MM/DD/YYYY, DD-MM-YYYY | 1980-05-15 |
| `Gender` | gender, sex | string | M, F, Male, Female, O, U | M |

### Important Columns (Tier 2)

| Column Name | Aliases | Type | Example |
|-------------|---------|------|---------|
| `Phone` | phone, phone_number, contact | string | 555-1234-5678 |
| `Email` | email, email_address | string | john.doe@example.com |
| `Address` | address, street_address, full_address | string | 123 Main St, City, State 12345 |

### Optional Columns (Tier 3)

| Column Name | Aliases | Type | Example |
|-------------|---------|------|---------|
| `Race` | race | string | White, Black, Asian, etc. |
| `Ethnicity` | ethnicity | string | Hispanic or Latino, Not Hispanic or Latino |
| `Language` | language, preferred_language | string | English, Spanish, Mandarin |
| `SSN` | ssn, social_security_number | string | 123-45-6789 |

### Column Mapping Rules

1. **Case-Insensitive**: `FirstName`, `firstname`, `FIRSTNAME` all work
2. **Flexible Naming**: `first_name`, `First Name`, `Given Name` supported
3. **Whitespace Handling**: Leading/trailing spaces ignored
4. **Special Characters**: Underscores, spaces, hyphens normalized

### Sample CSV

```csv
MRN,FirstName,LastName,DOB,Gender,Phone,Email,Address,Race,Ethnicity,Language,SSN
MRN001,John,Doe,1980-05-15,M,555-1234,john.doe@example.com,"123 Main St, City, State 12345",White,Not Hispanic or Latino,English,123-45-6789
MRN002,Jane,Smith,05/20/1990,Female,555-5678,jane.smith@example.com,"456 Oak Ave, Town, State 67890",Asian,Not Hispanic or Latino,English,987-65-4321
MRN003,Bob,Johnson,15-08-1975,M,555-9012,bob.j@example.com,"789 Pine Rd, Village, State 11223",Black,Hispanic or Latino,Spanish,111-22-3333
```

### Supported Date Formats

- `YYYY-MM-DD` (ISO 8601) - Recommended
- `MM/DD/YYYY` (US format)
- `DD-MM-YYYY` (European format)
- `YYYY/MM/DD`
- `DD/MM/YYYY`
- `MM-DD-YYYY`

### Gender Normalization

| Input Values | Normalized To |
|--------------|---------------|
| M, Male, MALE, m | M |
| F, Female, FEMALE, f | F |
| O, Other, OTHER, o | O |
| U, Unknown, UNKNOWN, u | U |

---

## Code Architecture

### Project Structure

```
interface-wizard/
├── actual-code/
│   ├── main_with_fastapi.py       # Main backend application (2155 lines)
│   ├── sample_patients.csv        # Test data
│   └── requirements.txt
├── frontend-react/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx
│   │   │   └── UploadPreview.jsx  # NEW: Preview component
│   │   └── services/
│   │       └── api.js
│   └── package.json
├── frontend-angular/
│   ├── src/app/
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   └── upload-preview/    # NEW: Preview component
│   │   └── services/
│   └── package.json
└── docs/
    ├── IW-Backend-API-Documentation-v3.0.md  # This file
    └── ...
```

### Key Code Sections in main_with_fastapi.py

#### 1. Configuration (Lines 1-167)
- Imports and dependencies
- Global constants (OPENAI_API_KEY, MIRTH_HOST, MIRTH_PORT)
- Field tier definitions (FIELD_TIERS)
- Column mapping dictionary (COLUMN_MAPPINGS)
- Pydantic models (PatientRecord, UploadSession, etc.)
- FastAPI app initialization
- **CORS middleware configuration** 🆕

#### 2. Data Storage (Lines 207-235)
- `upload_sessions: Dict[str, Dict]` - In-memory session storage
- `dashboard_stats: Dict` - Statistics tracking

#### 3. Helper Functions (Lines 219-482)
- `_normalize_colname()` - Column name normalization
- `normalize_column_name()` - Enhanced normalization
- `parse_date_flexible()` - Multi-format date parsing
- `validate_patient_record()` - 3-tier validation
- `parse_csv_with_preview()` - CSV parsing with UUID assignment 🆕
- `ClientWrapper` - OpenAI API wrapper with retry logic
- `generate_hl7_fallback()` - Rule-based HL7 generator

#### 4. HL7 Generation (Lines 534-686)
- `generate_hl7_message()` - Primary HL7 generator (AI-powered)
- `add_zpi_segment_with_uuid()` - Custom ZPI segment for UUID tracking 🆕
- `send_to_mirth()` - MLLP protocol implementation

#### 5. Processing Logic (Lines 777-1154)
- `process_confirmed_patients()` - Async processing for confirmed uploads 🆕
- `process_csv_with_progress()` - 6-step workflow with SSE streaming

#### 6. Background Tasks (Lines 1156-1189)
- `cleanup_expired_sessions()` - Scheduled session cleanup 🆕

#### 7. API Endpoints (Lines 1191-2155)
- Health check
- Dashboard endpoints
- Upload preview (NEW)
- Confirm upload (NEW)
- Get preview with pagination (NEW)
- Direct upload (legacy)
- Stream progress (SSE)
- Upload status and results

### CORS Configuration 🆕

```python
# Lines 205-220
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React frontend
        "http://localhost:4200",      # Angular frontend
        "http://localhost:5173",      # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:4200",
        "http://127.0.0.1:5173",
        "*"                           # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Note**: For production, replace `"*"` with specific domain names.

---

## Validation System

### 3-Tier Validation Framework

#### Tier 1: Critical Fields (Must be present and valid)
- **MRN**: Non-empty, unique identifier
- **First Name**: Non-empty string
- **Last Name**: Non-empty string
- **DOB**: Valid date in supported format
- **Gender**: One of M, F, O, U (normalized)

**Failure Impact**: Record marked as `invalid`, not processed

#### Tier 2: Important Fields (Recommended)
- **Phone**: Contact phone number
- **Email**: Email address
- **Address**: Full address

**Failure Impact**: Warning logged, record still processed

#### Tier 3: Optional Fields (Nice to have)
- **Race**: Patient race
- **Ethnicity**: Patient ethnicity
- **Language**: Preferred language
- **SSN**: Social Security Number

**Failure Impact**: No impact, optional fields

### Validation Function

```python
def validate_patient_record(patient: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
    """
    Validates patient record against 3-tier system.

    Returns:
        (is_valid, validation_errors)
        - is_valid: True if all Tier 1 fields present
        - validation_errors: List of all validation issues
    """
    errors = []

    # Tier 1 validation
    for field in FIELD_TIERS["tier_1"]:
        if not patient.get(field):
            errors.append(ValidationError(
                field=field,
                tier=1,
                message=f"Missing required field: {field} (Tier 1 - Critical)"
            ))

    # DOB format validation
    if patient.get("dob"):
        try:
            parse_date_flexible(patient["dob"])
        except:
            errors.append(ValidationError(
                field="dob",
                tier=1,
                message="Invalid date format for DOB"
            ))

    # Tier 2 validation (warnings only)
    for field in FIELD_TIERS["tier_2"]:
        if not patient.get(field):
            errors.append(ValidationError(
                field=field,
                tier=2,
                message=f"Missing important field: {field} (Tier 2 - Important)"
            ))

    # Tier 3 validation (informational)
    for field in FIELD_TIERS["tier_3"]:
        if not patient.get(field):
            errors.append(ValidationError(
                field=field,
                tier=3,
                message=f"Missing optional field: {field} (Tier 3 - Optional)"
            ))

    # Only Tier 1 errors invalidate the record
    is_valid = not any(err.tier == 1 for err in errors)

    return is_valid, errors
```

### Validation Error Response

```json
{
  "uuid": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "validation_status": "invalid",
  "validation_errors": [
    {
      "field": "first_name",
      "tier": 1,
      "message": "Missing required field: first_name (Tier 1 - Critical)"
    },
    {
      "field": "phone",
      "tier": 2,
      "message": "Missing important field: phone (Tier 2 - Important)"
    }
  ]
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful request |
| 400 | Bad Request | Invalid input (missing file, invalid session_id) |
| 404 | Not Found | Resource not found (session expired, upload not found) |
| 500 | Internal Server Error | Backend processing error |

### Error Response Format

```json
{
  "detail": "Session not found or expired",
  "error_code": "SESSION_NOT_FOUND",
  "timestamp": "2025-12-29T10:30:00Z"
}
```

### Common Error Scenarios

#### 1. Session Expired
```json
{
  "detail": "Session 550e8400-e29b-41d4-a716-446655440000 not found or expired"
}
```
**Resolution**: Re-upload file to create new session

#### 2. No File Uploaded
```json
{
  "detail": "No file uploaded"
}
```
**Resolution**: Include file in multipart/form-data request

#### 3. Invalid File Format
```json
{
  "detail": "Unsupported file type. Please upload CSV or Excel (.xlsx, .xls)"
}
```
**Resolution**: Ensure file is CSV or Excel format

#### 4. Mirth Connection Failed
```json
{
  "detail": "Failed to connect to Mirth: Connection refused",
  "mirth_host": "localhost",
  "mirth_port": 6661
}
```
**Resolution**:
- Verify Mirth Connect is running
- Check MIRTH_PORT configuration
- Test with: `telnet localhost 6661`

#### 5. OpenAI API Error
```json
{
  "detail": "OpenAI API rate limit exceeded. Using fallback generator."
}
```
**Resolution**: System automatically uses fallback generator, no action needed

#### 6. CORS Error (Frontend)
```
Access to fetch at 'http://localhost:8000/api/dashboard/stats' from origin
'http://localhost:3000' has been blocked by CORS policy
```
**Resolution**: CORS middleware now configured in v3.0 (lines 205-220)

---

## Testing Guide

### 1. Local Setup Testing

#### Start Backend
```bash
cd actual-code
python main_with_fastapi.py --api

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

#### Test Health Endpoint
```bash
curl http://localhost:8000/health

# Expected:
# {"status":"healthy","message":"Interface Wizard API is running"}
```

#### Test CORS (from Browser Console)
```javascript
fetch('http://localhost:8000/api/dashboard/stats')
  .then(r => r.json())
  .then(d => console.log(d));

// Should succeed without CORS errors
```

### 2. Preview & Confirmation Workflow Testing

#### Step 1: Upload for Preview
```bash
curl -X POST http://localhost:8000/api/upload-preview \
  -F "file=@sample_patients.csv" \
  > preview_response.json

# Extract session_id from response
SESSION_ID=$(cat preview_response.json | jq -r '.session_id')
echo "Session ID: $SESSION_ID"
```

#### Step 2: View Preview (Paginated)
```bash
curl "http://localhost:8000/api/upload/$SESSION_ID/preview?page=1&page_size=5"
```

#### Step 3: Confirm and Process
```bash
# Extract first patient UUID
PATIENT_UUID=$(cat preview_response.json | jq -r '.patients[0].uuid')

curl -X POST http://localhost:8000/api/confirm-upload \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"selected_patient_uuids\": [\"$PATIENT_UUID\"]
  }" > confirm_response.json

# Extract upload_id
UPLOAD_ID=$(cat confirm_response.json | jq -r '.upload_id')
echo "Upload ID: $UPLOAD_ID"
```

#### Step 4: Monitor Progress (SSE)
```bash
# Using curl (basic)
curl -N http://localhost:8000/api/upload/$UPLOAD_ID/stream

# Or use websocat for better SSE handling
websocat -E ws://localhost:8000/api/upload/$UPLOAD_ID/stream
```

#### Step 5: Get Results
```bash
curl http://localhost:8000/api/upload/$UPLOAD_ID/results
```

### 3. Direct Upload Testing (Legacy)

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@sample_patients.csv" \
  -F "trigger_event=A04" \
  > upload_response.json

UPLOAD_ID=$(cat upload_response.json | jq -r '.upload_id')
curl http://localhost:8000/api/upload/$UPLOAD_ID/results
```

### 4. Dashboard Testing

```bash
# Get statistics
curl http://localhost:8000/api/dashboard/stats

# Check system status
curl http://localhost:8000/api/dashboard/system-status
```

### 5. Integration Testing with Mirth

#### Prerequisites
1. Mirth Connect running on port 6661
2. Channel configured with MLLP listener
3. Database connection to OpenEMR

#### Test Flow
```bash
# 1. Upload small CSV file
curl -X POST http://localhost:8000/api/upload-preview \
  -F "file=@test_single_patient.csv" \
  > test_preview.json

# 2. Extract session and patient UUID
SESSION_ID=$(cat test_preview.json | jq -r '.session_id')
PATIENT_UUID=$(cat test_preview.json | jq -r '.patients[0].uuid')

# 3. Confirm processing
curl -X POST http://localhost:8000/api/confirm-upload \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"selected_patient_uuids\": [\"$PATIENT_UUID\"]
  }"

# 4. Check Mirth Admin UI
# - Verify message received
# - Check channel statistics
# - View message in dashboard

# 5. Verify in OpenEMR database
mysql -u openemr -p openemr -e "
  SELECT pid, fname, lname, pubpid, DOB
  FROM patient_data
  ORDER BY pid DESC
  LIMIT 5;
"
```

### 6. Load Testing

```bash
# Generate 100-patient CSV
python generate_test_csv.py --rows 100 --output large_test.csv

# Upload for preview
curl -X POST http://localhost:8000/api/upload-preview \
  -F "file=@large_test.csv" \
  > large_preview.json

# Extract all valid patient UUIDs
cat large_preview.json | jq -r '.patients[] | select(.validation_status == "valid") | .uuid' > valid_uuids.txt

# Create JSON array of UUIDs
UUIDS_JSON=$(cat valid_uuids.txt | jq -R . | jq -s .)

# Confirm all
SESSION_ID=$(cat large_preview.json | jq -r '.session_id')
curl -X POST http://localhost:8000/api/confirm-upload \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"selected_patient_uuids\": $UUIDS_JSON
  }"
```

### 7. Error Scenario Testing

#### Test Session Expiration
```bash
# Upload for preview
curl -X POST http://localhost:8000/api/upload-preview \
  -F "file=@sample_patients.csv" \
  > temp_session.json

SESSION_ID=$(cat temp_session.json | jq -r '.session_id')

# Wait 1 hour (or manually set expiration in code for testing)
# Then try to confirm
curl -X POST http://localhost:8000/api/confirm-upload \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"selected_patient_uuids\": [\"dummy-uuid\"]
  }"

# Expected: 404 Not Found
```

#### Test Invalid Session ID
```bash
curl -X POST http://localhost:8000/api/confirm-upload \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "invalid-uuid-12345",
    "selected_patient_uuids": ["dummy"]
  }'

# Expected: 404 Not Found
```

#### Test Empty Patient List
```bash
SESSION_ID="valid-session-id-here"
curl -X POST http://localhost:8000/api/confirm-upload \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"selected_patient_uuids\": []
  }"

# Expected: 400 Bad Request
```

---

## Troubleshooting

### Issue 1: CORS Errors in Frontend

**Symptom**:
```
Access to fetch at 'http://localhost:8000/api/...' from origin 'http://localhost:3000'
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present
```

**Solution**: ✅ Fixed in v3.0
- CORS middleware now configured (lines 205-220 in main_with_fastapi.py)
- Supports React (3000), Angular (4200), Vite (5173)

**Verification**:
```bash
# Check CORS headers
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     http://localhost:8000/api/dashboard/stats -v

# Look for:
# Access-Control-Allow-Origin: *
# Access-Control-Allow-Methods: *
```

---

### Issue 2: Mirth Connection Refused

**Symptom**:
```json
{"detail": "Failed to connect to Mirth: [Errno 61] Connection refused"}
```

**Diagnosis**:
1. Check Mirth is running:
   ```bash
   ps aux | grep mirth
   # OR
   netstat -an | grep 6661
   ```

2. Verify channel is deployed:
   - Open Mirth Connect Administrator
   - Check channel status (should be green)

3. Test socket connection:
   ```bash
   telnet localhost 6661
   # Should connect without error
   ```

**Solutions**:
- Start Mirth Connect service
- Deploy channel in Mirth Administrator
- Update `MIRTH_PORT` in main_with_fastapi.py if using different port
- Check firewall rules

---

### Issue 3: Session Not Found

**Symptom**:
```json
{"detail": "Session 550e8400-... not found or expired"}
```

**Causes**:
1. Session expired (1 hour timeout)
2. Backend restarted (in-memory storage cleared)
3. Invalid session_id

**Solutions**:
- Re-upload file to create new session
- Implement persistent storage (Redis/database) for production
- Reduce time between preview and confirmation

---

### Issue 4: Invalid Patient Records

**Symptom**:
```json
{
  "validation_status": "invalid",
  "validation_errors": [...]
}
```

**Diagnosis**:
Check `validation_errors` array for Tier 1 issues:
```json
{
  "field": "dob",
  "tier": 1,
  "message": "Invalid date format for DOB"
}
```

**Solutions**:
- **Missing Tier 1 fields**: Add required columns to CSV
- **Invalid DOB format**: Use YYYY-MM-DD, MM/DD/YYYY, or DD-MM-YYYY
- **Invalid Gender**: Use M, F, O, or U
- **Empty MRN**: Ensure unique identifier present

---

### Issue 5: OpenAI API Errors

**Symptom**:
```
Rate limit exceeded for gpt-4o-mini
```

**Behavior**:
- System automatically falls back to rule-based generator
- Processing continues without interruption

**Solutions**:
- Check OpenAI quota: https://platform.openai.com/account/usage
- Upgrade OpenAI plan if needed
- Reduce request frequency
- Fallback generator produces valid HL7 messages

---

### Issue 6: SSE Stream Not Updating

**Symptom**:
EventSource connection established but no messages received

**Diagnosis**:
```javascript
const es = new EventSource('http://localhost:8000/api/upload/xyz/stream');
es.onerror = (err) => console.error('SSE error:', err);
```

**Solutions**:
1. Verify upload_id is correct
2. Check browser console for network errors
3. Ensure processing started (status should be "processing")
4. Check backend logs for exceptions
5. Try closing and reopening EventSource

---

### Issue 7: Database Insertion Fails

**Symptom**:
HL7 message sent to Mirth, but no record in OpenEMR database

**Diagnosis**:
1. Check Mirth channel logs in Administrator UI
2. Verify transformer JavaScript executed
3. Check database connection settings

**Solutions**:
- Review Mirth channel configuration
- Verify database credentials
- Check `patient_data` table schema matches transformer
- Ensure `pid` field calculation correct (`SELECT MAX(pid) + 1`)

---

### Issue 8: Large File Upload Timeout

**Symptom**:
Upload preview fails for files > 1000 rows

**Solutions**:
1. Increase FastAPI timeout:
   ```python
   # In main_with_fastapi.py
   uvicorn.run(app, host="0.0.0.0", port=8000, timeout=300)
   ```

2. Use pagination aggressively:
   ```bash
   curl "http://localhost:8000/api/upload/$SESSION_ID/preview?page=1&page_size=50"
   ```

3. Split large CSV into smaller batches

---

### Issue 9: UUID Not Found in Database

**Symptom**:
Patient created but UUID (ZPI segment) not stored

**Diagnosis**:
- Check if Mirth transformer extracts ZPI segment
- Verify OpenEMR database has custom UUID column

**Solutions**:
1. Add UUID column to `patient_data` table:
   ```sql
   ALTER TABLE patient_data ADD COLUMN uuid VARCHAR(36);
   ```

2. Update Mirth transformer to extract ZPI segment:
   ```javascript
   var zpiSegment = msg['ZPI'];
   if (zpiSegment) {
       var uuid = zpiSegment['ZPI.1']['ZPI.1.1'].toString();
       // Add uuid to INSERT statement
   }
   ```

---

## Appendix

### A. Sample cURL Commands

#### Complete Preview & Confirm Workflow
```bash
#!/bin/bash

# 1. Upload for preview
echo "1. Uploading file for preview..."
PREVIEW_RESP=$(curl -s -X POST http://localhost:8000/api/upload-preview \
  -F "file=@sample_patients.csv")

echo "$PREVIEW_RESP" | jq .

# 2. Extract session and first valid patient
SESSION_ID=$(echo "$PREVIEW_RESP" | jq -r '.session_id')
PATIENT_UUID=$(echo "$PREVIEW_RESP" | jq -r '.patients[] | select(.validation_status == "valid") | .uuid' | head -1)

echo "Session ID: $SESSION_ID"
echo "Patient UUID: $PATIENT_UUID"

# 3. Confirm and process
echo "2. Confirming upload..."
CONFIRM_RESP=$(curl -s -X POST http://localhost:8000/api/confirm-upload \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"selected_patient_uuids\": [\"$PATIENT_UUID\"]
  }")

echo "$CONFIRM_RESP" | jq .

UPLOAD_ID=$(echo "$CONFIRM_RESP" | jq -r '.upload_id')
echo "Upload ID: $UPLOAD_ID"

# 4. Wait for processing (simulate SSE)
echo "3. Waiting for processing..."
sleep 5

# 5. Get results
echo "4. Fetching results..."
curl -s "http://localhost:8000/api/upload/$UPLOAD_ID/results" | jq .
```

### B. Sample Frontend Integration (React)

```javascript
// UploadWithPreview.jsx
import React, { useState } from 'react';

function UploadWithPreview() {
  const [previewData, setPreviewData] = useState(null);
  const [selectedUUIDs, setSelectedUUIDs] = useState([]);
  const [processing, setProcessing] = useState(false);

  const handleFileUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('http://localhost:8000/api/upload-preview', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    setPreviewData(data);

    // Auto-select all valid patients
    const validUUIDs = data.patients
      .filter(p => p.validation_status === 'valid')
      .map(p => p.uuid);
    setSelectedUUIDs(validUUIDs);
  };

  const handleConfirm = async () => {
    setProcessing(true);

    const response = await fetch('http://localhost:8000/api/confirm-upload', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: previewData.session_id,
        selected_patient_uuids: selectedUUIDs,
      }),
    });

    const data = await response.json();

    // Connect to SSE stream
    const eventSource = new EventSource(
      `http://localhost:8000${data.stream_url}`
    );

    eventSource.onmessage = (event) => {
      const progress = JSON.parse(event.data);
      console.log(`Step ${progress.step}: ${progress.message}`);

      if (progress.step === 6) {
        eventSource.close();
        setProcessing(false);
        alert('Upload complete!');
      }
    };
  };

  return (
    <div>
      <input
        type="file"
        accept=".csv,.xlsx,.xls"
        onChange={(e) => handleFileUpload(e.target.files[0])}
      />

      {previewData && (
        <div>
          <h3>Preview: {previewData.total_records} records</h3>
          <p>Valid: {previewData.valid_count}, Invalid: {previewData.invalid_count}</p>

          <table>
            <thead>
              <tr>
                <th>Select</th>
                <th>MRN</th>
                <th>Name</th>
                <th>DOB</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {previewData.patients.map(patient => (
                <tr key={patient.uuid}>
                  <td>
                    <input
                      type="checkbox"
                      checked={selectedUUIDs.includes(patient.uuid)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedUUIDs([...selectedUUIDs, patient.uuid]);
                        } else {
                          setSelectedUUIDs(selectedUUIDs.filter(id => id !== patient.uuid));
                        }
                      }}
                      disabled={patient.validation_status === 'invalid'}
                    />
                  </td>
                  <td>{patient.mrn}</td>
                  <td>{patient.first_name} {patient.last_name}</td>
                  <td>{patient.dob}</td>
                  <td>{patient.validation_status}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <button onClick={handleConfirm} disabled={processing || selectedUUIDs.length === 0}>
            {processing ? 'Processing...' : `Confirm (${selectedUUIDs.length} selected)`}
          </button>
        </div>
      )}
    </div>
  );
}

export default UploadWithPreview;
```

### C. HL7 Message Example (with ZPI Segment)

```
MSH|^~\&|InterfaceWizard|IW|Mirth|Mirth|20251229103000||ADT^A04|MSG20251229103000|P|2.5
EVN|A04|20251229103000
PID|1||MRN001^^^MRN||Doe^John||19800515|M||White|123 Main St^^City^State^12345||555-1234||English|M|||||987-65-4321
PV1|1|O
ZPI|a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Segment Breakdown**:
- **MSH**: Message Header
  - Sending Application: InterfaceWizard
  - Message Type: ADT^A04 (Register Patient)
  - Version: 2.5
- **EVN**: Event Type (A04)
- **PID**: Patient Identification
  - MRN: MRN001
  - Name: Doe^John
  - DOB: 19800515 (YYYYMMDD)
  - Gender: M
  - Address: 123 Main St...
- **PV1**: Patient Visit (outpatient)
- **ZPI**: Custom segment with UUID 🆕

---

## Changelog

### v3.0.0 (2025-12-29)

**New Features**:
- ✅ **CORS Middleware**: Pre-configured for React, Angular, Vite frontends
- ✅ **Preview & Confirmation Workflow**: Two-phase upload process
- ✅ **UUID Tracking**: Each patient record assigned unique identifier
- ✅ **Session Management**: 1-hour expiring sessions with cleanup scheduler
- ✅ **Paginated Preview**: Handle large datasets efficiently
- ✅ **Custom ZPI Segment**: UUID embedded in HL7 messages
- ✅ **New Endpoints**:
  - `POST /api/upload-preview`
  - `POST /api/confirm-upload`
  - `GET /api/upload/{session_id}/preview`

**Improvements**:
- Enhanced column mapping with more aliases
- Better error messages with tier information
- Automatic fallback to rule-based HL7 generator

**Bug Fixes**:
- Fixed CORS blocking frontend requests
- Improved date parsing for multiple formats
- Better gender normalization

### v2.0.0 (Previous Release)
- Initial FastAPI implementation
- CSV/Excel upload support
- Real-time SSE progress
- Dashboard statistics
- Mirth MLLP integration
- OpenAI GPT-4o-mini integration

---

## Support & Contact

**Project Repository**: https://github.com/Shirishag1911/interface-wizard

**Author**: Shirisha G
**Email**: shirisha.g1911@gmail.com

**Documentation**:
- **This File**: IW-Backend-API-Documentation-v3.0.md
- **Previous Version**: IW-API-Documentation-v2.0.pdf
- **CLAUDE.md**: Project instructions for AI assistance

**Related Documentation**:
- `CSV_UPLOAD_GUIDE.md` - CSV format specification
- `docs/BACKEND_MIRTH_INTEGRATION.md` - Mirth setup guide
- `docs/QUICK_REFERENCE.md` - Quick command reference

---

## License

Proprietary - All Rights Reserved

---

**End of Documentation**

*Last Updated: December 29, 2025*
*Document Version: 3.0.0*
*Backend Version: 2.0.0*
*Generated for Interface Wizard - Smart HL7 Message Generator*
