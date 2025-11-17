# Backend → Mirth Connect Integration Guide

## 📚 Table of Contents
1. [Overview](#overview)
2. [Required Libraries](#required-libraries)
3. [Configuration Files](#configuration-files)
4. [Backend Code Structure](#backend-code-structure)
5. [HL7 Service Implementation](#hl7-service-implementation)
6. [MLLP Protocol Implementation](#mllp-protocol-implementation)
7. [Complete Code Walkthrough](#complete-code-walkthrough)
8. [Testing the Integration](#testing-the-integration)

---

## Overview

### What We're Building

```
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND → MIRTH FLOW                          │
└─────────────────────────────────────────────────────────────────┘

User Command
    ↓
AI Service (processes command)
    ↓
HL7 Service (creates HL7 message)
    ↓
MLLP Client (sends via TCP/IP)
    ↓
Mirth Connect (receives on port 6661)
    ↓
Database Insert
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend Framework** | FastAPI | REST API server |
| **HL7 Library** | hl7apy | Create/parse HL7 messages |
| **Network Protocol** | TCP Sockets | MLLP communication |
| **Database** | MySQL | Patient storage |
| **AI** | OpenAI GPT-4 | Natural language processing |

---

## Required Libraries

### Python Dependencies

All libraries are specified in `backend/requirements.txt`:

```txt
# requirements.txt

# ============================================
# Web Framework
# ============================================
fastapi==0.104.1          # Modern web framework for APIs
uvicorn[standard]==0.24.0 # ASGI server to run FastAPI
pydantic==2.5.0           # Data validation
pydantic-settings==2.1.0  # Settings management

# ============================================
# HL7 Messaging (CRITICAL FOR MIRTH)
# ============================================
hl7apy==1.3.4             # Create and parse HL7 v2.x messages
                          # This library builds the HL7 format that Mirth understands

# ============================================
# Database
# ============================================
pymysql==1.1.0            # MySQL database driver
sqlalchemy==2.0.23        # Database ORM
cryptography==41.0.7      # For MySQL SSL connections

# ============================================
# AI Integration
# ============================================
openai==1.3.5             # OpenAI GPT API client
python-dotenv==1.0.0      # Load .env files

# ============================================
# Utilities
# ============================================
python-multipart==0.0.6   # File upload support
```

### Why Each Library?

#### 1. **hl7apy** (Most Important for Mirth!)
```python
from hl7apy.core import Message, Segment

# Creates HL7 messages in the exact format Mirth expects:
# MSH|^~\&|InterfaceWizard|...
# PID|1||12345||Doe^John||...
```

**Without hl7apy:**
- ❌ Would need to manually construct HL7 strings
- ❌ Easy to make formatting errors
- ❌ Hard to maintain

**With hl7apy:**
- ✅ Automatic HL7 formatting
- ✅ Validates message structure
- ✅ Easy to add segments

#### 2. **Socket** (Built-in Python)
```python
import socket

# Creates TCP connection to Mirth on port 6661
# Sends messages using MLLP protocol
```

**What it does:**
- Opens TCP connection to Mirth Connect
- Sends HL7 messages wrapped in MLLP envelope
- Receives ACK (acknowledgment) responses

#### 3. **FastAPI**
```python
from fastapi import FastAPI

# Provides REST API endpoints for frontend
# Example: POST /api/v1/command
```

---

## Configuration Files

### 1. `.env` File (CRITICAL!)

**Location:** `backend/.env`

This file contains ALL configuration needed to connect to Mirth and OpenEMR.

```bash
# ============================================
# APPLICATION SETTINGS
# ============================================
APP_NAME=Interface Wizard
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true

# ============================================
# SERVER CONFIGURATION
# ============================================
HOST=0.0.0.0              # Listen on all interfaces
PORT=8000                 # Backend API port

# ============================================
# DATABASE CONFIGURATION (OpenEMR MySQL)
# ============================================
DB_HOST=localhost         # MySQL server location
DB_PORT=3306              # MySQL port
DB_NAME=openemr           # OpenEMR database name
DB_USER=openemr           # Database username
DB_PASSWORD=openemr       # Database password

# ============================================
# OPENEMR CONFIGURATION
# ============================================
OPENEMR_USERNAME=administrator
OPENEMR_PASSWORD=Admin@123456
OPENEMR_BASE_URL=http://localhost/openemr

# ============================================
# MIRTH CONNECT CONFIGURATION
# ⚠️ CRITICAL FOR HL7 MESSAGE DELIVERY
# ============================================
MIRTH_HOST=localhost      # Where Mirth Connect is running
MIRTH_PORT=8443           # Mirth Admin API port (not used for messages)
MIRTH_USERNAME=admin      # Mirth admin username
MIRTH_PASSWORD=Admin@123  # Mirth admin password
MIRTH_USE_HTTPS=true

# ============================================
# HL7 MLLP CONFIGURATION
# ⚠️ MOST IMPORTANT FOR SENDING MESSAGES TO MIRTH
# ============================================
MLLP_HOST=localhost       # Where Mirth MLLP listener is running
MLLP_PORT=6661            # MUST MATCH Mirth channel listener port!
MLLP_TIMEOUT=30           # Seconds to wait for response

# ============================================
# OPENAI CONFIGURATION
# ============================================
OPENAI_API_KEY=sk-proj-xxx...  # Your OpenAI API key
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# ============================================
# FHIR CONFIGURATION (Optional)
# ============================================
FHIR_BASE_URL=http://localhost/openemr/apis/default/fhir
FHIR_VERSION=R4

# ============================================
# SECURITY
# ============================================
SECRET_KEY=interface-wizard-secret-key-2024-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ============================================
# LOGGING
# ============================================
LOG_LEVEL=INFO
LOG_FILE=logs/interface-wizard.log

# ============================================
# CORS (Frontend Access)
# ============================================
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001", "http://localhost:4200", "http://localhost:4201"]
```

### 2. `config.py` - Loads .env Variables

**Location:** `backend/app/config.py`

```python
# ============================================
# Configuration Management
# Loads settings from .env file
# ============================================

from pydantic_settings import BaseSettings
from typing import List
import json

class Settings(BaseSettings):
    """
    Application settings loaded from .env file

    Pydantic automatically:
    - Reads .env file
    - Validates types
    - Provides defaults
    """

    # Application
    APP_NAME: str = "Interface Wizard"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "openemr"
    DB_USER: str = "openemr"
    DB_PASSWORD: str = "openemr"

    # OpenEMR
    OPENEMR_USERNAME: str = "administrator"
    OPENEMR_PASSWORD: str = "Admin@123456"
    OPENEMR_BASE_URL: str = "http://localhost/openemr"

    # Mirth Connect
    MIRTH_HOST: str = "localhost"
    MIRTH_PORT: int = 8443
    MIRTH_USERNAME: str = "admin"
    MIRTH_PASSWORD: str = "Admin@123"
    MIRTH_USE_HTTPS: bool = True

    # HL7 MLLP - CRITICAL FOR MIRTH COMMUNICATION
    MLLP_HOST: str = "localhost"      # Where to send HL7 messages
    MLLP_PORT: int = 6661             # Mirth listener port
    MLLP_TIMEOUT: int = 30            # Connection timeout

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TEMPERATURE: float = 0.7

    # FHIR
    FHIR_BASE_URL: str = "http://localhost/openemr/apis/default/fhir"
    FHIR_VERSION: str = "R4"

    # Security
    SECRET_KEY: str = "interface-wizard-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/interface-wizard.log"

    # CORS
    CORS_ORIGINS: str = '["http://localhost:3000"]'

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS JSON string into list"""
        try:
            return json.loads(self.CORS_ORIGINS)
        except:
            return ["http://localhost:3000"]

    @property
    def database_url(self) -> str:
        """Construct database connection URL"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"              # Load from .env file
        case_sensitive = True          # Environment variable names are case-sensitive

# Create global settings instance
settings = Settings()
```

---

## Backend Code Structure

### Project Directory Layout

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration (loads .env)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── command.py     # POST /api/v1/command endpoint
│   │           └── health.py      # GET /health endpoint
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py          # OpenAI integration
│   │   ├── hl7_service.py         # ⭐ HL7 MESSAGE CREATION
│   │   ├── mllp_client.py         # ⭐ MIRTH COMMUNICATION
│   │   ├── patient_service.py     # Patient data management
│   │   └── database_service.py    # Database operations
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── command.py             # Request/Response models
│   │   └── patient.py             # Patient data models
│   │
│   └── utils/
│       ├── __init__.py
│       └── logger.py              # Logging configuration
│
├── .env                           # ⭐ CONFIGURATION FILE
├── requirements.txt               # ⭐ PYTHON DEPENDENCIES
└── run.py                         # Application entry point
```

---

## HL7 Service Implementation

### File: `backend/app/services/hl7_service.py`

This is the CORE file that creates HL7 messages for Mirth!

```python
# ============================================
# HL7 SERVICE - Creates HL7 Messages
# ============================================

from hl7apy.core import Message, Segment
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class HL7Service:
    """
    Service for creating HL7 v2.x messages

    HL7 (Health Level 7) is the standard format for healthcare
    data exchange. Mirth Connect expects messages in this format.
    """

    def __init__(self):
        """Initialize HL7 Service"""
        logger.info("HL7 Service initialized")

    def create_adt_a04_message(self, patient_data: Dict[str, Any]) -> str:
        """
        Create HL7 ADT^A04 message (Register Patient)

        ADT = Admission, Discharge, Transfer
        A04 = Register a patient

        Args:
            patient_data: Dictionary containing:
                - mrn: Medical Record Number
                - first_name: Patient first name
                - last_name: Patient last name
                - middle_name: Patient middle name (optional)
                - dob: Date of birth (YYYYMMDD)
                - gender: M/F/U
                - diagnosis: Medical diagnosis (optional)

        Returns:
            String containing HL7 message in ER7 format

        Example Output:
            MSH|^~\&|InterfaceWizard|Facility|||20251117101530||ADT^A04|MSG001|P|2.5
            PID|1||12345^^^MRN||Doe^John^M||19800101|M|||123 Main St^^Boston^MA^02101
        """

        try:
            logger.info(f"Creating ADT^A04 message for patient: {patient_data.get('first_name')} {patient_data.get('last_name')}")

            # ============================================
            # STEP 1: Create Message Structure
            # ============================================
            # ADT_A04 is a predefined message type in hl7apy
            msg = Message("ADT_A04", version="2.5")

            # ============================================
            # STEP 2: Populate MSH (Message Header) Segment
            # ============================================
            # MSH contains metadata about the message itself

            msg.msh.msh_3 = "InterfaceWizard"           # Sending Application
            msg.msh.msh_4 = "Facility"                  # Sending Facility
            msg.msh.msh_5 = "OpenEMR"                   # Receiving Application
            msg.msh.msh_6 = "OpenEMR"                   # Receiving Facility
            msg.msh.msh_7 = datetime.now().strftime("%Y%m%d%H%M%S")  # Message timestamp
            msg.msh.msh_9 = "ADT^A04"                   # Message Type
            msg.msh.msh_10 = f"MSG{datetime.now().strftime('%Y%m%d%H%M%S%f')}"  # Unique message ID
            msg.msh.msh_11 = "P"                        # Processing ID (P=Production, T=Test)
            msg.msh.msh_12 = "2.5"                      # HL7 Version

            # ============================================
            # STEP 3: Populate EVN (Event) Segment
            # ============================================
            # EVN describes the event that triggered the message

            msg.evn.evn_1 = "A04"                       # Event Type Code
            msg.evn.evn_2 = datetime.now().strftime("%Y%m%d%H%M%S")  # Event timestamp

            # ============================================
            # STEP 4: Populate PID (Patient Identification) Segment
            # ============================================
            # PID contains all patient demographic information
            # This is the MOST IMPORTANT segment for Mirth to extract data from!

            # Set ID
            msg.pid.pid_1 = "1"

            # Patient Identifier (Medical Record Number)
            # Format: MRN^^^AssigningAuthority
            mrn = patient_data.get('mrn', f"MRN{datetime.now().strftime('%Y%m%d%H%M%S')}")
            msg.pid.pid_3 = f"{mrn}^^^MRN"

            # Patient Name
            # Format: LastName^FirstName^MiddleName
            first_name = patient_data.get('first_name', '')
            last_name = patient_data.get('last_name', '')
            middle_name = patient_data.get('middle_name', '')

            if middle_name:
                msg.pid.pid_5 = f"{last_name}^{first_name}^{middle_name}"
            else:
                msg.pid.pid_5 = f"{last_name}^{first_name}"

            # Date of Birth
            # Format: YYYYMMDD
            dob = patient_data.get('dob', '')
            if dob:
                msg.pid.pid_7 = dob

            # Gender
            # M = Male, F = Female, U = Unknown
            gender = patient_data.get('gender', 'U')
            msg.pid.pid_8 = gender

            # Address (optional)
            address = patient_data.get('address', '')
            if address:
                msg.pid.pid_11 = address

            # Phone (optional)
            phone = patient_data.get('phone', '')
            if phone:
                msg.pid.pid_13 = phone

            # ============================================
            # STEP 5: Add DG1 (Diagnosis) Segment (Optional)
            # ============================================
            diagnosis = patient_data.get('diagnosis', '')
            if diagnosis:
                # Add DG1 segment for diagnosis
                dg1 = Segment("DG1", version="2.5")
                dg1.dg1_1 = "1"                         # Set ID
                dg1.dg1_3 = f"{diagnosis}^{diagnosis}"  # Diagnosis code and description
                dg1.dg1_4 = diagnosis                   # Diagnosis description
                dg1.dg1_6 = "F"                         # Diagnosis type (F = Final)
                msg.add(dg1)

            # ============================================
            # STEP 6: Convert to ER7 Format
            # ============================================
            # ER7 is the pipe-delimited text format: MSH|^~\&|...
            # This is what Mirth Connect expects to receive

            hl7_string = msg.to_er7()

            logger.info(f"✓ HL7 message created successfully")
            logger.debug(f"HL7 Message:\n{hl7_string}")

            return hl7_string

        except Exception as e:
            logger.error(f"Error creating HL7 message: {str(e)}")
            raise

    def create_adt_a08_message(self, patient_data: Dict[str, Any]) -> str:
        """
        Create HL7 ADT^A08 message (Update Patient Information)

        ADT^A08 is used to update existing patient demographics
        Similar to A04 but indicates an update rather than new registration
        """
        # Implementation similar to A04, but with A08 event type
        pass

    def create_oru_r01_message(self, lab_data: Dict[str, Any]) -> str:
        """
        Create HL7 ORU^R01 message (Lab Results)

        ORU^R01 is used to send observation/lab results
        """
        # Implementation for lab results
        pass
```

---

## MLLP Protocol Implementation

### File: `backend/app/services/mllp_client.py`

This file handles the TCP/IP communication with Mirth Connect using MLLP protocol.

```python
# ============================================
# MLLP CLIENT - Communicates with Mirth Connect
# ============================================

import socket
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)

class MLLPClient:
    """
    MLLP (Minimal Lower Layer Protocol) Client

    MLLP is the standard protocol for sending HL7 messages over TCP/IP.
    It wraps HL7 messages with special control characters.

    MLLP Message Format:
    <VT> + HL7_MESSAGE + <FS> + <CR>

    Where:
    - <VT> = Vertical Tab (0x0B) - Start of Block
    - HL7_MESSAGE = The actual HL7 message content
    - <FS> = File Separator (0x1C) - End of Block
    - <CR> = Carriage Return (0x0D) - End of Message
    """

    # MLLP Control Characters (defined by HL7 standard)
    VT = b'\x0b'   # Start Block (Vertical Tab)
    FS = b'\x1c'   # End Block (File Separator)
    CR = b'\x0d'   # Carriage Return

    def __init__(self,
                 host: str = None,
                 port: int = None,
                 timeout: int = None):
        """
        Initialize MLLP Client

        Args:
            host: Mirth Connect server hostname (default from .env)
            port: MLLP listener port (default from .env)
            timeout: Connection timeout in seconds (default from .env)
        """
        self.host = host or settings.MLLP_HOST
        self.port = port or settings.MLLP_PORT
        self.timeout = timeout or settings.MLLP_TIMEOUT

        logger.info(f"MLLP Client initialized: {self.host}:{self.port}")

    def send_message(self, hl7_message: str) -> dict:
        """
        Send HL7 message to Mirth Connect via MLLP

        Args:
            hl7_message: HL7 message string in ER7 format

        Returns:
            Dictionary containing:
                - success: bool
                - ack: ACK message from Mirth
                - error: Error message if failed

        Process:
            1. Wrap HL7 message with MLLP envelope
            2. Connect to Mirth via TCP
            3. Send wrapped message
            4. Receive ACK response
            5. Close connection
        """

        sock = None

        try:
            logger.info(f"Connecting to Mirth Connect at {self.host}:{self.port}")

            # ============================================
            # STEP 1: Wrap HL7 message with MLLP envelope
            # ============================================
            # MLLP Format: <VT> + MESSAGE + <FS> + <CR>

            mllp_message = self.VT + hl7_message.encode('utf-8') + self.FS + self.CR

            logger.debug(f"MLLP wrapped message length: {len(mllp_message)} bytes")
            logger.debug(f"HL7 Message:\n{hl7_message}")

            # ============================================
            # STEP 2: Create TCP socket connection
            # ============================================
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)

            # ============================================
            # STEP 3: Connect to Mirth Connect
            # ============================================
            sock.connect((self.host, self.port))
            logger.info(f"✓ Connected to Mirth Connect")

            # ============================================
            # STEP 4: Send MLLP-wrapped HL7 message
            # ============================================
            sock.sendall(mllp_message)
            logger.info(f"✓ HL7 message sent ({len(mllp_message)} bytes)")

            # ============================================
            # STEP 5: Receive ACK (Acknowledgment) response
            # ============================================
            # Mirth will send back an ACK message indicating success/failure
            # ACK format: MSH|...|ACK|...\rMSA|AA|...  (AA = Application Accept)

            response = sock.recv(4096)  # Receive up to 4KB

            # Remove MLLP envelope from response
            if response.startswith(self.VT) and response.endswith(self.CR):
                response = response[1:-2]  # Remove <VT> at start and <FS><CR> at end

            response_str = response.decode('utf-8', errors='ignore')

            logger.info(f"✓ Received ACK from Mirth")
            logger.debug(f"ACK Response:\n{response_str}")

            # ============================================
            # STEP 6: Parse ACK to check if successful
            # ============================================
            # ACK codes:
            # - AA = Application Accept (Success)
            # - AE = Application Error
            # - AR = Application Reject

            is_success = 'MSA|AA' in response_str or 'MSA|CA' in response_str

            if is_success:
                logger.info("✓ Message accepted by Mirth (ACK: AA)")
            else:
                logger.warning(f"⚠ Message not fully accepted. ACK: {response_str}")

            return {
                "success": is_success,
                "ack": response_str,
                "error": None
            }

        except socket.timeout:
            error_msg = f"Timeout connecting to Mirth at {self.host}:{self.port}"
            logger.error(error_msg)
            return {
                "success": False,
                "ack": None,
                "error": error_msg
            }

        except ConnectionRefusedError:
            error_msg = f"Connection refused to {self.host}:{self.port}. Is Mirth Connect running?"
            logger.error(error_msg)
            return {
                "success": False,
                "ack": None,
                "error": error_msg
            }

        except Exception as e:
            error_msg = f"Error sending HL7 message: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "ack": None,
                "error": error_msg
            }

        finally:
            # ============================================
            # STEP 7: Clean up - Close socket connection
            # ============================================
            if sock:
                try:
                    sock.close()
                    logger.info("✓ Connection closed")
                except:
                    pass

    def test_connection(self) -> bool:
        """
        Test if Mirth Connect is reachable

        Returns:
            True if connection successful, False otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.host, self.port))
            sock.close()
            logger.info(f"✓ Mirth Connect is reachable at {self.host}:{self.port}")
            return True
        except:
            logger.error(f"✗ Cannot reach Mirth Connect at {self.host}:{self.port}")
            return False
```

---

## Complete Code Walkthrough

### How Everything Works Together

#### Step 1: User sends command via Frontend

```typescript
// frontend-angular/src/app/chat/chat.service.ts

sendMessage(content: string) {
  return this.http.post('http://localhost:8000/api/v1/command', {
    content: "Create patient John Doe with diabetes"
  });
}
```

#### Step 2: Backend receives request

```python
# backend/app/api/v1/endpoints/command.py

from fastapi import APIRouter, HTTPException
from app.services.ai_service import AIService
from app.models.command import CommandRequest, CommandResponse

router = APIRouter()
ai_service = AIService()

@router.post("/command", response_model=CommandResponse)
async def process_command(request: CommandRequest):
    """
    Process natural language command

    Example: "Create patient John Doe"

    Flow:
    1. Receive command from frontend
    2. Send to AI service for processing
    3. AI service extracts patient data
    4. Creates HL7 message
    5. Sends to Mirth via MLLP
    6. Returns result to frontend
    """
    try:
        result = await ai_service.process_command(request.content)
        return CommandResponse(
            success=True,
            message=result['message'],
            data=result.get('data')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### Step 3: AI Service processes command

```python
# backend/app/services/ai_service.py

from app.services.hl7_service import HL7Service
from app.services.mllp_client import MLLPClient
import openai
from app.config import settings

class AIService:
    def __init__(self):
        self.hl7_service = HL7Service()
        self.mllp_client = MLLPClient()
        openai.api_key = settings.OPENAI_API_KEY

    async def process_command(self, user_message: str):
        """
        Process natural language command

        Args:
            user_message: "Create patient John Doe with diabetes"

        Returns:
            Result dictionary with success status
        """

        # ============================================
        # STEP 1: Extract intent and data using OpenAI
        # ============================================
        response = openai.ChatCompletion.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """Extract patient data from the command.
                    Return JSON: {
                        "action": "create_patient",
                        "first_name": "John",
                        "last_name": "Doe",
                        "diagnosis": "diabetes"
                    }"""
                },
                {"role": "user", "content": user_message}
            ]
        )

        # Parse AI response
        patient_data = json.loads(response.choices[0].message.content)

        # ============================================
        # STEP 2: Create HL7 message
        # ============================================
        hl7_message = self.hl7_service.create_adt_a04_message({
            'mrn': f"MRN{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'first_name': patient_data['first_name'],
            'last_name': patient_data['last_name'],
            'diagnosis': patient_data.get('diagnosis', ''),
            'dob': '19800101',  # Default or extract from command
            'gender': 'U'        # Default or extract from command
        })

        # ============================================
        # STEP 3: Send HL7 message to Mirth via MLLP
        # ============================================
        result = self.mllp_client.send_message(hl7_message)

        if result['success']:
            return {
                'message': f"Patient {patient_data['first_name']} {patient_data['last_name']} created successfully!",
                'data': {
                    'hl7_sent': hl7_message,
                    'ack_received': result['ack']
                }
            }
        else:
            raise Exception(f"Failed to send to Mirth: {result['error']}")
```

---

## Testing the Integration

### Test 1: Check if Mirth is reachable

```python
# Run this Python script to test connection

from app.services.mllp_client import MLLPClient

client = MLLPClient()

if client.test_connection():
    print("✓ Mirth Connect is reachable!")
else:
    print("✗ Cannot connect to Mirth. Check:")
    print("  1. Is Mirth Connect running?")
    print("  2. Is channel deployed and started?")
    print("  3. Is port 6661 correct?")
```

### Test 2: Send test HL7 message

```python
# backend/test_hl7.py

from app.services.hl7_service import HL7Service
from app.services.mllp_client import MLLPClient

# Create HL7 message
hl7_service = HL7Service()
hl7_msg = hl7_service.create_adt_a04_message({
    'mrn': 'TEST12345',
    'first_name': 'Test',
    'last_name': 'Patient',
    'dob': '19900101',
    'gender': 'M'
})

print("HL7 Message:")
print(hl7_msg)
print("\n" + "="*50 + "\n")

# Send to Mirth
mllp_client = MLLPClient()
result = mllp_client.send_message(hl7_msg)

print(f"Success: {result['success']}")
print(f"ACK: {result['ack']}")
if result['error']:
    print(f"Error: {result['error']}")
```

### Test 3: Full end-to-end test

```bash
# 1. Start backend
cd backend
./venv/Scripts/python.exe -m uvicorn app.main:app --reload

# 2. Use curl to send command
curl -X POST http://localhost:8000/api/v1/command \
  -H "Content-Type: application/json" \
  -d '{"content": "Create patient John Doe"}'

# 3. Check response
# Should see: {"success": true, "message": "Patient created..."}

# 4. Check Mirth Connect dashboard
# Should see: Received: 1, Sent: 1

# 5. Check database
# Run in phpMyAdmin:
SELECT * FROM patient_data ORDER BY pid DESC LIMIT 1;
```

---

## Summary - Required Files Checklist

### ✅ Configuration Files:
- [ ] `backend/.env` - All environment variables
- [ ] `backend/requirements.txt` - Python dependencies
- [ ] `backend/app/config.py` - Configuration loader

### ✅ Code Files:
- [ ] `backend/app/services/hl7_service.py` - Creates HL7 messages
- [ ] `backend/app/services/mllp_client.py` - Sends to Mirth
- [ ] `backend/app/services/ai_service.py` - Processes commands
- [ ] `backend/app/api/v1/endpoints/command.py` - API endpoint

### ✅ Libraries Used:
- [ ] `hl7apy` - HL7 message creation
- [ ] `socket` (built-in) - TCP/IP communication
- [ ] `fastapi` - Web framework
- [ ] `openai` - AI processing
- [ ] `pydantic` - Configuration management

### ✅ Key Configuration Values:
- [ ] `MLLP_HOST=localhost` - Where Mirth runs
- [ ] `MLLP_PORT=6661` - Must match Mirth channel listener port
- [ ] `MLLP_TIMEOUT=30` - Connection timeout

---

**Document Version:** 1.0
**Last Updated:** 2025-11-17
