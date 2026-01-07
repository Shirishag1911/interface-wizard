# Interface Wizard Backend API Documentation

**Version:** 4.0
**Last Updated:** January 7, 2026
**Backend Framework:** FastAPI 0.109+
**Base URL:** `http://localhost:8000`

---

## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Technology Stack](#technology-stack)
4. [Quick Start](#quick-start)
5. [Understanding HL7 ADT Messages](#understanding-hl7-adt-messages)
6. [Intelligent Column Mapping](#intelligent-column-mapping)
7. [API Endpoints Reference](#api-endpoints-reference)
8. [Complete End-to-End Examples](#complete-end-to-end-examples)
9. [Data Models](#data-models)
10. [CSV/Excel File Format](#csvexcel-file-format)
11. [Error Handling](#error-handling)
12. [Testing & Troubleshooting](#testing--troubleshooting)

---

## Overview

**Interface Wizard** is a healthcare integration platform that converts patient data from CSV/Excel files into HL7 v2.5 ADT (Admit/Discharge/Transfer) messages and transmits them to Electronic Health Record (EHR) systems via Mirth Connect using the MLLP (Minimal Lower Layer Protocol).

### What Problems Does It Solve?

1. **Bulk Patient Registration**: Process hundreds or thousands of patient records from spreadsheets
2. **System Migration**: Transfer patient data between healthcare systems
3. **Data Integration**: Connect non-HL7 systems with HL7-compliant EHRs
4. **Testing & Training**: Generate realistic HL7 messages for integration testing

### How It Works (Simple Flow)

```
1. Upload CSV/Excel → 2. AI Analyzes Columns → 3. Preview Data → 4. Generate HL7 → 5. Send to Mirth → 6. Download Messages
```

**Detailed Flow:**

```
┌─────────────────┐
│ User uploads    │
│ patients.csv    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Backend API (FastAPI)               │
│ ┌─────────────────────────────────┐ │
│ │ 1. Parse CSV/Excel              │ │
│ │ 2. AI Column Mapping (OpenAI)   │ │
│ │ 3. Validate All Records         │ │
│ │ 4. Return Preview + Session ID  │ │
│ └─────────────────────────────────┘ │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────┐
│ User Reviews    │
│ Preview Table   │
│ Selects Patients│
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Backend API (FastAPI)               │
│ ┌─────────────────────────────────┐ │
│ │ 5. Generate HL7 ADT Messages    │ │
│ │    (Programmatic Builder)       │ │
│ │ 6. Send to Mirth via MLLP       │ │
│ │ 7. Stream Real-Time Progress    │ │
│ │ 8. Store Generated Messages     │ │
│ └─────────────────────────────────┘ │
└────────┬────────────────────────────┘
         │ MLLP (port 6661)
         ▼
┌─────────────────────────────────────┐
│ Mirth Connect                       │
│ ┌─────────────────────────────────┐ │
│ │ 9. Parse HL7 Message            │ │
│ │ 10. Extract Patient Data        │ │
│ │ 11. Insert into Database        │ │
│ │ 12. Send ACK Response           │ │
│ └─────────────────────────────────┘ │
└────────┬────────────────────────────┘
         │ SQL INSERT
         ▼
┌─────────────────┐
│ OpenEMR MySQL   │
│ patient_data    │
└─────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ User Downloads HL7 Messages         │
│ ┌─────────────────────────────────┐ │
│ │ • Preview messages              │ │
│ │ • Download as ZIP (browser)     │ │
│ │ • Copy to clipboard             │ │
│ │ • Export metadata               │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

## Key Features

### 1. Intelligent Column Mapping (AI-Powered)

**Two Strategies**:
1. **OpenAI GPT-4o-mini** (Primary) - True AI understanding
2. **Fuzzy Matching** (Fallback) - Rule-based keyword detection

**Example Mappings**:

| Your Column Name | Detected As | Confidence | How? |
|-----------------|-------------|------------|------|
| `Patient Last Name` | `lastName` | 100% | AI semantic understanding |
| `Pateint First Name` | `firstName` | 98% | AI detects typo |
| `Email Address` | `email` | 100% | AI keyword matching |
| `Phone #` | `phone` | 95% | AI symbol understanding |
| `DOB` | `dateOfBirth` | 100% | AI abbreviation knowledge |

**Benefits:**
- Handles unlimited column name variations
- Typo tolerant - AI understands "Pateint" means "Patient"
- Context aware - Distinguishes "Full Name" vs "Last Name"
- Confidence scores show certainty of mapping
- Automatic fallback to fuzzy matching if AI unavailable

See [Intelligent Column Mapping](#intelligent-column-mapping) for details.

### 2. Programmatic HL7 Generation

Fast, deterministic HL7 v2.5 message builder:
- **Fast**: <10ms per patient (no AI needed for message generation)
- **Reliable**: 100% spec-compliant HL7 messages
- **Cost-effective**: No API costs for HL7 generation
- **Comprehensive**: Supports all ADT message types (A01, A04, A08, A28, A31)

### 3. Flexible HL7 Message Types

**All ADT (Admit/Discharge/Transfer) trigger events supported:**

| Trigger Event | Description | Patient Class | Use Case |
|--------------|-------------|---------------|----------|
| **ADT^A01** | Admit/Visit Notification | Inpatient (I) | Hospital admission |
| **ADT^A04** | Register Patient | Outpatient (O) | **Default - Most Common** |
| **ADT^A08** | Update Patient Info | Inpatient (I) | Update existing patient |
| **ADT^A28** | Add Person Information | Outpatient (O) | New patient registration |
| **ADT^A31** | Update Person Info | Outpatient (O) | Update existing person |

**Why ADT-A04 is Default:**
- Most commonly used for bulk patient registration
- Works for outpatient registration (most use cases)
- Compatible with most EHR systems
- Simpler than A01 (no admission details needed)

See [Understanding HL7 ADT Messages](#understanding-hl7-adt-messages) for details.

### 4. Two-Phase Workflow

Preview before processing:
```
Phase 1: Upload → Parse → Validate → Preview (user reviews data)
Phase 2: Confirm → Generate HL7 → Send to Mirth (user confirms)
```

**Benefits:**
- User can review parsed data before sending
- Can deselect invalid patients
- Prevents accidental data submission
- Shows validation errors upfront

### 5. Real-Time Progress Tracking

Uses Server-Sent Events (SSE) to stream live updates:
```
Step 1: Initializing... (0%)
Step 2: Generating HL7 messages (1/10)... (20%)
Step 3: Generating HL7 messages (2/10)... (30%)
Step 4: Sending to Mirth (1/10)... (50%)
...
Step 6: Complete! (100%)
```

### 6. Multi-Format Support

**Supported File Types:**
- CSV (.csv)
- Excel (.xlsx, .xls)
- Tab-separated values (.tsv)

**Supported Date Formats:**
- `YYYY-MM-DD` (ISO 8601) - **Recommended**
- `MM/DD/YYYY` (US format)
- `DD-MM-YYYY` (European format)
- `YYYY/MM/DD`
- `DD/MM/YYYY`
- `MM-DD-YYYY`

### 7. 3-Tier Data Validation

**Tier 1 (Critical)** - Must have:
- MRN (Medical Record Number)
- First Name
- Last Name
- Date of Birth
- Gender

**Tier 2 (Important)** - Should have:
- Phone
- Email
- Address

**Tier 3 (Optional)** - Nice to have:
- City, State, ZIP
- Race, Ethnicity
- Language, SSN

**Validation Output:**
```json
{
  "validation_status": "invalid",
  "validation_messages": [
    "Missing required field: firstName (Tier 1 - Critical)",
    "Invalid date format for DOB: '15/05/1980' (Tier 1 - Critical)"
  ]
}
```

### 8. UUID Tracking

Every patient record gets a unique UUID (v4) for tracking:
```
Patient: John Doe (MRN: MRN001)
UUID: a1b2c3d4-e5f6-7890-abcd-ef1234567890

 HL7 Message includes custom ZPI segment:
ZPI|a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Benefits:**
- Track specific patient records across systems
- Correlate upload batch with database records
- Debugging and audit trails
- Prevent duplicate processing

### 9. HL7 Message Download & Export

**JSON-Based Download**:
- Returns structured JSON with all generated HL7 messages
- Each message includes: MRN, patient name, trigger event, full HL7 content, suggested filename

**UI Capabilities**:
- **Preview** - Display messages before download
- **Individual Download** - Download specific messages
- **ZIP Archive** - Create ZIP in browser (no backend needed)
- **Clipboard Copy** - Quick copy for testing
- **Metadata Export** - CSV export for tracking

---

## Technology Stack

### Backend Components

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | 0.109+ | REST API server with auto-docs |
| **Language** | Python | 3.9+ | Backend implementation |
| **HL7 Library** | python-hl7 | 0.4.5 | HL7 message parsing/validation |
| **AI Engine** | OpenAI API | GPT-4o-mini | Column mapping intelligence |
| **Data Processing** | pandas | 2.1+ | CSV/Excel parsing |
| **Async Runtime** | asyncio | Built-in | Background task processing |
| **ASGI Server** | uvicorn | 0.27+ | Production-ready server |

### Integration Stack

| Component | Technology | Port | Purpose |
|-----------|-----------|------|---------|
| **Mirth Connect** | v4.x | 6661 (MLLP) | HL7 routing & transformation |
| **OpenEMR** | v7.x | 80 (HTTP) | Target EHR system |
| **MySQL** | 8.0+ | 3306 | Patient data storage |

### Frontend Libraries (for Download Feature)

| Library | Purpose | Installation |
|---------|---------|--------------|
| **JSZip** | Create ZIP files in browser | `npm install jszip` |
| **file-saver** | Trigger file downloads easily | `npm install file-saver` |
| **papaparse** | CSV parsing/generation | `npm install papaparse` |

### Why These Technologies?

**FastAPI**:
- Automatic OpenAPI documentation (Swagger UI)
- Built-in data validation (Pydantic)
- Async support for SSE streaming
- High performance

**OpenAI GPT-4o-mini**:
- Fast inference (<1 second)
- Accurate semantic understanding
- Cost-effective ($0.150 per 1M tokens)
- Can handle any column name variation

**Programmatic HL7 Builder**:
- No AI needed for message generation
- Deterministic output
- HL7 v2.5 spec-compliant
- Supports all ADT message types

**Browser-Based ZIP Creation**:
- No server-side processing needed
- Faster for users (no upload/download cycle)
- Reduces server load
- UI team has full control

---

## Quick Start

### Prerequisites

1. **Python 3.9+** installed
2. **Mirth Connect** running on port 6661
3. **OpenAI API Key** (optional - fallback available)
4. **MySQL/OpenEMR** database (optional for testing)

### Installation

```bash
# 1. Navigate to project directory
cd interface-wizard/actual-code

# 2. Install dependencies
pip install -r requirements.txt

# This installs:
# - fastapi==0.109.0
# - uvicorn[standard]==0.27.0
# - pandas==2.1.4
# - openpyxl==3.1.2
# - hl7==0.4.5
# - openai>=1.0.0
# - python-multipart==0.0.6
```

### Configuration

Edit `main_with_fastapi.py` (lines 47-59):

```python
# ==================== CONFIGURATION ====================
# LLM Configuration for Column Mapping
USE_OLLAMA_CLOUD = False  # Set to True for free Ollama Cloud (if not blocked)
OLLAMA_API_KEY = "21fd147c52c4460e8083c9a660e2c158._3CZGjnMdm-00AnCwvnOe9Bx"
OLLAMA_BASE_URL = "https://cloud.ollama.ai/v1"
OLLAMA_MODEL = "glm4:latest"

# OpenAI Configuration (Currently Active)
OPENAI_API_KEY = "sk-your-actual-key-here"  # TODO: Replace with your key

# Mirth Connect Configuration
MIRTH_HOST = "localhost"
MIRTH_PORT = 6661
```

**Important**: Replace `OPENAI_API_KEY` with your actual OpenAI API key if you want AI column mapping.

### Running the Server

```bash
# Start server
python main_with_fastapi.py --api

# Output:
# INFO:     Started server process [12345]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Server URLs:**
- API Base: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

### Verify Installation

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","message":"Interface Wizard API is running"}
```

---

## Understanding HL7 ADT Messages

### What is HL7?

**HL7 (Health Level 7)** is the international standard for healthcare data exchange. Think of it as the "language" that different healthcare systems use to communicate.

**ADT (Admit/Discharge/Transfer)** messages specifically handle patient registration, admission, discharge, and demographic updates.

### HL7 v2.5 Message Structure

An HL7 message consists of **segments** (rows), each with **fields** separated by pipes (`|`):

```
MSH|^~\&|InterfaceWizard|FACILITY|OpenEMR|HOSPITAL|20260107120000||ADT^A04|MSG001|P|2.5
EVN|A04|20260107120000
PID|1||MRN001^^^MRN||Doe^John||19800515|M|||123 Main St^City^State^12345||555-1234|||||||||||||||
ZPI|a1b2c3d4-e5f6-7890-abcd-ef1234567890
PV1|1|O|||||||||||||||||||||||||||||||||||||||||20260107120000
```

**Segment Breakdown:**

| Segment | Name | Purpose | Required? |
|---------|------|---------|-----------|
| `MSH` | Message Header | Identifies sender, receiver, message type | ✅ Yes |
| `EVN` | Event Type | Event code and timestamp | ✅ Yes |
| `PID` | Patient Identification | Patient demographics (name, DOB, gender, etc.) | ✅ Yes |
| `ZPI` | Custom UUID Segment | Unique tracking ID (Interface Wizard specific) | ⚠️ Custom |
| `PV1` | Patient Visit | Visit information (patient class, location, etc.) | ✅ Yes |

### MSH Segment (Message Header)

```
MSH|^~\&|InterfaceWizard|FACILITY|OpenEMR|HOSPITAL|20260107120000||ADT^A04|MSG001|P|2.5
```

| Field | Value | Meaning |
|-------|-------|---------|
| MSH-1 | `|` | Field separator |
| MSH-2 | `^~\&` | Encoding characters |
| MSH-3 | `InterfaceWizard` | Sending application |
| MSH-4 | `FACILITY` | Sending facility |
| MSH-5 | `OpenEMR` | Receiving application |
| MSH-6 | `HOSPITAL` | Receiving facility |
| MSH-7 | `20260107120000` | Message timestamp (YYYYMMDDHHmmss) |
| MSH-9 | `ADT^A04` | Message type (ADT) and trigger event (A04) |
| MSH-10 | `MSG001` | Unique message control ID |
| MSH-11 | `P` | Processing ID (P = Production) |
| MSH-12 | `2.5` | HL7 version |

### EVN Segment (Event Type)

```
EVN|A04|20260107120000
```

| Field | Value | Meaning |
|-------|-------|---------|
| EVN-1 | `A04` | Event type code (Register Patient) |
| EVN-2 | `20260107120000` | Event occurred timestamp |

### PID Segment (Patient Identification)

```
PID|1||MRN001^^^MRN||Doe^John||19800515|M|||123 Main St^City^State^12345||555-1234|||||||||||||||
```

| Field | Value | Meaning |
|-------|-------|---------|
| PID-1 | `1` | Set ID (sequence number) |
| PID-3 | `MRN001^^^MRN` | Patient identifier (MRN) |
| PID-5 | `Doe^John` | Patient name (Last^First) |
| PID-7 | `19800515` | Date of birth (YYYYMMDD) |
| PID-8 | `M` | Gender (M/F/O/U) |
| PID-11 | `123 Main St^City^State^12345` | Address |
| PID-13 | `555-1234` | Phone number |

### PV1 Segment (Patient Visit)

```
PV1|1|O|||||||||||||||||||||||||||||||||||||||||20260107120000
```

| Field | Value | Meaning |
|-------|-------|---------|
| PV1-1 | `1` | Set ID |
| PV1-2 | `O` | Patient class (O=Outpatient, I=Inpatient, E=Emergency) |
| PV1-44 | `20260107120000` | Admit timestamp |

### ADT Trigger Event Types Explained

#### ADT^A01 - Admit/Visit Notification

**Purpose**: Notify systems of patient admission to hospital (inpatient)

**When to Use**:
- Patient is being admitted to hospital
- Creating inpatient record
- Requires admission details (attending doctor, room, etc.)

**Patient Class**: `I` (Inpatient)

**Example Use Case**:
```
Patient "John Doe" is admitted to hospital for surgery
→ Send ADT^A01 message
→ Creates inpatient record in OpenEMR
```

#### ADT^A04 - Register Patient (DEFAULT)

**Purpose**: Register a patient (typically outpatient)

**When to Use**:
- Bulk patient registration
- Creating new patient records
- Outpatient registration
- Most common for CSV uploads

**Patient Class**: `O` (Outpatient)

**Why Default**:
- Simple - no admission details needed
- Works for most use cases
- Widely supported by EHR systems
- Perfect for bulk imports

**Example Use Case**:
```
Import 100 patients from Excel file
→ Send ADT^A04 for each patient
→ Creates outpatient records in OpenEMR
```

#### ADT^A08 - Update Patient Information

**Purpose**: Update existing patient demographic information

**When to Use**:
- Patient changed address
- Phone number updated
- Name correction needed

**Patient Class**: `I` (Inpatient)

**Example Use Case**:
```
Patient "John Doe" moved to new address
→ Send ADT^A08 message with updated address
→ Updates existing record in OpenEMR
```

#### ADT^A28 - Add Person Information

**Purpose**: Add a new person (may not be a patient yet)

**When to Use**:
- Pre-registration
- Adding guarantor or next-of-kin
- Creating person before patient status

**Patient Class**: `O` (Outpatient)

**Example Use Case**:
```
Pre-register patient before appointment
→ Send ADT^A28 message
→ Creates person record in OpenEMR
```

#### ADT^A31 - Update Person Information

**Purpose**: Update existing person demographic information

**When to Use**:
- Update pre-registered person details
- Modify guarantor information

**Patient Class**: `O` (Outpatient)

### Choosing the Right Trigger Event

**Decision Tree:**

```
Are you bulk uploading new patients from CSV?
  ├─ YES → Use ADT^A04 (Register Patient) ✅ DEFAULT
  └─ NO
      ├─ Admitting patient to hospital?
      │   └─ YES → Use ADT^A01 (Admit)
      ├─ Updating existing patient?
      │   └─ YES → Use ADT^A08 (Update Patient)
      ├─ Pre-registering person?
      │   └─ YES → Use ADT^A28 (Add Person)
      └─ Updating person info?
          └─ YES → Use ADT^A31 (Update Person)
```

**For 99% of CSV uploads → Use ADT^A04**

---

## Intelligent Column Mapping

### The Problem

CSV/Excel files from different sources have inconsistent column names:

```
File 1: "First Name", "Last Name", "DOB"
File 2: "Patient First Name", "Patient Last Name", "Date of Birth"
File 3: "fname", "lname", "birthdate"
File 4: "Pateint First Name" (typo!), "Patient Surname", "Birth Date"
```

**Old Approach (Hardcoding)**:
```python
COLUMN_MAPPINGS = {
    "firstName": ["first_name", "fname", "first name", "patient first name",
                  "given name", "given_name", "firstname", "first", ...]
}
# Would need hundreds of variations!
```

**Problem**: Impossible to predict every variation, typos, or custom formats.

### The Solution: Two-Strategy Approach

#### Strategy 1: AI-Powered Mapping (Primary)

**How It Works:**

1. Extract all column names from CSV
2. Send to OpenAI GPT-4o-mini with context
3. AI analyzes semantics and returns mapping
4. System validates and applies mapping

**Example Request to AI:**

```json
{
  "model": "gpt-4o-mini",
  "messages": [
    {
      "role": "system",
      "content": "You are a healthcare data mapping expert. Map CSV columns to standard fields."
    },
    {
      "role": "user",
      "content": "Map these columns to standard healthcare fields:\n['Patient Last Name', 'Pateint First Name', 'Email Address', 'Phone Number', 'DOB']\n\nStandard fields: mrn, firstName, lastName, dateOfBirth, gender, phone, email, address, city, state, zip"
    }
  ]
}
```

**AI Response:**

```json
{
  "mappings": [
    {
      "column": "Patient Last Name",
      "field": "lastName",
      "confidence": 1.0,
      "reasoning": "Exact semantic match"
    },
    {
      "column": "Pateint First Name",
      "field": "firstName",
      "confidence": 0.98,
      "reasoning": "Typo detected in 'Pateint', should be 'Patient'"
    },
    {
      "column": "Email Address",
      "field": "email",
      "confidence": 1.0,
      "reasoning": "Standard email field"
    },
    {
      "column": "Phone Number",
      "field": "phone",
      "confidence": 1.0,
      "reasoning": "Standard phone field"
    },
    {
      "column": "DOB",
      "field": "dateOfBirth",
      "confidence": 1.0,
      "reasoning": "Common abbreviation for Date of Birth"
    }
  ],
  "warnings": [
    "Detected typo in column 'Pateint First Name' - likely meant 'Patient First Name'"
  ],
  "unmapped": []
}
```

**Advantages:**

- **Unlimited Variations**: Works with ANY reasonable column name
- **Typo Tolerance**: AI understands "Pateint" = "Patient"
- **Context Awareness**: Distinguishes "Full Name" vs "Last Name"
- **Multi-Language**: Can understand non-English column names
- **Confidence Scores**: Shows certainty of mapping
- **Warnings**: Flags ambiguous or unusual mappings
- **Self-Improving**: Gets better as AI models improve

**Cost**: ~$0.0001 per file (very cheap)

#### Strategy 2: Fuzzy Matching (Fallback)

**How It Works:**

1. Normalize column name (lowercase, remove special chars)
2. Extract meaningful keywords (remove noise words)
3. Match keywords against predefined field mappings

**Noise Words Removed:**
- "patient", "person", "record", "data", "info", "information"
- "field", "column", "value", "the", "a", "an"

**Field Keywords:**

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

**Example Matching Process:**

Input: `"Patient Last Name"`

1. **Normalize**: `"patient last name"` (lowercase)
2. **Split**: `["patient", "last", "name"]` (split by spaces)
3. **Remove Noise**: `["last", "name"]` (remove "patient")
4. **Match Keywords**: Find "last" in keywords → matches `lastName` ✅

**Example Mappings:**

| Your Column Name | Detected As | How Matched |
|-----------------|-------------|-------------|
| `Patient First Name` | `firstName` | Keyword: "first" |
| `Pateint First Name` | `firstName` | Substring match (typo) |
| `Email Address` | `email` | Keyword: "email" |
| `Phone #` | `phone` | Keyword: "phone" |
| `Zipcode` | `zip` | Substring: "zip" |
| `Medical Record Number` | `mrn` | Exact match (predefined) |

**Advantages:**

- **No API Costs**: Completely free
- **Fast**: <1ms per column
- **Offline**: Works without internet
- **Predictable**: Deterministic results

**Limitations:**

- Less flexible than AI
- Can't handle complex variations
- Limited to predefined keywords

### When Each Strategy is Used

**AI Mapping (Primary)**:
- Used when `use_llm_mapping=true` (default)
- Requires valid OpenAI API key
- Automatically falls back to fuzzy matching if fails

**Fuzzy Matching (Fallback)**:
- Used when `use_llm_mapping=false`
- Used when OpenAI API key not configured
- Used when AI mapping fails (network error, rate limit, etc.)

**Example API Usage:**

```bash
# Use AI mapping (default)
curl -X POST http://localhost:8000/api/upload \
  -F "file=@patients.csv" \
  -F "use_llm_mapping=true"

# Use fuzzy matching only
curl -X POST http://localhost:8000/api/upload \
  -F "file=@patients.csv" \
  -F "use_llm_mapping=false"
```

### Column Mapping Response

**Successful Mapping:**

```json
{
  "column_mapping": {
    "Patient Last Name": "lastName",
    "Pateint First Name": "firstName",
    "Email Address": "email",
    "Phone Number": "phone",
    "DOB": "dateOfBirth",
    "Gender": "gender",
    "MRN": "mrn"
  },
  "mapping_confidence": {
    "Patient Last Name": 1.0,
    "Pateint First Name": 0.98,
    "Email Address": 1.0,
    "Phone Number": 1.0,
    "DOB": 1.0,
    "Gender": 1.0,
    "MRN": 1.0
  },
  "mapping_warnings": [
    "Detected typo in 'Pateint First Name' - mapped to firstName with 98% confidence"
  ]
}
```

**Unmapped Columns:**

```json
{
  "column_mapping": {
    "First Name": "firstName",
    "Last Name": "lastName"
  },
  "unmapped_columns": [
    "Unknown Column 1",
    "Random Data"
  ]
}
```

**What Happens to Unmapped Columns?**
- They are ignored during patient record creation
- No validation errors generated
- Logged for user awareness

---

## API Endpoints Reference

### Overview

| Method | Endpoint | Purpose | Phase |
|--------|----------|---------|-------|
| POST | `/api/upload` | Upload file, get preview | Phase 1 |
| POST | `/api/upload/confirm` | Process selected patients | Phase 2 |
| GET | `/api/upload/{id}/stream` | Real-time progress (SSE) | Phase 2 |
| GET | `/api/upload/{id}/results` | Get final results | Phase 2 |
| GET | `/api/upload/{id}/download` | Download HL7 messages | Phase 2 |
| GET | `/api/dashboard/stats` | Dashboard statistics | - |
| GET | `/health` | Basic health check | - |

---

### 1. POST /api/upload

**Purpose**: Upload CSV/Excel file and get preview of all parsed patient records.

**Phase**: 1 (Upload & Preview)

**Request**:

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@patients.csv" \
  -F "trigger_event=ADT-A04" \
  -F "use_llm_mapping=true"
```

**Request Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file` | File | ✅ Yes | - | CSV or Excel file (.csv, .xlsx, .xls) |
| `trigger_event` | string | ❌ No | `ADT-A04` | HL7 trigger event (A01, A04, A08, A28, A31) |
| `use_llm_mapping` | boolean | ❌ No | `true` | Use AI for column mapping (true) or fuzzy matching (false) |

**Response** (200 OK):

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "file_name": "patients.csv",
  "file_type": "csv",
  "total_records": 3,
  "valid_records": 2,
  "invalid_records": 1,
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
      "address": "123 Main St",
      "city": "Springfield",
      "state": "IL",
      "zip": "62701",
      "validation_status": "valid",
      "validation_messages": []
    }
  ],
  "column_mapping": {
    "Patient Last Name": "lastName",
    "Pateint First Name": "firstName",
    "Email Address": "email",
    "Phone Number": "phone",
    "DOB": "dateOfBirth",
    "Gender": "gender",
    "MRN": "mrn"
  },
  "mapping_method": "llm",
  "mapping_confidence": {
    "Patient Last Name": 1.0,
    "Pateint First Name": 0.98
  },
  "expires_at": "2026-01-07T13:30:00Z",
  "timestamp": "2026-01-07T12:30:00Z"
}
```

**Status Codes**:

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | File processed successfully |
| 400 | Bad Request | No file uploaded, invalid file format |
| 500 | Internal Server Error | Processing error, AI error |

---

### 2. POST /api/upload/confirm

**Purpose**: Confirm patient selection and start HL7 generation + Mirth transmission.

**Phase**: 2 (Confirm & Process)

**Request**:

```bash
curl -X POST http://localhost:8000/api/upload/confirm \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "selected_indices": [0, 1],
    "send_to_mirth": true
  }'
```

**Request Body**:

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "selected_indices": [0, 1],
  "send_to_mirth": true
}
```

**Request Fields**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `session_id` | string (UUID) | ✅ Yes | - | Session ID from `/api/upload` response |
| `selected_indices` | array[int] | ❌ No | `[]` | Patient indices to process (empty = all valid) |
| `send_to_mirth` | boolean | ❌ No | `true` | Actually send to Mirth (false = dry run, testing only) |

**Response** (200 OK):

```json
{
  "upload_id": "upload_1735559400_abc123",
  "status": "processing",
  "total_selected": 2,
  "message": "Processing 2 patient(s)",
  "stream_url": "/api/upload/upload_1735559400_abc123/stream"
}
```

**Status Codes**:

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Processing started successfully |
| 400 | Bad Request | Invalid session_id, no patients selected |
| 404 | Not Found | Session not found or expired (>1 hour old) |
| 500 | Internal Server Error | Processing error |

---

### 3. GET /api/upload/{upload_id}/stream

**Purpose**: Monitor real-time processing progress via Server-Sent Events (SSE).

**Phase**: 2 (Processing)

**Request**:

```javascript
// Browser (JavaScript)
const uploadId = "upload_1735559400_abc123";

const eventSource = new EventSource(
  `http://localhost:8000/api/upload/${uploadId}/stream`
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);

  console.log(`Step ${data.step}: ${data.message}`);
  console.log(`Progress: ${data.progress}%`);

  if (data.status === 'completed' || data.status === 'failed') {
    eventSource.close();
  }
};
```

**Response Stream**:

```
data: {"step":1,"message":"Initializing processing...","progress":0,"status":"processing"}

data: {"step":2,"message":"Generating HL7 messages (1/2)","progress":20,"status":"processing"}

data: {"step":6,"message":"Complete: 2 processed, 2 success, 0 failed","progress":100,"status":"completed"}
```

**Event Data Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `step` | integer | Current processing step (1-6) |
| `message` | string | Human-readable progress message |
| `progress` | integer | Progress percentage (0-100) |
| `status` | string | "processing", "completed", or "failed" |

---

### 4. GET /api/upload/{upload_id}/results

**Purpose**: Retrieve final processing results after completion.

**Phase**: 2 (After Processing)

**Request**:

```bash
curl http://localhost:8000/api/upload/upload_1735559400_abc123/results
```

**Response** (200 OK):

```json
{
  "upload_id": "upload_1735559400_abc123",
  "status": "completed",
  "total_processed": 2,
  "successful": 2,
  "failed": 0,
  "processing_time_seconds": 0.45,
  "results": [
    {
      "patient": "John Doe (MRN: MRN001)",
      "hl7_message": "MSH|^~\\&|InterfaceWizard|...",
      "mirth_ack": "MSH|^~\\&|Mirth|...|ACK|...\nMSA|AA|MSG001",
      "status": "success",
      "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    }
  ]
}
```

**Status Codes**:

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Results retrieved successfully |
| 404 | Not Found | Upload ID doesn't exist |
| 202 | Accepted | Processing still in progress (not ready yet) |

---

### 5. GET /api/upload/{upload_id}/download

**Purpose**: Download all generated HL7 messages as JSON for preview, download, or export.

**Phase**: 2 (After Processing)

**Request**:

```bash
curl http://localhost:8000/api/upload/662d9ed4-0c10-4417-bec6-1d1416755cc0/download
```

**Request Parameters**:

| Parameter | Type | Location | Required | Description |
|-----------|------|----------|----------|-------------|
| `upload_id` | string (UUID) | path | ✅ Yes | Upload session ID from `/api/upload/confirm` response |

**Response** (200 OK):

```json
{
  "upload_id": "662d9ed4-0c10-4417-bec6-1d1416755cc0",
  "total_messages": 10,
  "messages": [
    {
      "mrn": "MRN001",
      "trigger_event": "ADT^A04",
      "patient_name": "Doe^John",
      "hl7_message": "MSH|^~\\&|InterfaceWizard|FACILITY|OpenEMR|HOSPITAL|20260107072241||ADT^A04|MSG001|P|2.5\nEVN|A04|20260107072241\nPID|1||MRN001^^^MRN||Doe^John||19800515|M|||123 Main St^Springfield^IL^62701||555-1234\nZPI|a1b2c3d4-e5f6-7890-abcd-ef1234567890\nPV1|1|O|||||||||||||||||||||||||||||||||||||||||20260107072241",
      "suggested_filename": "MRN001_ADT_A04.hl7"
    },
    {
      "mrn": "MRN002",
      "trigger_event": "ADT^A04",
      "patient_name": "Smith^Jane",
      "hl7_message": "MSH|^~\\&|InterfaceWizard|FACILITY|OpenEMR|HOSPITAL|20260107072241||ADT^A04|MSG002|P|2.5\nEVN|A04|20260107072241\nPID|1||MRN002^^^MRN||Smith^Jane||19900820|F|||^Springfield^IL^||555-5678\nZPI|b2c3d4e5-f6a7-8901-bcde-f12345678901\nPV1|1|O|||||||||||||||||||||||||||||||||||||||||20260107072241",
      "suggested_filename": "MRN002_ADT_A04.hl7"
    }
  ]
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `upload_id` | string | The upload session ID |
| `total_messages` | integer | Number of HL7 messages in this upload |
| `messages` | array | Array of message objects (see below) |

**Message Object Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `mrn` | string | Patient Medical Record Number |
| `trigger_event` | string | HL7 trigger event (e.g., "ADT^A04") |
| `patient_name` | string | Patient name in HL7 format (Last^First) |
| `hl7_message` | string | Complete HL7 v2.5 message (with `\n` for line breaks) |
| `suggested_filename` | string | Recommended filename for download (e.g., "MRN001_ADT_A04.hl7") |

**Error Responses**:

**404 - Upload Not Found:**
```json
{
  "detail": "Upload session not found"
}
```

**404 - No Messages:**
```json
{
  "detail": "No HL7 messages found for this upload"
}
```

**Status Codes**:

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Messages retrieved successfully |
| 404 | Not Found | Upload ID doesn't exist or no messages available |
| 500 | Internal Server Error | Retrieval error |

---

### 6. GET /api/dashboard/stats

**Purpose**: Retrieve aggregated statistics across all uploads.

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

### 7. GET /health

**Purpose**: Basic server health check.

**Request**:

```bash
curl http://localhost:8000/health
```

**Response** (200 OK):

```json
{
  "status": "healthy",
  "message": "Interface Wizard API is running"
}
```

---

## UI Implementation Guide for Download Endpoint

### Overview

The download endpoint returns **JSON** instead of a binary file, giving the UI team complete flexibility to:
- Preview messages in modals
- Download as individual files
- Create ZIP archives in the browser
- Copy to clipboard
- Display in tables
- Export metadata

### 1. Preview Modal Component

Display HL7 messages in a modal with syntax highlighting.

**Component**: `HL7PreviewModal.tsx`

```typescript
import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Copy, Download } from 'lucide-react';
import { toast } from 'sonner';

interface HL7Message {
  mrn: string;
  trigger_event: string;
  patient_name: string;
  hl7_message: string;
  suggested_filename: string;
}

interface HL7PreviewModalProps {
  uploadId: string;
  isOpen: boolean;
  onClose: () => void;
}

export function HL7PreviewModal({ uploadId, isOpen, onClose }: HL7PreviewModalProps) {
  const [messages, setMessages] = useState<HL7Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedMessage, setSelectedMessage] = useState<HL7Message | null>(null);

  useEffect(() => {
    if (isOpen && uploadId) {
      loadMessages();
    }
  }, [isOpen, uploadId]);

  const loadMessages = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/upload/${uploadId}/download`
      );

      if (!response.ok) throw new Error('Failed to load messages');

      const data = await response.json();
      setMessages(data.messages);
      if (data.messages.length > 0) {
        setSelectedMessage(data.messages[0]);
      }
    } catch (error) {
      toast.error('Failed to load HL7 messages');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (selectedMessage) {
      navigator.clipboard.writeText(selectedMessage.hl7_message);
      toast.success('HL7 message copied to clipboard!');
    }
  };

  const downloadSingleFile = () => {
    if (selectedMessage) {
      const blob = new Blob([selectedMessage.hl7_message], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = selectedMessage.suggested_filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      toast.success('HL7 message downloaded!');
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle>HL7 Messages Preview</DialogTitle>
        </DialogHeader>

        {loading ? (
          <div className="flex items-center justify-center p-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900" />
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-4">
            {/* Message List */}
            <div className="col-span-1 border-r pr-4">
              <h3 className="font-semibold mb-2">Patients ({messages.length})</h3>
              <div className="space-y-2 max-h-[400px] overflow-y-auto">
                {messages.map((msg, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedMessage(msg)}
                    className={`w-full text-left p-3 rounded border ${
                      selectedMessage === msg ? 'bg-blue-50 border-blue-500' : 'hover:bg-gray-50'
                    }`}
                  >
                    <div className="font-semibold text-sm">{msg.mrn}</div>
                    <div className="text-xs text-gray-600">{msg.patient_name}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Message Content */}
            <div className="col-span-2">
              {selectedMessage && (
                <>
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold">
                      {selectedMessage.mrn} - {selectedMessage.trigger_event}
                    </h3>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" onClick={copyToClipboard}>
                        <Copy className="w-4 h-4 mr-1" />
                        Copy
                      </Button>
                      <Button size="sm" onClick={downloadSingleFile}>
                        <Download className="w-4 h-4 mr-1" />
                        Download
                      </Button>
                    </div>
                  </div>

                  <pre className="bg-gray-900 text-green-400 p-4 rounded text-xs overflow-x-auto max-h-[400px] overflow-y-auto font-mono">
                    {selectedMessage.hl7_message}
                  </pre>
                </>
              )}
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
```

---

### 2. Download All as ZIP (Browser-Side)

Create ZIP file in the browser without backend processing.

**Install Dependencies**:

```bash
npm install jszip
npm install --save-dev @types/jszip
```

**Utility Function**: `utils/hl7Download.ts`

```typescript
import JSZip from 'jszip';
import { toast } from 'sonner';

export async function downloadAllAsZip(uploadId: string) {
  try {
    // 1. Fetch messages from API
    const response = await fetch(
      `http://localhost:8000/api/upload/${uploadId}/download`
    );

    if (!response.ok) throw new Error('Failed to load messages');

    const data = await response.json();

    // 2. Create ZIP file
    const zip = new JSZip();

    data.messages.forEach((msg: any) => {
      zip.file(msg.suggested_filename, msg.hl7_message);
    });

    // 3. Generate ZIP blob
    const zipBlob = await zip.generateAsync({ type: 'blob' });

    // 4. Trigger download
    const url = URL.createObjectURL(zipBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `hl7_messages_${uploadId.substring(0, 8)}.zip`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    toast.success(`Downloaded ${data.total_messages} HL7 messages as ZIP!`);
  } catch (error) {
    toast.error('Failed to create ZIP file');
    console.error(error);
  }
}
```

**Usage in CompleteStep.tsx**:

```typescript
import { downloadAllAsZip } from '@/utils/hl7Download';

export function CompleteStep({ uploadId, onComplete }: CompleteStepProps) {
  return (
    <div>
      <Button onClick={() => downloadAllAsZip(uploadId)}>
        <Download className="w-4 h-4 mr-2" />
        Download All as ZIP
      </Button>
    </div>
  );
}
```

---

### 3. Copy to Clipboard

Simple function to copy messages to clipboard.

**Utility Function**: `utils/hl7Clipboard.ts`

```typescript
import { toast } from 'sonner';

export async function copyAllMessages(uploadId: string) {
  try {
    const response = await fetch(
      `http://localhost:8000/api/upload/${uploadId}/download`
    );
    const data = await response.json();

    // Combine all messages with separators
    const allMessages = data.messages
      .map((msg: any) => `// ${msg.suggested_filename}\n${msg.hl7_message}`)
      .join('\n\n========================================\n\n');

    await navigator.clipboard.writeText(allMessages);
    toast.success(`Copied ${data.total_messages} messages to clipboard!`);
  } catch (error) {
    toast.error('Failed to copy messages');
  }
}

export async function copySingleMessage(uploadId: string, mrn: string) {
  try {
    const response = await fetch(
      `http://localhost:8000/api/upload/${uploadId}/download`
    );
    const data = await response.json();

    const message = data.messages.find((msg: any) => msg.mrn === mrn);
    if (message) {
      await navigator.clipboard.writeText(message.hl7_message);
      toast.success(`Copied ${message.suggested_filename} to clipboard!`);
    }
  } catch (error) {
    toast.error('Failed to copy message');
  }
}
```

---

### 4. Export Metadata as CSV

Export message metadata (without full HL7 content) for tracking.

**Install Dependencies**:

```bash
npm install file-saver papaparse
npm install --save-dev @types/file-saver @types/papaparse
```

**Utility Function**: `utils/hl7Export.ts`

```typescript
import { saveAs } from 'file-saver';
import Papa from 'papaparse';
import { toast } from 'sonner';

export async function exportMetadataAsCSV(uploadId: string) {
  try {
    const response = await fetch(
      `http://localhost:8000/api/upload/${uploadId}/download`
    );
    const data = await response.json();

    // Extract metadata only
    const metadata = data.messages.map((msg: any) => ({
      MRN: msg.mrn,
      'Patient Name': msg.patient_name,
      'Trigger Event': msg.trigger_event,
      'Filename': msg.suggested_filename,
      'Message Length': msg.hl7_message.length,
      'Upload ID': uploadId
    }));

    // Convert to CSV
    const csv = Papa.unparse(metadata);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    saveAs(blob, `hl7_metadata_${uploadId.substring(0, 8)}.csv`);

    toast.success('Metadata exported as CSV!');
  } catch (error) {
    toast.error('Failed to export metadata');
  }
}
```

---

### 5. Complete Integration Example

**CompleteStep.tsx** - Full implementation with all download options:

```typescript
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Download, Eye, Copy, FileSpreadsheet } from 'lucide-react';
import { HL7PreviewModal } from './HL7PreviewModal';
import { downloadAllAsZip } from '@/utils/hl7Download';
import { copyAllMessages } from '@/utils/hl7Clipboard';
import { exportMetadataAsCSV } from '@/utils/hl7Export';

interface CompleteStepProps {
  uploadId: string;
  patientCount: number;
  messageCount: number;
  onComplete: () => void;
}

export function CompleteStep({
  uploadId,
  patientCount,
  messageCount,
  onComplete
}: CompleteStepProps) {
  const [showPreview, setShowPreview] = useState(false);

  return (
    <div className="space-y-6">
      {/* Success Message */}
      <div className="text-center">
        <div className="text-6xl mb-4">✅</div>
        <h2 className="text-2xl font-bold mb-2">Processing Complete!</h2>
        <p className="text-gray-600">
          Successfully processed {patientCount} patients and generated {messageCount} HL7 messages.
        </p>
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-4">
        <Button onClick={() => setShowPreview(true)} variant="outline">
          <Eye className="w-4 h-4 mr-2" />
          Preview Messages
        </Button>

        <Button onClick={() => downloadAllAsZip(uploadId)}>
          <Download className="w-4 h-4 mr-2" />
          Download as ZIP
        </Button>

        <Button onClick={() => copyAllMessages(uploadId)} variant="outline">
          <Copy className="w-4 h-4 mr-2" />
          Copy All to Clipboard
        </Button>

        <Button onClick={() => exportMetadataAsCSV(uploadId)} variant="outline">
          <FileSpreadsheet className="w-4 h-4 mr-2" />
          Export Metadata CSV
        </Button>
      </div>

      {/* Close Button */}
      <Button onClick={onComplete} className="w-full">
        Close Wizard
      </Button>

      {/* Preview Modal */}
      <HL7PreviewModal
        uploadId={uploadId}
        isOpen={showPreview}
        onClose={() => setShowPreview(false)}
      />
    </div>
  );
}
```

---

### Frontend Dependencies Summary

```bash
# Required for download features
npm install jszip file-saver papaparse

# TypeScript types
npm install --save-dev @types/jszip @types/file-saver @types/papaparse
```

---

## Complete End-to-End Examples

### Example 1: Full Workflow with Download (Python)

```python
import requests
import json
import time

BASE_URL = "http://localhost:8000"

# Step 1: Upload CSV file
print("Step 1: Uploading file...")
with open('patients.csv', 'rb') as f:
    files = {'file': ('patients.csv', f, 'text/csv')}
    data = {
        'trigger_event': 'ADT-A04',
        'use_llm_mapping': 'true'
    }

    response = requests.post(f'{BASE_URL}/api/upload', files=files, data=data)
    preview = response.json()

session_id = preview['session_id']
print(f"✅ Session ID: {session_id}")
print(f"   Total: {preview['total_records']}, Valid: {preview['valid_records']}")

# Step 2: Confirm processing
print("\nStep 2: Confirming processing...")
confirm_data = {
    'session_id': session_id,
    'selected_indices': [],  # Process all valid patients
    'send_to_mirth': True
}

response = requests.post(f'{BASE_URL}/api/upload/confirm', json=confirm_data)
confirm = response.json()

upload_id = confirm['upload_id']
print(f"✅ Upload ID: {upload_id}")

# Step 3: Wait for completion
print("\nStep 3: Waiting for processing...")
time.sleep(5)

# Step 4: Get results
response = requests.get(f'{BASE_URL}/api/upload/{upload_id}/results')
results = response.json()

print(f"\n✅ Processing Complete!")
print(f"   Success: {results['successful']}/{results['total_processed']}")
print(f"   Time: {results['processing_time_seconds']}s")

# Step 5: Download HL7 messages
print("\nStep 5: Downloading HL7 messages...")
response = requests.get(f'{BASE_URL}/api/upload/{upload_id}/download')
download = response.json()

print(f"✅ Downloaded {download['total_messages']} HL7 messages")
print("\nFirst message:")
print(f"  MRN: {download['messages'][0]['mrn']}")
print(f"  Patient: {download['messages'][0]['patient_name']}")
print(f"  Filename: {download['messages'][0]['suggested_filename']}")
print(f"  HL7 Preview: {download['messages'][0]['hl7_message'][:100]}...")
```

---

### Example 2: Full Workflow (Bash)

```bash
#!/bin/bash
# Complete workflow test script with download

BASE_URL="http://localhost:8000"

# 1. Upload
echo "Step 1: Uploading file..."
curl -X POST $BASE_URL/api/upload \
  -F "file=@patients.csv" \
  -F "trigger_event=ADT-A04" \
  -F "use_llm_mapping=true" \
  -o preview.json

SESSION_ID=$(cat preview.json | jq -r '.session_id')
echo "✅ Session ID: $SESSION_ID"

# 2. Confirm
echo "Step 2: Confirming processing..."
curl -X POST $BASE_URL/api/upload/confirm \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"selected_indices\":[],\"send_to_mirth\":true}" \
  -o confirm.json

UPLOAD_ID=$(cat confirm.json | jq -r '.upload_id')
echo "✅ Upload ID: $UPLOAD_ID"

# 3. Wait
echo "Step 3: Waiting 5 seconds..."
sleep 5

# 4. Results
echo "Step 4: Getting results..."
curl $BASE_URL/api/upload/$UPLOAD_ID/results -o results.json
cat results.json | jq '{status, total: .total_processed, success: .successful}'

# 5. Download HL7 messages
echo "Step 5: Downloading HL7 messages..."
curl $BASE_URL/api/upload/$UPLOAD_ID/download -o download.json
cat download.json | jq '{total: .total_messages, first_patient: .messages[0].patient_name}'

echo "✅ Complete! All files saved: preview.json, confirm.json, results.json, download.json"
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
    phone: Optional[str] = None         # Contact phone
    email: Optional[str] = None         # Email address
    address: Optional[str] = None       # Street address
    city: Optional[str] = None          # City
    state: Optional[str] = None         # State/Province
    zip: Optional[str] = None           # ZIP/Postal code
    validation_status: str              # "valid" or "invalid"
    validation_messages: List[str] = [] # Validation errors
```

### HL7MessageDownload

```python
class HL7MessageDownload(BaseModel):
    mrn: str                            # Medical Record Number
    trigger_event: str                  # HL7 trigger event (e.g., "ADT^A04")
    patient_name: str                   # Patient name in HL7 format (Last^First)
    hl7_message: str                    # Complete HL7 v2.5 message
    suggested_filename: str             # Recommended filename for download
```

---

## CSV/Excel File Format

### Required Columns (Tier 1)

| Column | Aliases | Example |
|--------|---------|---------|
| MRN | mrn, medical_record_number | MRN001 |
| FirstName | first_name, fname | John |
| LastName | last_name, lname | Doe |
| DOB | dob, date_of_birth | 1980-05-15 |
| Gender | gender, sex | Male |

### Sample CSV

```csv
MRN,FirstName,LastName,DOB,Gender,Phone,Email
MRN001,John,Doe,1980-05-15,Male,555-1234,john@example.com
MRN002,Jane,Smith,1990-08-20,Female,555-5678,jane@example.com
```

---

## Error Handling

### Common Errors

**Session Expired (404)**:
```json
{"detail": "Session not found or expired. Please upload the file again."}
```

**Invalid File (400)**:
```json
{"detail": "No file uploaded or invalid file format"}
```

**No Messages Found (404)**:
```json
{"detail": "No HL7 messages found for this upload"}
```

---

## Testing & Troubleshooting

### Quick Test Script

```bash
#!/bin/bash
# test_with_download.sh - Full end-to-end test with download

# 1. Upload
curl -X POST http://localhost:8000/api/upload \
  -F "file=@patients.csv" > preview.json

SESSION_ID=$(cat preview.json | jq -r '.session_id')

# 2. Confirm
curl -X POST http://localhost:8000/api/upload/confirm \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"selected_indices\":[],\"send_to_mirth\":true}" \
  > confirm.json

UPLOAD_ID=$(cat confirm.json | jq -r '.upload_id')

# 3. Wait
sleep 5

# 4. Results
curl http://localhost:8000/api/upload/$UPLOAD_ID/results | jq '.'

# 5. Download
curl http://localhost:8000/api/upload/$UPLOAD_ID/download | jq '.'
```

### Test Download Endpoint

```bash
# Get all messages
curl http://localhost:8000/api/upload/662d9ed4-0c10-4417-bec6-1d1416755cc0/download | jq '.'

# Check total count
curl http://localhost:8000/api/upload/662d9ed4-0c10-4417-bec6-1d1416755cc0/download | jq '.total_messages'

# Get first message
curl http://localhost:8000/api/upload/662d9ed4-0c10-4417-bec6-1d1416755cc0/download | jq '.messages[0]'

# Extract all filenames
curl http://localhost:8000/api/upload/662d9ed4-0c10-4417-bec6-1d1416755cc0/download | jq -r '.messages[].suggested_filename'
```

### Troubleshooting

**CORS Errors**: Check CORS middleware configuration
**Mirth Connection Refused**: Verify Mirth is running on port 6661
**AI Mapping Fails**: Falls back to fuzzy matching automatically
**Download Returns 404**: Verify upload_id exists and processing completed

---

## Conclusion

This documentation provides complete coverage of the Interface Wizard Backend API v4.0. For interactive documentation, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Summary of Key Features

- **AI-powered column mapping** - Handles any CSV format with typo tolerance
- **Programmatic HL7 generation** - Fast, reliable, cost-effective
- **Support for all ADT trigger events** - A01, A04, A08, A28, A31
- **Two-phase workflow** - Preview before processing
- **Real-time progress streaming** - SSE-based status updates
- **Comprehensive validation** - 3-tier validation system
- **HL7 message download** - JSON response with multiple export options
- **UUID tracking** - Full audit trail for all patients

---

**Document Version**: 4.0
**Last Updated**: January 7, 2026
**Author**: Shirisha G

**For UI Implementation Details**: See [API-v3.0.1-HL7-Download-Endpoint.md](./API-v3.0.1-HL7-Download-Endpoint.md) for additional UI code examples and integration patterns.
