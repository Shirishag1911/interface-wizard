# Interface Wizard Backend API Documentation

**Version:** 3.0 (Complete Rewrite)
**Last Updated:** December 30, 2025
**Backend Framework:** FastAPI 0.109+
**Base URL:** `http://localhost:8000`

---

## Table of Contents

1. [Overview](#overview)
2. [What's New in v3.0](#whats-new-in-v30)
3. [Key Features](#key-features)
4. [Technology Stack](#technology-stack)
5. [Quick Start](#quick-start)
6. [Understanding HL7 ADT Messages](#understanding-hl7-adt-messages)
7. [Intelligent Column Mapping](#intelligent-column-mapping)
8. [API Endpoints Reference](#api-endpoints-reference)
9. [Complete End-to-End Examples](#complete-end-to-end-examples)
10. [Data Models](#data-models)
11. [CSV/Excel File Format](#csvexcel-file-format)
12. [Error Handling](#error-handling)
13. [Testing & Troubleshooting](#testing--troubleshooting)

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
1. Upload CSV/Excel → 2. AI Analyzes Columns → 3. Preview Data → 4. Generate HL7 → 5. Send to Mirth → 6. Insert to OpenEMR
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
│ └─────────────────────────────────┘ │
└────────┬────────────────────────────┘
         │ MLLP (port 6661)
         ▼
┌─────────────────────────────────────┐
│ Mirth Connect                       │
│ ┌─────────────────────────────────┐ │
│ │ 8. Parse HL7 Message            │ │
│ │ 9. Extract Patient Data         │ │
│ │ 10. Insert into Database        │ │
│ │ 11. Send ACK Response           │ │
│ └─────────────────────────────────┘ │
└────────┬────────────────────────────┘
         │ SQL INSERT
         ▼
┌─────────────────┐
│ OpenEMR MySQL   │
│ patient_data    │
└─────────────────┘
```

---

## What's New in v3.0

### 🚀 Major Improvements

#### 1. **AI-Powered Column Mapping** (NEW!)

**Problem**: CSV files have inconsistent column names like "Patient First Name", "Pateint First Name" (typo), "First Name", "fname", etc.

**Old Solution (v2.0)**: Hardcoded every possible variation
```python
# Had to manually add every variation:
COLUMN_MAPPINGS = {
    "firstName": ["first_name", "fname", "first name", "patient first name", "given name", ...]
}
# Impossible to cover all variations!
```

**New Solution (v3.0)**: Use OpenAI GPT-4o-mini to intelligently understand column semantics
```python
# AI automatically understands ANY reasonable column name:
"Patient Last Name" → lastName ✅
"Pateint First Name" → firstName ✅ (detects typo)
"E-mail Address" → email ✅
"Phone #" → phone ✅
# No hardcoding needed!
```

**Benefits:**
- ✅ Handles **unlimited column name variations** (no hardcoding)
- ✅ **Typo tolerant** - AI understands "Pateint" means "Patient"
- ✅ **Context aware** - Distinguishes "Full Name" vs "Last Name"
- ✅ **Confidence scores** - Shows how certain the mapping is
- ✅ **Automatic fallback** - Uses fuzzy matching if AI unavailable

#### 2. **Programmatic HL7 Generation** (NEW!)

**Problem**: v2.0 used AI to generate HL7 messages, which was slow and unreliable.

**Old Solution**:
- Asked GPT-4 to generate HL7 messages from patient data
- **Slow**: 1-2 seconds per patient
- **Expensive**: API cost for every patient
- **Unreliable**: AI sometimes formatted messages incorrectly

**New Solution**: Deterministic programmatic HL7 builder
```python
def build_hl7_message_programmatically(patient, trigger_event="ADT-A04"):
    """
    Builds HL7 v2.5 message using code (NO AI needed!)
    - Fast: <10ms per patient
    - Free: No API costs
    - Reliable: 100% spec-compliant
    """
```

**Benefits:**
- ✅ **10x faster** (0.1s vs 1-2s per patient)
- ✅ **100% reliable** - Always generates spec-compliant HL7
- ✅ **Free** - No API costs for HL7 generation
- ✅ **Supports all ADT types** - A01, A04, A08, A28, A31

#### 3. **Two-Phase Workflow** (IMPROVED!)

**Problem**: v1.0 processed files immediately without user review.

**New Solution**: Preview before processing
```
Phase 1: Upload → Parse → Validate → Preview (user reviews data)
Phase 2: Confirm → Generate HL7 → Send to Mirth (user confirms)
```

**Benefits:**
- ✅ User can review parsed data before sending
- ✅ Can deselect invalid patients
- ✅ Prevents accidental data submission
- ✅ Shows validation errors upfront

#### 4. **Real-Time Progress Tracking** (NEW!)

Uses Server-Sent Events (SSE) to stream live updates:
```
Step 1: Initializing... (0%)
Step 2: Generating HL7 messages (1/10)... (20%)
Step 3: Generating HL7 messages (2/10)... (30%)
Step 4: Sending to Mirth (1/10)... (50%)
...
Step 6: Complete! (100%)
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

See [Intelligent Column Mapping](#intelligent-column-mapping) for details.

### 2. Flexible HL7 Message Types

**All ADT (Admit/Discharge/Transfer) trigger events supported:**

| Trigger Event | Description | Patient Class | Use Case |
|--------------|-------------|---------------|----------|
| **ADT^A01** | Admit/Visit Notification | Inpatient (I) | Hospital admission |
| **ADT^A04** | Register Patient | Outpatient (O) | **Default - Most Common** |
| **ADT^A08** | Update Patient Info | Inpatient (I) | Update existing patient |
| **ADT^A28** | Add Person Information | Outpatient (O) | New patient registration |
| **ADT^A31** | Update Person Info | Outpatient (O) | Update existing person |

**Why ADT-A04 is Default:**
- ✅ Most commonly used for bulk patient registration
- ✅ Works for outpatient registration (most use cases)
- ✅ Compatible with most EHR systems
- ✅ Simpler than A01 (no admission details needed)

See [Understanding HL7 ADT Messages](#understanding-hl7-adt-messages) for details.

### 3. Multi-Format Support

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

### 4. 3-Tier Data Validation

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

### 5. UUID Tracking

Every patient record gets a unique UUID (v4) for tracking:
```
Patient: John Doe (MRN: MRN001)
UUID: a1b2c3d4-e5f6-7890-abcd-ef1234567890

HL7 Message includes custom ZPI segment:
ZPI|a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Benefits:**
- ✅ Track specific patient records across systems
- ✅ Correlate upload batch with database records
- ✅ Debugging and audit trails
- ✅ Prevent duplicate processing

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
MSH|^~\&|InterfaceWizard|FACILITY|OpenEMR|HOSPITAL|20251230120000||ADT^A04|MSG001|P|2.5
EVN|A04|20251230120000
PID|1||MRN001^^^MRN||Doe^John||19800515|M|||123 Main St^City^State^12345||555-1234|||||||||||||||
ZPI|a1b2c3d4-e5f6-7890-abcd-ef1234567890
PV1|1|O|||||||||||||||||||||||||||||||||||||||||20251230120000
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
MSH|^~\&|InterfaceWizard|FACILITY|OpenEMR|HOSPITAL|20251230120000||ADT^A04|MSG001|P|2.5
```

| Field | Value | Meaning |
|-------|-------|---------|
| MSH-1 | `|` | Field separator |
| MSH-2 | `^~\&` | Encoding characters |
| MSH-3 | `InterfaceWizard` | Sending application |
| MSH-4 | `FACILITY` | Sending facility |
| MSH-5 | `OpenEMR` | Receiving application |
| MSH-6 | `HOSPITAL` | Receiving facility |
| MSH-7 | `20251230120000` | Message timestamp (YYYYMMDDHHmmss) |
| MSH-9 | `ADT^A04` | Message type (ADT) and trigger event (A04) |
| MSH-10 | `MSG001` | Unique message control ID |
| MSH-11 | `P` | Processing ID (P = Production) |
| MSH-12 | `2.5` | HL7 version |

### EVN Segment (Event Type)

```
EVN|A04|20251230120000
```

| Field | Value | Meaning |
|-------|-------|---------|
| EVN-1 | `A04` | Event type code (Register Patient) |
| EVN-2 | `20251230120000` | Event occurred timestamp |

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
PV1|1|O|||||||||||||||||||||||||||||||||||||||||20251230120000
```

| Field | Value | Meaning |
|-------|-------|---------|
| PV1-1 | `1` | Set ID |
| PV1-2 | `O` | Patient class (O=Outpatient, I=Inpatient, E=Emergency) |
| PV1-44 | `20251230120000` | Admit timestamp |

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
- **Most common for CSV uploads**

**Patient Class**: `O` (Outpatient)

**Why Default**:
- ✅ Simple - no admission details needed
- ✅ Works for most use cases
- ✅ Widely supported by EHR systems
- ✅ Perfect for bulk imports

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

✅ **Unlimited Variations**: Works with ANY reasonable column name
✅ **Typo Tolerance**: AI understands "Pateint" = "Patient"
✅ **Context Awareness**: Distinguishes "Full Name" vs "Last Name"
✅ **Multi-Language**: Can understand non-English column names
✅ **Confidence Scores**: Shows certainty of mapping
✅ **Warnings**: Flags ambiguous or unusual mappings
✅ **Self-Improving**: Gets better as AI models improve

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

✅ **No API Costs**: Completely free
✅ **Fast**: <1ms per column
✅ **Offline**: Works without internet
✅ **Predictable**: Deterministic results

**Limitations:**

❌ Less flexible than AI
❌ Can't handle complex variations
❌ Limited to predefined keywords

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
    },
    {
      "index": 1,
      "uuid": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "mrn": "MRN002",
      "firstName": "Jane",
      "lastName": "Smith",
      "dateOfBirth": "1990-08-20",
      "gender": "Female",
      "phone": "555-5678",
      "email": "jane.smith@example.com",
      "address": null,
      "city": null,
      "state": null,
      "zip": null,
      "validation_status": "valid",
      "validation_messages": []
    },
    {
      "index": 2,
      "uuid": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "mrn": "",
      "firstName": "",
      "lastName": "Johnson",
      "dateOfBirth": "invalid-date",
      "gender": "M",
      "phone": null,
      "email": null,
      "address": null,
      "city": null,
      "state": null,
      "zip": null,
      "validation_status": "invalid",
      "validation_messages": [
        "Missing required field: mrn (Tier 1 - Critical)",
        "Missing required field: firstName (Tier 1 - Critical)",
        "Invalid date format for dateOfBirth: 'invalid-date' (Tier 1 - Critical)"
      ]
    }
  ],
  "validation_errors": [
    {
      "row": 2,
      "field": "mrn",
      "error": "Missing required field",
      "value": "",
      "severity": "error"
    },
    {
      "row": 2,
      "field": "firstName",
      "error": "Missing required field",
      "value": "",
      "severity": "error"
    },
    {
      "row": 2,
      "field": "dateOfBirth",
      "error": "Invalid date format",
      "value": "invalid-date",
      "severity": "error"
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
    "Pateint First Name": 0.98,
    "Email Address": 1.0,
    "Phone Number": 1.0,
    "DOB": 1.0,
    "Gender": 1.0,
    "MRN": 1.0
  },
  "mapping_warnings": [
    "Detected typo in 'Pateint First Name' - mapped to firstName"
  ],
  "expires_at": "2025-12-30T13:30:00Z",
  "timestamp": "2025-12-30T12:30:00Z"
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string (UUID) | Unique session identifier - use this for `/confirm` |
| `file_name` | string | Original filename |
| `file_type` | string | "csv" or "excel" |
| `total_records` | integer | Total number of records in file |
| `valid_records` | integer | Number of valid patient records (can be processed) |
| `invalid_records` | integer | Number of invalid records (has validation errors) |
| `patients` | array | **ALL patient records** with validation status |
| `validation_errors` | array | List of all validation errors across all records |
| `column_mapping` | object | CSV column names → standard field names |
| `mapping_method` | string | "llm" (AI) or "fuzzy" (rule-based) |
| `mapping_confidence` | object | Confidence score (0.0-1.0) for each mapping |
| `mapping_warnings` | array | Warnings about ambiguous or unusual mappings |
| `expires_at` | string | Session expiration time (1 hour from upload) |
| `timestamp` | string | Upload timestamp (ISO 8601) |

**Status Codes**:

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | File processed successfully |
| 400 | Bad Request | No file uploaded, invalid file format |
| 500 | Internal Server Error | Processing error, AI error |

**Testing Example (Python)**:

```python
import requests

# Upload file
with open('patients.csv', 'rb') as f:
    files = {'file': ('patients.csv', f, 'text/csv')}
    data = {
        'trigger_event': 'ADT-A04',
        'use_llm_mapping': 'true'  # Use AI mapping
    }

    response = requests.post(
        'http://localhost:8000/api/upload',
        files=files,
        data=data
    )

# Check response
if response.status_code == 200:
    preview = response.json()

    print(f"Session ID: {preview['session_id']}")
    print(f"Total: {preview['total_records']}, Valid: {preview['valid_records']}")
    print(f"\nColumn Mapping (Method: {preview['mapping_method']}):")
    for csv_col, std_field in preview['column_mapping'].items():
        confidence = preview['mapping_confidence'].get(csv_col, 'N/A')
        print(f"  '{csv_col}' → '{std_field}' (confidence: {confidence})")

    print(f"\nPatients:")
    for patient in preview['patients']:
        status_icon = "✅" if patient['validation_status'] == 'valid' else "❌"
        print(f"  {status_icon} {patient['firstName']} {patient['lastName']} - {patient['validation_status']}")
        if patient['validation_messages']:
            for msg in patient['validation_messages']:
                print(f"      - {msg}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

**Expected Output**:

```
Session ID: 550e8400-e29b-41d4-a716-446655440000
Total: 3, Valid: 2

Column Mapping (Method: llm):
  'Patient Last Name' → 'lastName' (confidence: 1.0)
  'Pateint First Name' → 'firstName' (confidence: 0.98)
  'Email Address' → 'email' (confidence: 1.0)
  'Phone Number' → 'phone' (confidence: 1.0)
  'DOB' → 'dateOfBirth' (confidence: 1.0)
  'Gender' → 'gender' (confidence: 1.0)
  'MRN' → 'mrn' (confidence: 1.0)

Patients:
  ✅ John Doe - valid
  ✅ Jane Smith - valid
  ❌  Johnson - invalid
      - Missing required field: mrn (Tier 1 - Critical)
      - Missing required field: firstName (Tier 1 - Critical)
      - Invalid date format for dateOfBirth: 'invalid-date' (Tier 1 - Critical)
```

**Testing Example (curl + jq)**:

```bash
# Upload and save response
curl -X POST http://localhost:8000/api/upload \
  -F "file=@patients.csv" \
  -F "trigger_event=ADT-A04" \
  -F "use_llm_mapping=true" \
  | jq '.' > preview.json

# Extract session ID
SESSION_ID=$(cat preview.json | jq -r '.session_id')
echo "Session ID: $SESSION_ID"

# Show column mapping
cat preview.json | jq '.column_mapping'

# Show valid vs invalid count
cat preview.json | jq '{total: .total_records, valid: .valid_records, invalid: .invalid_records}'

# Show first patient
cat preview.json | jq '.patients[0]'
```

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

**How `selected_indices` Works:**

```python
# Example: You have 5 patients from upload (indices 0-4)
# Valid: indices 0, 1, 3 (patients with validation_status = "valid")
# Invalid: indices 2, 4

# Process ALL valid patients
{"selected_indices": []}  # Empty array = all valid

# Process specific patients only
{"selected_indices": [0, 1]}  # Only process indices 0 and 1

# Process only one patient
{"selected_indices": [3]}  # Only process index 3
```

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

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `upload_id` | string | Unique processing job ID - use for `/stream` and `/results` |
| `status` | string | Always "processing" (background task started) |
| `total_selected` | integer | Number of patients being processed |
| `message` | string | Human-readable status message |
| `stream_url` | string | SSE endpoint to monitor real-time progress |

**Status Codes**:

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Processing started successfully |
| 400 | Bad Request | Invalid session_id, no patients selected |
| 404 | Not Found | Session not found or expired (>1 hour old) |
| 500 | Internal Server Error | Processing error |

**What Happens After Confirmation?**

1. **Background Task Starts**: Processing runs asynchronously (non-blocking)
2. **HL7 Generation**: Programmatic builder creates HL7 messages (<10ms per patient)
3. **MLLP Transmission**: Sends to Mirth Connect on port 6661
4. **ACK Processing**: Receives acknowledgment from Mirth
5. **Results Stored**: Final results saved in memory

**Testing Example (Python)**:

```python
import requests

# Assume we have session_id from previous upload
session_id = "550e8400-e29b-41d4-a716-446655440000"

# Confirm and process all valid patients
confirm_data = {
    'session_id': session_id,
    'selected_indices': [],  # Empty = all valid patients
    'send_to_mirth': True
}

response = requests.post(
    'http://localhost:8000/api/upload/confirm',
    json=confirm_data
)

if response.status_code == 200:
    result = response.json()

    print(f"Upload ID: {result['upload_id']}")
    print(f"Status: {result['status']}")
    print(f"Processing {result['total_selected']} patients")
    print(f"Monitor progress at: {result['stream_url']}")

    # Now connect to SSE stream (next endpoint)
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

**Testing Example (curl)**:

```bash
# Extract session_id from previous upload
SESSION_ID=$(cat preview.json | jq -r '.session_id')

# Confirm and process
curl -X POST http://localhost:8000/api/upload/confirm \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"selected_indices\": [],
    \"send_to_mirth\": true
  }" | jq '.' > confirm.json

# Extract upload_id
UPLOAD_ID=$(cat confirm.json | jq -r '.upload_id')
echo "Upload ID: $UPLOAD_ID"
```

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
  console.log(`Status: ${data.status}`);

  // Update UI (progress bar, message, etc.)
  updateProgressBar(data.progress);
  updateMessage(data.message);

  if (data.status === 'completed' || data.status === 'failed') {
    eventSource.close();
    console.log("Processing finished!");
  }
};

eventSource.onerror = (error) => {
  console.error('SSE error:', error);
  eventSource.close();
};
```

**Response Stream**:

```
data: {"step":1,"message":"Initializing processing...","progress":0,"status":"processing"}

data: {"step":2,"message":"Generating HL7 messages (1/2)","progress":20,"status":"processing"}

data: {"step":3,"message":"Generating HL7 messages (2/2)","progress":40,"status":"processing"}

data: {"step":4,"message":"Sending to Mirth Connect (1/2)","progress":60,"status":"processing"}

data: {"step":5,"message":"Sending to Mirth Connect (2/2)","progress":80,"status":"processing"}

data: {"step":6,"message":"Complete: 2 processed, 2 success, 0 failed","progress":100,"status":"completed"}
```

**Event Data Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `step` | integer | Current processing step (1-6) |
| `message` | string | Human-readable progress message |
| `progress` | integer | Progress percentage (0-100) |
| `status` | string | "processing", "completed", or "failed" |

**Processing Steps Explained**:

| Step | Name | Progress | What's Happening |
|------|------|----------|------------------|
| 1 | Initialization | 0% | Loading patient records from session |
| 2-3 | HL7 Generation | 20-50% | Building HL7 messages programmatically |
| 4-5 | Mirth Transmission | 50-90% | Sending via MLLP protocol, receiving ACKs |
| 6 | Completion | 100% | Finalizing results, cleanup |

**Status Codes**:

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Stream established successfully |
| 404 | Not Found | Upload ID doesn't exist |

**Testing Example (Python with sseclient)**:

```python
import requests
import sseclient  # pip install sseclient-py

upload_id = "upload_1735559400_abc123"

# Connect to SSE stream
response = requests.get(
    f'http://localhost:8000/api/upload/{upload_id}/stream',
    stream=True
)

client = sseclient.SSEClient(response)

for event in client.events():
    data = json.loads(event.data)

    print(f"[Step {data['step']}] {data['message']} ({data['progress']}%)")

    if data['status'] == 'completed':
        print("✅ Processing completed successfully!")
        break
    elif data['status'] == 'failed':
        print("❌ Processing failed!")
        break
```

**Testing Example (curl)**:

```bash
# Monitor SSE stream (will stay connected until complete)
UPLOAD_ID=$(cat confirm.json | jq -r '.upload_id')

curl -N http://localhost:8000/api/upload/$UPLOAD_ID/stream
```

**Example Output**:

```
data: {"step":1,"message":"Initializing processing...","progress":0,"status":"processing"}
[Step 1] Initializing processing... (0%)

data: {"step":2,"message":"Generating HL7 messages (1/2)","progress":20,"status":"processing"}
[Step 2] Generating HL7 messages (1/2) (20%)

data: {"step":3,"message":"Generating HL7 messages (2/2)","progress":40,"status":"processing"}
[Step 3] Generating HL7 messages (2/2) (40%)

data: {"step":4,"message":"Sending to Mirth Connect (1/2)","progress":60,"status":"processing"}
[Step 4] Sending to Mirth Connect (1/2) (60%)

data: {"step":5,"message":"Sending to Mirth Connect (2/2)","progress":80,"status":"processing"}
[Step 5] Sending to Mirth Connect (2/2) (80%)

data: {"step":6,"message":"Complete: 2 processed, 2 success, 0 failed","progress":100,"status":"completed"}
[Step 6] Complete: 2 processed, 2 success, 0 failed (100%)
✅ Processing completed successfully!
```

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
      "hl7_message": "MSH|^~\\&|InterfaceWizard|FACILITY|OpenEMR|HOSPITAL|20251230120000||ADT^A04|MSG001|P|2.5\nEVN|A04|20251230120000\nPID|1||MRN001^^^MRN||Doe^John||19800515|M|||123 Main St^Springfield^IL^62701||555-1234||||||||||||||||\nZPI|a1b2c3d4-e5f6-7890-abcd-ef1234567890\nPV1|1|O|||||||||||||||||||||||||||||||||||||||||20251230120000",
      "mirth_ack": "MSH|^~\\&|Mirth|Mirth|InterfaceWizard|IW|20251230120001||ACK|ACK001|P|2.5\nMSA|AA|MSG001",
      "status": "success",
      "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    },
    {
      "patient": "Jane Smith (MRN: MRN002)",
      "hl7_message": "MSH|^~\\&|InterfaceWizard|FACILITY|OpenEMR|HOSPITAL|20251230120001||ADT^A04|MSG002|P|2.5\nEVN|A04|20251230120001\nPID|1||MRN002^^^MRN||Smith^Jane||19900820|F|||^Springfield^IL^||555-5678||||||||||||||||\nZPI|b2c3d4e5-f6a7-8901-bcde-f12345678901\nPV1|1|O|||||||||||||||||||||||||||||||||||||||||20251230120001",
      "mirth_ack": "MSH|^~\\&|Mirth|Mirth|InterfaceWizard|IW|20251230120002||ACK|ACK002|P|2.5\nMSA|AA|MSG002",
      "status": "success",
      "uuid": "b2c3d4e5-f6a7-8901-bcde-f12345678901"
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
| `processing_time_seconds` | float | Total processing time |
| `results` | array | Detailed result for each patient |

**Result Object Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `patient` | string | Patient name and MRN (human-readable) |
| `hl7_message` | string | Full HL7 v2.5 message sent to Mirth |
| `mirth_ack` | string | Acknowledgment response from Mirth |
| `status` | string | "success" or "failed" |
| `uuid` | string | Patient UUID for tracking |

**Mirth ACK Interpretation**:

```
MSA|AA|MSG001
     ^^
     ||
     |└─ AA = Application Accept (success)
     └── Other codes:
         AE = Application Error (failed)
         AR = Application Reject (rejected)
```

**Status Codes**:

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Results retrieved successfully |
| 404 | Not Found | Upload ID doesn't exist |
| 202 | Accepted | Processing still in progress (not ready yet) |

**Testing Example (Python)**:

```python
import requests
import time

upload_id = "upload_1735559400_abc123"

# Wait for processing to complete (poll every 2 seconds)
while True:
    response = requests.get(
        f'http://localhost:8000/api/upload/{upload_id}/results'
    )

    if response.status_code == 200:
        results = response.json()

        if results['status'] == 'completed':
            print(f"✅ Processing Complete!")
            print(f"   Total: {results['total_processed']}")
            print(f"   Success: {results['successful']}")
            print(f"   Failed: {results['failed']}")
            print(f"   Time: {results['processing_time_seconds']}s")

            print(f"\nResults:")
            for i, result in enumerate(results['results'], 1):
                status_icon = "✅" if result['status'] == 'success' else "❌"
                print(f"  {status_icon} {i}. {result['patient']}")
                print(f"      UUID: {result['uuid']}")
                print(f"      Status: {result['status']}")

                # Show HL7 message (first 200 chars)
                hl7_preview = result['hl7_message'][:200] + "..."
                print(f"      HL7: {hl7_preview}")

            break
        else:
            print(f"⏳ Processing still running... ({results.get('progress', 'N/A')}%)")
    elif response.status_code == 202:
        print("⏳ Processing in progress, waiting...")
    else:
        print(f"❌ Error: {response.status_code}")
        break

    time.sleep(2)  # Wait 2 seconds before checking again
```

**Testing Example (curl)**:

```bash
# Get results
UPLOAD_ID=$(cat confirm.json | jq -r '.upload_id')

curl http://localhost:8000/api/upload/$UPLOAD_ID/results | jq '.'

# Show summary only
curl http://localhost:8000/api/upload/$UPLOAD_ID/results | \
  jq '{status, total: .total_processed, success: .successful, failed}'

# Show first patient's HL7 message
curl http://localhost:8000/api/upload/$UPLOAD_ID/results | \
  jq -r '.results[0].hl7_message'
```

---

### 5. GET /api/dashboard/stats

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

### 6. GET /health

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

## Complete End-to-End Examples

### Example 1: Simple Upload (Python)

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
time.sleep(5)  # Give it time to process

# Step 4: Get results
response = requests.get(f'{BASE_URL}/api/upload/{upload_id}/results')
results = response.json()

print(f"\n✅ Processing Complete!")
print(f"   Success: {results['successful']}/{results['total_processed']}")
print(f"   Time: {results['processing_time_seconds']}s")
```

### Example 2: Full Workflow with React

See [QUICK_START.md](../QUICK_START.md) for complete React integration example.

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

---

## Testing & Troubleshooting

### Quick Test Script

```bash
#!/bin/bash
# test.sh - Quick end-to-end test

# 1. Upload
echo "Uploading..."
curl -X POST http://localhost:8000/api/upload \
  -F "file=@patients.csv" > preview.json

SESSION_ID=$(cat preview.json | jq -r '.session_id')
echo "Session ID: $SESSION_ID"

# 2. Confirm
echo "Confirming..."
curl -X POST http://localhost:8000/api/upload/confirm \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"selected_indices\":[],\"send_to_mirth\":true}" \
  > confirm.json

UPLOAD_ID=$(cat confirm.json | jq -r '.upload_id')
echo "Upload ID: $UPLOAD_ID"

# 3. Wait
echo "Waiting 5 seconds..."
sleep 5

# 4. Results
echo "Getting results..."
curl http://localhost:8000/api/upload/$UPLOAD_ID/results | jq '.'
```

### Troubleshooting

**CORS Errors**: Check CORS middleware configuration
**Mirth Connection Refused**: Verify Mirth is running on port 6661
**AI Mapping Fails**: Falls back to fuzzy matching automatically

---

## Conclusion

This documentation provides complete coverage of the Interface Wizard Backend API v3.0. For interactive documentation, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

**Key Improvements in v3.0**:
- ✅ AI-powered column mapping
- ✅ Programmatic HL7 generation (10x faster)
- ✅ Support for all ADT trigger events
- ✅ Real-time progress streaming
- ✅ Comprehensive validation

---

**Document Version**: 3.0 (Complete Rewrite)
**Last Updated**: December 30, 2025
**Author**: Shirisha G
