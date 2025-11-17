# Mirth Connect Setup Guide for Interface Wizard

## Table of Contents
1. [What is Mirth Connect?](#what-is-mirth-connect)
2. [Architecture Overview](#architecture-overview)
3. [Understanding HL7 Messages](#understanding-hl7-messages)
4. [Channel Components Explained](#channel-components-explained)
5. [Step-by-Step Channel Setup](#step-by-step-channel-setup)
6. [Why Use Source Transformer for Database?](#why-use-source-transformer-for-database)
7. [Code Walkthrough](#code-walkthrough)
8. [Troubleshooting](#troubleshooting)

---

## What is Mirth Connect?

**Mirth Connect** is an integration engine (middleware) that helps different healthcare systems communicate with each other. Think of it as a **translator and messenger** between systems.

### Real-World Analogy:
Imagine you speak English, and your friend speaks Spanish. Mirth Connect is like a translator who:
1. Listens to you speak English
2. Translates it to Spanish
3. Delivers it to your friend
4. Can also save a copy of the conversation in a notebook (database)

### In Our Project:
- **You (English Speaker)** = Interface Wizard Backend (sends HL7 messages)
- **Friend (Spanish Speaker)** = OpenEMR Database (expects database records)
- **Translator** = Mirth Connect (converts HL7 → Database inserts)
- **Notebook** = MySQL Database (stores patient records)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         INTERFACE WIZARD SYSTEM                      │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Frontend   │         │   Backend    │         │    Mirth     │
│  (Angular/   │  HTTP   │   (FastAPI)  │  MLLP   │   Connect    │
│   React)     │ ──────> │              │ ──────> │              │
│              │         │              │         │              │
└──────────────┘         └──────────────┘         └──────────────┘
                                                          │
                                                          │ JDBC/SQL
                                                          ▼
                                                   ┌──────────────┐
                                                   │   OpenEMR    │
                                                   │   Database   │
                                                   │   (MySQL)    │
                                                   └──────────────┘

FLOW EXPLANATION:
─────────────────

1. User types: "Create patient John Doe" in Frontend

2. Frontend sends HTTP request to Backend API

3. Backend (FastAPI) creates HL7 message:
   MSH|^~\&|Interface Wizard|...
   PID|||12345||Doe^John||19800101|M|||...

4. Backend sends HL7 message via MLLP protocol to Mirth Connect

5. Mirth Connect receives and processes:
   ┌────────────────────────────────────────────┐
   │         MIRTH CONNECT CHANNEL              │
   │                                            │
   │  ┌──────────┐    ┌────────────┐           │
   │  │  Source  │    │   Source   │           │
   │  │ Connector│───>│Transformer │           │
   │  │ (MLLP)   │    │ (Database  │           │
   │  │ Listen   │    │  Insert)   │           │
   │  │ on 6661  │    │            │           │
   │  └──────────┘    └────────────┘           │
   │                        │                   │
   │                        ▼                   │
   │                  ┌────────────┐            │
   │                  │OpenEMR DB  │            │
   │                  │ (Patient   │            │
   │                  │  Created)  │            │
   │                  └────────────┘            │
   └────────────────────────────────────────────┘

6. Patient appears in OpenEMR
```

---

## Understanding HL7 Messages

### What is HL7?

**HL7 (Health Level 7)** is a standard format for exchanging healthcare information between systems.

### Example HL7 Message:

```
MSH|^~\&|InterfaceWizard|Facility|||20251117101530||ADT^A04|MSG001|P|2.5
PID|1||12345^^^MRN||Doe^John^M||19800101|M|||123 Main St^^Boston^MA^02101
```

### Breaking It Down:

```
┌─────────────────────────────────────────────────────────────┐
│ MSH Segment (Message Header)                                │
├─────────────────────────────────────────────────────────────┤
│ MSH | ^~\& | InterfaceWizard | ... | ADT^A04 | ...         │
│  │     │         │                      │                   │
│  │     │         │                      └─ Message Type     │
│  │     │         └─ Sending Application                     │
│  │     └─ Field Separator Characters                        │
│  └─ Segment Type                                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ PID Segment (Patient Identification)                        │
├─────────────────────────────────────────────────────────────┤
│ PID | 1 || 12345 ||| Doe^John^M || 19800101 | M | ...      │
│      │     │         │              │          │            │
│      │     │         │              │          └─ Gender    │
│      │     │         │              └─ Date of Birth        │
│      │     │         └─ Patient Name (Last^First^Middle)   │
│      │     └─ Patient ID (MRN)                              │
│      └─ Set ID                                              │
└─────────────────────────────────────────────────────────────┘
```

### Message Types:
- **ADT^A04** = Admit/Register Patient
- **ADT^A08** = Update Patient Information
- **ORU^R01** = Observation Result (Lab Results)
- **QRY^A19** = Patient Query

---

## Channel Components Explained

A Mirth Connect **Channel** is like a pipeline with different stages. Our channel has these components:

```
┌────────────────────────────────────────────────────────────────┐
│                      MIRTH CHANNEL                             │
│                                                                │
│  ┌──────────────┐      ┌──────────────┐      ┌─────────────┐ │
│  │    SOURCE    │      │ TRANSFORMER  │      │ DESTINATION │ │
│  │  CONNECTOR   │─────>│              │─────>│             │ │
│  │              │      │              │      │             │ │
│  └──────────────┘      └──────────────┘      └─────────────┘ │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 1. Source Connector
**What it does:** Listens for incoming messages

**Types:**
- **MLLP Listener** - Waits for HL7 messages on a TCP port
- **File Reader** - Reads HL7 files from a folder
- **HTTP Listener** - Receives messages via HTTP POST

**Our Setup:**
```
Type: MLLP Listener
Port: 6661
Host: localhost (0.0.0.0)
```

**Real-World Analogy:** Like a mailbox waiting to receive letters

---

### 2. Source Transformer
**What it does:** Processes/transforms the incoming message BEFORE sending to destinations

**When to use:**
- Convert message format (HL7 → JSON, HL7 → XML)
- Extract data from message
- **Write to database directly** (what we're doing!)
- Data validation and enrichment

**Real-World Analogy:** Like opening the letter, reading it, and taking notes in your personal notebook before forwarding it

**Why we use it for database?**
- ✅ Faster - no need to wait for destination
- ✅ Guaranteed execution - runs even if destinations fail
- ✅ Can validate before forwarding
- ✅ Single point of data processing

---

### 3. Destination Connector
**What it does:** Sends the transformed message to target systems

**Types:**
- **File Writer** - Saves message to a file
- **Database Writer** - Inserts/updates database (but we don't use this!)
- **HTTP Sender** - Sends to REST API
- **SMTP** - Sends email

**Our Setup:**
```
Type: File Writer
Directory: C:/mirth/hl7_messages/
File Name: MSG_${message.messageId}.hl7
```

**Real-World Analogy:** Like filing the original letter in a cabinet for record-keeping

---

## Why Use Source Transformer for Database?

### Option 1: Database Destination (Not Recommended)
```
Source → Transformer → Database Destination
                          ↓
                     (Slower, can fail)
```

**Problems:**
- ❌ Destination can fail independently
- ❌ Harder to debug
- ❌ Message must complete before database insert
- ❌ More complex error handling

---

### Option 2: Source Transformer (What We Use)
```
Source → Transformer (writes to DB) → File Destination
            ↓                            ↓
         Database                     Archive
         (Fast!)                      (Backup)
```

**Benefits:**
- ✅ Database insert happens immediately
- ✅ Even if file write fails, patient is saved
- ✅ Easier to debug (all logic in one place)
- ✅ More control with JavaScript/SQL
- ✅ Can check if patient exists before inserting

---

## Step-by-Step Channel Setup

### Step 1: Open Mirth Connect Administrator

1. Launch **Mirth Connect Administrator**
2. Login (default: admin/admin)
3. Click **Channels** in the left panel

---

### Step 2: Create New Channel

1. Click **New Channel** button
2. Set these properties:

```
┌─────────────────────────────────────────┐
│ Channel Properties                       │
├─────────────────────────────────────────┤
│ Name: Interface Wizard HL7 Listener     │
│ Data Type: HL7v2.x                      │
│ Description: Receives HL7 from          │
│              Interface Wizard and       │
│              stores in OpenEMR DB       │
└─────────────────────────────────────────┘
```

---

### Step 3: Configure Source Connector

Click on **Source** tab:

```
┌─────────────────────────────────────────┐
│ Source Connector Settings                │
├─────────────────────────────────────────┤
│ Connector Type: MLLP Listener           │
│                                          │
│ Listener Settings:                       │
│   Host: 0.0.0.0                         │
│   Port: 6661                            │
│                                          │
│ Response:                                │
│   ACK (Acknowledgment)                  │
│                                          │
│ Data Type: HL7v2.x                      │
└─────────────────────────────────────────┘
```

**What this means:**
- Listens on all network interfaces (0.0.0.0)
- Waits for messages on port 6661
- Automatically sends ACK (acknowledgment) back to sender
- Expects HL7 v2.x format messages

---

### Step 4: Configure Source Transformer

Click on **Source → Transformer** tab:

This is where we write JavaScript code to:
1. Extract patient data from HL7 message
2. Insert into OpenEMR database

**Full Code:**

```javascript
// ============================================
// SOURCE TRANSFORMER: HL7 to Database Insert
// ============================================

logger.info('=== Source Transformer: Patient Creation ===');

// Get PID segment (Patient Identification)
var pid = msg['PID'];
if (!pid) {
    logger.error('No PID segment in message');
    return msg;
}

// Helper function to safely extract field values
function safe(obj, field) {
    try {
        return obj && obj[field] ? String(obj[field]) : '';
    } catch (e) {
        return '';
    }
}

// Extract patient data from HL7 PID segment
var patientMRN = safe(pid['PID.3'], 'PID.3.1');      // Medical Record Number
var firstName = safe(pid['PID.5'], 'PID.5.2');       // First Name
var lastName = safe(pid['PID.5']['PID.5.1'], 'PID.5.1.1'); // Last Name

logger.info('Processing: ' + firstName + ' ' + lastName + ' (MRN: ' + patientMRN + ')');

// Escape single quotes for SQL safety (prevent SQL injection)
function esc(s) {
    return s ? String(s).replace(/'/g, "''") : '';
}

var dbConn = null;
var rs = null;

try {
    // ============================================
    // STEP 1: Connect to OpenEMR Database
    // ============================================
    dbConn = DatabaseConnectionFactory.createDatabaseConnection(
        'com.mysql.cj.jdbc.Driver',           // MySQL JDBC Driver
        'jdbc:mysql://localhost:3306/openemr', // Database URL
        'openemr',                             // Username
        'openemr'                              // Password
    );
    logger.info('Database connected');

    // ============================================
    // STEP 2: Check if patient already exists
    // ============================================
    var checkSql = "SELECT pid FROM patient_data WHERE pubpid = '" + esc(patientMRN) + "' LIMIT 1";
    rs = dbConn.executeCachedQuery(checkSql);

    if (rs.next()) {
        var existingPid = rs.getInt('pid');
        logger.info('Patient exists (pid=' + existingPid + ') - SKIPPING');
        rs.close();
        return msg;
    }
    rs.close();
    logger.info('Patient does not exist - proceeding with insert');

    // ============================================
    // STEP 3: Get next available patient ID
    // ============================================
    // Note: OpenEMR's pid field is NOT AUTO_INCREMENT
    // So we must manually calculate the next ID
    var nextPidSql = "SELECT COALESCE(MAX(pid), 0) + 1 AS next_pid FROM patient_data";
    rs = dbConn.executeCachedQuery(nextPidSql);
    rs.next();
    var nextPid = rs.getInt('next_pid');
    rs.close();
    logger.info('Next available pid: ' + nextPid);

    // ============================================
    // STEP 4: Insert patient into database
    // ============================================
    var insertSql =
        "INSERT INTO patient_data (pid, pubpid, fname, lname, date, regdate, status, language, financial, hipaa_allowemail) " +
        "VALUES (" +
        nextPid + ", '" +
        esc(patientMRN) + "', '" +
        esc(firstName) + "', '" +
        esc(lastName) + "', " +
        "NOW(), NOW(), 'active', 'English', 1, 'YES')";

    logger.info('Executing INSERT into patient_data...');
    var rows = dbConn.executeUpdate(insertSql);
    logger.info('SUCCESS! Inserted ' + rows + ' row(s) with pid=' + nextPid);

} catch (e) {
    logger.error('DATABASE ERROR: ' + e.toString());
    if (e.getMessage) {
        logger.error('Message: ' + e.getMessage());
    }
    var sw = new java.io.StringWriter();
    var pw = new java.io.PrintWriter(sw);
    e.printStackTrace(pw);
    logger.error('Stack: ' + sw.toString());

} finally {
    // ============================================
    // STEP 5: Clean up database connections
    // ============================================
    if (rs) {
        try { rs.close(); } catch(e) { logger.error('Close RS error: ' + e); }
    }
    if (dbConn) {
        try { dbConn.close(); logger.info('DB connection closed'); } catch(e) { logger.error('Close DB error: ' + e); }
    }
}

// Return the message for destinations to use
return msg;
```

---

### Step 5: Configure Destination (File Writer)

Click on **Destinations** tab → **Add New Destination**

```
┌─────────────────────────────────────────┐
│ Destination Connector Settings           │
├─────────────────────────────────────────┤
│ Connector Type: File Writer             │
│                                          │
│ Directory: C:/mirth/hl7_messages/       │
│                                          │
│ File Name Pattern:                       │
│   MSG_${DATE('yyyyMMdd')}_${UUID()}.hl7│
│                                          │
│ File Exists Action: Append               │
│                                          │
│ Encoding: UTF-8                         │
└─────────────────────────────────────────┘
```

**What this does:**
- Saves each HL7 message to a file for archival
- Creates unique filename with date and UUID
- Example: `MSG_20251117_abc123.hl7`

---

### Step 6: Deploy Channel

1. Click **Save** button
2. Click **Deploy** button (green arrow)
3. Channel status should show **Started** (green dot)

---

## Code Walkthrough

Let's understand the Interface Wizard backend code that generates HL7 messages:

### File: `backend/app/services/hl7_service.py`

```python
# ============================================
# HL7 Service - Generates HL7 Messages
# ============================================

from hl7apy.core import Message, Segment
import socket
from datetime import datetime

class HL7Service:
    def __init__(self, mllp_host='localhost', mllp_port=6661):
        """Initialize HL7 service with Mirth Connect connection details"""
        self.mllp_host = mllp_host
        self.mllp_port = mllp_port

    def create_patient_message(self, patient_data):
        """
        Creates an HL7 ADT^A04 message (Patient Registration)

        Args:
            patient_data: Dict with keys: mrn, first_name, last_name, dob, gender

        Returns:
            HL7 message string
        """

        # ============================================
        # STEP 1: Create HL7 Message
        # ============================================
        msg = Message("ADT_A04")  # ADT = Admission/Discharge/Transfer
                                   # A04 = Register Patient
        msg.msh.msh_3 = "InterfaceWizard"  # Sending Application
        msg.msh.msh_4 = "Facility"         # Sending Facility
        msg.msh.msh_5 = "OpenEMR"          # Receiving Application
        msg.msh.msh_7 = datetime.now().strftime("%Y%m%d%H%M%S")  # Timestamp
        msg.msh.msh_9 = "ADT^A04"          # Message Type
        msg.msh.msh_10 = f"MSG{datetime.now().strftime('%Y%m%d%H%M%S')}"  # Message ID
        msg.msh.msh_11 = "P"               # Processing ID (P=Production, T=Test)
        msg.msh.msh_12 = "2.5"             # HL7 Version

        # ============================================
        # STEP 2: Add Patient Identification (PID)
        # ============================================
        msg.pid.pid_1 = "1"                                    # Set ID
        msg.pid.pid_3 = f"{patient_data['mrn']}^^^MRN"        # Patient ID (MRN)
        msg.pid.pid_5 = f"{patient_data['last_name']}^{patient_data['first_name']}"  # Name
        msg.pid.pid_7 = patient_data.get('dob', '')           # Date of Birth (YYYYMMDD)
        msg.pid.pid_8 = patient_data.get('gender', 'U')       # Gender (M/F/U)

        # Convert to HL7 string format
        hl7_string = msg.to_er7()

        return hl7_string

    def send_message(self, hl7_message):
        """
        Sends HL7 message to Mirth Connect via MLLP protocol

        MLLP Protocol Format:
        <VT> + HL7 Message + <FS> + <CR>

        Where:
        <VT> = Vertical Tab (0x0B) - Start of message
        <FS> = File Separator (0x1C) - End of message
        <CR> = Carriage Return (0x0D) - End of transmission
        """

        # ============================================
        # STEP 1: Wrap message with MLLP envelope
        # ============================================
        VT = b'\x0b'   # Start Block (Vertical Tab)
        FS = b'\x1c'   # End Block (File Separator)
        CR = b'\x0d'   # Carriage Return

        mllp_message = VT + hl7_message.encode('utf-8') + FS + CR

        # ============================================
        # STEP 2: Connect to Mirth Connect via TCP
        # ============================================
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.mllp_host, self.mllp_port))

        # ============================================
        # STEP 3: Send message
        # ============================================
        sock.sendall(mllp_message)

        # ============================================
        # STEP 4: Receive ACK (acknowledgment)
        # ============================================
        response = sock.recv(1024)

        # ============================================
        # STEP 5: Close connection
        # ============================================
        sock.close()

        return response.decode('utf-8')
```

---

### File: `backend/app/services/ai_service.py`

```python
# ============================================
# AI Service - Interprets Commands and Creates Patients
# ============================================

class AIService:
    def __init__(self):
        self.hl7_service = HL7Service()

    def process_command(self, user_message):
        """
        Processes natural language command
        Example: "Create patient John Doe"
        """

        # ============================================
        # STEP 1: Send to OpenAI to extract intent and data
        # ============================================
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Extract patient data from command"},
                {"role": "user", "content": user_message}
            ]
        )

        patient_data = {
            "mrn": "12345",
            "first_name": "John",
            "last_name": "Doe",
            "dob": "19800101",
            "gender": "M"
        }

        # ============================================
        # STEP 2: Generate HL7 message
        # ============================================
        hl7_message = self.hl7_service.create_patient_message(patient_data)

        # ============================================
        # STEP 3: Send to Mirth Connect
        # ============================================
        ack = self.hl7_service.send_message(hl7_message)

        return {
            "status": "success",
            "message": "Patient created successfully",
            "hl7_sent": hl7_message,
            "ack_received": ack
        }
```

---

## Complete Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                    COMPLETE MESSAGE FLOW                              │
└──────────────────────────────────────────────────────────────────────┘

USER TYPES: "Create patient John Doe"
    │
    ▼
┌─────────────────────────────────────────┐
│ FRONTEND (Angular/React)                │
│                                         │
│ POST /api/v1/command                    │
│ {                                       │
│   "content": "Create patient John Doe"  │
│ }                                       │
└────────────┬────────────────────────────┘
             │ HTTP
             ▼
┌─────────────────────────────────────────┐
│ BACKEND (FastAPI - ai_service.py)       │
│                                         │
│ 1. Receives command                     │
│ 2. Sends to OpenAI GPT-4               │
│ 3. Extracts: first_name=John,          │
│             last_name=Doe               │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ HL7 SERVICE (hl7_service.py)            │
│                                         │
│ Creates HL7 ADT^A04 message:           │
│ ┌───────────────────────────────────┐  │
│ │MSH|^~\&|InterfaceWizard|...       │  │
│ │PID|1||12345||Doe^John||19800101|M|│  │
│ └───────────────────────────────────┘  │
└────────────┬────────────────────────────┘
             │ MLLP (TCP Port 6661)
             │ <VT> + HL7 Message + <FS><CR>
             ▼
┌────────────────────────────────────────────────────┐
│ MIRTH CONNECT - Channel                           │
│                                                    │
│ ┌────────────────────────────────────────────┐   │
│ │ SOURCE CONNECTOR (MLLP Listener)           │   │
│ │ - Listening on port 6661                   │   │
│ │ - Receives: <VT>MSH|^~\&|...<FS><CR>       │   │
│ │ - Parses into HL7 object                   │   │
│ └────────────┬───────────────────────────────┘   │
│              │                                     │
│              ▼                                     │
│ ┌────────────────────────────────────────────┐   │
│ │ SOURCE TRANSFORMER (JavaScript)            │   │
│ │                                            │   │
│ │ var pid = msg['PID']                       │   │
│ │ var firstName = pid['PID.5']['PID.5.2']    │   │
│ │   → extracts "John"                        │   │
│ │ var lastName = pid['PID.5']['PID.5.1']     │   │
│ │   → extracts "Doe"                         │   │
│ │                                            │   │
│ │ Database INSERT:                           │   │
│ │ INSERT INTO patient_data                   │   │
│ │   (pid, fname, lname, ...)                 │   │
│ │ VALUES (13, 'John', 'Doe', ...)            │   │
│ └────────────┬───────────────────────────────┘   │
│              │                                     │
│              ▼                                     │
│ ┌────────────────────────────────────────────┐   │
│ │ DESTINATION (File Writer)                  │   │
│ │                                            │   │
│ │ Saves to:                                  │   │
│ │ C:/mirth/hl7_messages/MSG_20251117.hl7     │   │
│ └────────────────────────────────────────────┘   │
│                                                    │
└────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ OPENEMR DATABASE (MySQL)                │
│                                         │
│ patient_data table:                     │
│ ┌─────┬────────┬───────┬─────────┐    │
│ │ pid │ fname  │ lname │ pubpid  │    │
│ ├─────┼────────┼───────┼─────────┤    │
│ │ 13  │ John   │ Doe   │ 12345   │    │
│ └─────┴────────┴───────┴─────────┘    │
└─────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ OPENEMR WEB UI                          │
│                                         │
│ Patient List:                           │
│ ✓ John Doe (MRN: 12345)                │
└─────────────────────────────────────────┘
```

---

## Troubleshooting

### Problem 1: "Connection Refused" Error

**Symptoms:**
```
ERROR: Connection refused to localhost:6661
```

**Solution:**
1. Check if Mirth Connect is running
2. Check if channel is deployed and started (green status)
3. Verify port 6661 is not blocked by firewall

---

### Problem 2: "Duplicate entry '0' for key 'pid'"

**Symptoms:**
```
java.sql.SQLException: Duplicate entry '0' for key 'pid'
```

**Cause:** OpenEMR's `pid` field is NOT auto-increment

**Solution:** Use `SELECT MAX(pid) + 1` to get next ID (already in our code)

---

### Problem 3: Messages Not Appearing in OpenEMR Dashboard

**Symptoms:**
- Patient appears in database (phpMyAdmin)
- Patient does NOT appear in OpenEMR Messages dashboard

**Cause:** Direct database insert bypasses OpenEMR's notification system

**Solution:** Need to insert into `onsite_messages` or use OpenEMR API (in progress)

---

### Problem 4: "Unknown column 'user' in field list"

**Symptoms:**
```
ERROR: Unknown column 'user' in 'field list'
```

**Cause:** Different OpenEMR versions have different table schemas

**Solution:** Check actual table structure using:
```sql
SHOW COLUMNS FROM onsite_messages;
```

---

## Summary

### What We Built:

1. **Frontend** → User types natural language commands
2. **Backend** → Converts commands to HL7 messages
3. **Mirth Connect** → Receives HL7, extracts data, inserts into database
4. **OpenEMR** → Patient appears in system

### Why This Architecture?

- ✅ **Standards-based:** Uses HL7 (healthcare industry standard)
- ✅ **Scalable:** Can add more systems easily
- ✅ **Auditable:** All messages saved to files
- ✅ **Flexible:** Change database without touching backend
- ✅ **Reliable:** Mirth handles retries and errors

### Key Takeaways:

1. **Mirth Connect = Middleware** - Sits between systems
2. **Source Transformer** - Best place for database operations
3. **HL7 = Healthcare Language** - Standard message format
4. **MLLP = Delivery Method** - How HL7 travels over network

---

## Next Steps

1. **Add diagnosis support** - Store diabetes/cancer diagnosis
2. **Add OpenEMR API integration** - Make messages appear in dashboard
3. **Add error notifications** - Alert user when insert fails
4. **Add patient search** - Query existing patients

---

**Document Created:** 2025-11-17
**Version:** 1.0
**Author:** Interface Wizard Team
