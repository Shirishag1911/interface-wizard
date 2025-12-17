#!/usr/bin/env python3
"""
Smart HL7 Message Generator with OpenAI integration and FastAPI REST API.

Features:
- REST API endpoints with Swagger documentation
- Console mode (original functionality preserved)
- Excel/CSV file upload and processing
- HL7 message generation and validation
- Mirth Connect integration

Usage:
  API Mode:    python main.py --api
  Console Mode: python main.py --console (or just python main.py)
"""

import os
import sys
import re
import socket
import time
import argparse
from datetime import datetime
from tkinter import Tk, filedialog
from typing import List, Optional, Dict, Any
from io import BytesIO

import pandas as pd
import hl7  # pip install hl7
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Attempt to import OpenAI SDK
try:
    from openai import OpenAI
    OPENAI_SDK_AVAILABLE = True
except Exception:
    OPENAI_SDK_AVAILABLE = False

# ==================== CONFIGURATION ====================
OPENAI_API_KEY = "your-openai-api-key-here"  # TODO: Replace with your actual OpenAI API key
MIRTH_HOST = "localhost"
MIRTH_PORT = 6661

FIELD_TIERS = {
    "SYSTEM_FIELDS": {"MSH": [11, 12], "EVN": [2]},
    "CONTEXTUAL_FIELDS": {"PV1": [2], "ORC": [1], "OBR": [25], "OBX": [11]},
    "CRITICAL_FIELDS": {
        "MSH": [9],
        "PID": [3, 5, 7, 8],
        "ORC": [2, 3],
        "OBR": [1, 2, 3, 4, 7],
        "OBX": [2, 3, 5],
    },
}

TRIGGER_EVENT_MAPPING = {
    "A01": "I", "A02": "I", "A03": "I", "A04": "O", "A05": "P",
    "A08": "I", "A11": "I", "A13": "I",
}

# ==================== PYDANTIC MODELS ====================
class HL7GenerationRequest(BaseModel):
    """Request model for generating HL7 messages from text command"""
    command: str
    trigger_event: Optional[str] = "ADT-A01"

class HL7ValidationResponse(BaseModel):
    """Response model for HL7 validation"""
    is_valid: bool
    missing_fields: List[str] = []
    message: str

class HL7GenerationResponse(BaseModel):
    """Response model for HL7 generation"""
    hl7_message: str
    validation: HL7ValidationResponse
    patient_info: Optional[Dict[str, Any]] = None

class MirthSendResponse(BaseModel):
    """Response model for sending to Mirth"""
    success: bool
    message: str
    acknowledgment: Optional[str] = None

class BatchProcessingResponse(BaseModel):
    """Response model for batch processing"""
    total_patients: int
    successful: int
    failed: int
    messages: List[Dict[str, Any]]

# ==================== FASTAPI APP ====================
app = FastAPI(
    title="Smart HL7 Message Generator API",
    description="""
    ## 🏥 Smart HL7 Message Generator

    This API provides endpoints for generating, validating, and sending HL7 v2.x messages.

    ### Features:
    - ✨ **Auto-populate** system fields (MSH-11, MSH-12, EVN-2)
    - 🧠 **Smart inference** of contextual information
    - ✅ **Validation** of critical patient data
    - 📁 **Bulk processing** via Excel/CSV upload
    - 🔗 **Mirth Connect** integration
    - 🤖 **AI-powered** generation using OpenAI GPT-4

    ### Workflow:
    1. Upload Excel/CSV or provide text command
    2. Generate HL7 message(s)
    3. Validate critical fields
    4. Send to Mirth Connect (optional)

    ### Message Types Supported:
    - ADT (Admission/Discharge/Transfer)
    - ORU (Observation Results)
    - ORM (Orders)
    - Custom trigger events
    """,
    version="2.0.0",
    contact={
        "name": "Interface Wizard Team",
        "email": "support@example.com"
    }
)

# Initialize client wrapper globally
client_wrapper = None

# ==================== Helper Functions (same as before) ====================
def _normalize_colname(name: str) -> str:
    """Normalize a column name for comparison"""
    if not isinstance(name, str):
        return ""
    s = name.strip().lower()
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s)
    s = s.replace(" ", "_")
    return s

def _find_column(df, candidates):
    """Find best matching column name in dataframe"""
    norm_map = {_normalize_colname(c): c for c in df.columns}
    for cand in candidates:
        nc = _normalize_colname(cand)
        if nc in norm_map:
            return norm_map[nc]
    cand_tokens = [_normalize_colname(c) for c in candidates]
    for dfcol in df.columns:
        ndf = _normalize_colname(dfcol)
        for token in cand_tokens:
            if token and token in ndf:
                return dfcol
    return None

# ==================== CLIENT WRAPPER ====================
class ClientWrapper:
    """Wrapper for OpenAI generation with configured API key"""

    def __init__(self):
        self.openai_key = OPENAI_API_KEY
        self.has_remote = bool(self.openai_key and OPENAI_SDK_AVAILABLE)

        if self.openai_key and not OPENAI_SDK_AVAILABLE:
            print("⚠ openai package not installed or import failed. Remote generation disabled.")
            self.has_remote = False
        elif self.has_remote:
            print("✓ OpenAI API configured and ready")

    def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 2000) -> str:
        """Main entry: use remote API if available, otherwise fallback"""
        if self.has_remote:
            try:
                return self.generate_via_api(prompt, temperature=temperature, max_tokens=max_tokens)
            except Exception as e:
                print(f"⚠ Remote generation failed: {e}. Falling back to local generator.")
                return fallback_hl7_generator(prompt)
        else:
            return fallback_hl7_generator(prompt)

    def generate_via_api(self, prompt: str, temperature: float = 0.3, max_tokens: int = 2000) -> str:
        """Calls OpenAI Chat Completions to generate HL7 text"""
        if not self.openai_key:
            raise RuntimeError("No OPENAI_API_KEY available for remote generation.")

        client = OpenAI(api_key=self.openai_key)
        messages = [
            {"role": "system", "content": "You are an expert HL7 v2.x message generator. Output ONLY the HL7 message with no explanations."},
            {"role": "user", "content": prompt},
        ]

        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = resp.choices[0].message.content
            content = re.sub(r"^```(?:hl7)?\s*", "", content)
            content = re.sub(r"\s*```$", "", content)
            return content.strip()
        except Exception:
            raise

# ==================== FALLBACK HL7 GENERATOR ====================
def fallback_hl7_generator(command_text: str) -> str:
    """Deterministic local HL7 generator for offline testing"""
    now = datetime.now().strftime("%Y%m%d%H%M%S")

    trig_match = re.search(r"Trigger Event[:\s]*(ADT[- ]?A\d{2}|A\d{2})", command_text, re.IGNORECASE)
    trigger = trig_match.group(1).replace(" ", "-").upper() if trig_match else "ADT-A01"

    msh = ["MSH", "^~\\&", "SMART_APP", "SMART_FAC", "REC_APP", "REC_FAC", now, "", f"{trigger.replace('-', '^')}", "", "P", "2.5"]

    id_match = re.search(r"Patient ID[:\s]*([A-Za-z0-9\-_]+)", command_text, re.IGNORECASE)
    pid3 = id_match.group(1).strip() if id_match else ""

    name_match = re.search(r"Patient Name[:\s]*([A-Za-z\-]+)\s+([A-Za-z\-]+)", command_text, re.IGNORECASE)
    if name_match:
        pid5 = f"{name_match.group(1)}^{name_match.group(2)}"
    else:
        pid5 = ""

    dob_match = re.search(r"Date of Birth[:\s]*([0-9]{4}[-/]?[0-9]{2}[-/]?[0-9]{2}|[0-9]{8})", command_text, re.IGNORECASE)
    if not dob_match:
        dob_match = re.search(r"DOB[:\s]*([0-9]{4}[-/]?[0-9]{2}[-/]?[0-9]{2}|[0-9]{8})", command_text, re.IGNORECASE)
    pid7 = dob_match.group(1).replace("-", "").replace("/", "") if dob_match else ""

    sex_match = re.search(r"Gender[:\s]*(M|F|Male|Female|U|Unknown)", command_text, re.IGNORECASE)
    if sex_match:
        gender_val = sex_match.group(1).upper()
        if gender_val.startswith('M'):
            pid8 = "M"
        elif gender_val.startswith('F'):
            pid8 = "F"
        else:
            pid8 = "U"
    else:
        pid8 = ""

    address_match = re.search(r"Address[:\s]*([^\n]+)", command_text, re.IGNORECASE)
    pid11 = address_match.group(1).strip() if address_match else ""

    msh_line = "|".join(msh)
    evn_line = f"EVN|{trigger.split('-')[-1]}|{now}"

    pid_fields = ["PID", "1", pid3, "", pid5, "", pid7, pid8, "", "", pid11]
    pid_line = "|".join(pid_fields)

    pv1_class = "I" if any(x in trigger for x in ("A01", "A02", "A03")) else "O"
    pv1_line = f"PV1|1|{pv1_class}"

    return "\n".join([msh_line, evn_line, pid_line, pv1_line])

# ==================== HL7 GENERATION ====================
def generate_hl7_message(client: ClientWrapper, command: str) -> str:
    """Build prompt and call client.generate()"""
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    prompt = f"""You are an HL7 v2.x message generator. Generate a valid HL7 message based on the following command:

{command}

CRITICAL REQUIREMENTS:
- Use HL7 v2.x pipe-delimited format.
- Auto-populate MSH-11='P', MSH-12='2.5', EVN-2='{current_time}'
- Only include segments explicitly required or implied.
- For ADTs include MSH, EVN, PID, PV1 minimum.
- Output ONLY the HL7 message text (no explanation).
"""
    return client.generate(prompt, temperature=0.2, max_tokens=1500)

# ==================== HL7 VALIDATION ====================
def validate_hl7_structure(hl7_message_text: str):
    """Validate basic HL7 structure"""
    try:
        hl7_formatted = hl7_message_text.replace("\n", "\r")
        parsed_message = hl7.parse(hl7_formatted)
        return True, parsed_message
    except Exception as e:
        return False, str(e)

def validate_required_fields_api(hl7_message_text: str) -> HL7ValidationResponse:
    """Validate using 3-tier system - API version"""
    is_valid_structure, parsed_message = validate_hl7_structure(hl7_message_text)
    if not is_valid_structure:
        return HL7ValidationResponse(
            is_valid=False,
            missing_fields=[],
            message=f"Invalid HL7 structure: {parsed_message}"
        )

    missing_critical_fields = []
    validation_passed = True
    critical_fields = FIELD_TIERS["CRITICAL_FIELDS"]

    for segment in parsed_message:
        segment_name = str(segment[0])
        if segment_name in critical_fields:
            required_field_indices = critical_fields[segment_name]
            for field_index in required_field_indices:
                try:
                    field_value = str(segment[field_index]).strip()
                    if not field_value:
                        missing_critical_fields.append(f"{segment_name}-{field_index}")
                        validation_passed = False
                except IndexError:
                    missing_critical_fields.append(f"{segment_name}-{field_index}")
                    validation_passed = False

    return HL7ValidationResponse(
        is_valid=validation_passed,
        missing_fields=missing_critical_fields,
        message="Validation passed" if validation_passed else "Missing critical fields"
    )

# ==================== MIRTH INTEGRATION ====================
def send_to_mirth(hl7_message: str, host: str = MIRTH_HOST, port: int = MIRTH_PORT) -> tuple[bool, str]:
    """Send HL7 message to Mirth Connect via TCP/IP (MLLP)"""
    sock = None
    try:
        START_BLOCK = b"\x0b"
        END_BLOCK = b"\x1c\x0d"
        hl7_bytes = hl7_message.replace("\n", "\r").encode("utf-8")
        mllp_message = START_BLOCK + hl7_bytes + END_BLOCK

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15)  # Increased timeout to 15 seconds
        sock.connect((host, port))
        sock.sendall(mllp_message)

        response = sock.recv(4096)
        ack_message = ""
        if response:
            ack_message = response.decode("utf-8", errors="ignore").strip("\x0b\x1c\x0d")
            if "AA" in ack_message or "CA" in ack_message:
                return True, ack_message
            else:
                return False, ack_message
        return True, "Message sent successfully (no ACK received)"
    except socket.timeout:
        return False, "Connection timeout! Make sure Mirth is running and the channel is started."
    except ConnectionRefusedError:
        return False, "Connection refused! Check Mirth is running and channel is listening."
    except Exception as e:
        return False, f"Error sending to Mirth: {str(e)}"
    finally:
        # Always close the socket to prevent resource leaks
        if sock:
            try:
                sock.close()
            except:
                pass

# ==================== BATCH PROCESSING ====================
def process_excel_batch(df: pd.DataFrame, trigger_event: str = "ADT-A01") -> List[Dict[str, Any]]:
    """Process Excel/CSV data and generate HL7 messages for all rows"""
    global client_wrapper

    candidate_map = {
        'patient_last_name': ["Patient Last Name", "Last Name", "Lastname", "last_name", "surname"],
        'patient_first_name': ["Patient First Name", "First Name", "Firstname", "given_name", "first_name"],
        'dob': ["DOB", "Date of Birth", "birthdate", "date_of_birth"],
        'gender': ["Gender", "Sex"],
        'address1': ["Address 1", "Address1", "Street", "address", "addr1"],
        'address2': ["Address 2", "Address2", "addr2"],
        'city': ["City", "Town"],
        'state': ["State", "Province", "region"],
        'zipcode': ["Zipcode", "Zip", "Postal Code", "PostalCode"],
        'patient_id': ["Patient ID", "MRN", "Medical Record Number", "patient_id", "id"]
    }

    mapping = {}
    for key, candidates in candidate_map.items():
        found = _find_column(df, candidates)
        mapping[key] = found

    results = []
    for index, row in df.iterrows():
        # Extract patient data
        last_name = row.get(mapping.get('patient_last_name')) if mapping.get('patient_last_name') else ''
        first_name = row.get(mapping.get('patient_first_name')) if mapping.get('patient_first_name') else ''
        dob = row.get(mapping.get('dob')) if mapping.get('dob') else ''
        gender = row.get(mapping.get('gender')) if mapping.get('gender') else ''
        address1 = row.get(mapping.get('address1')) if mapping.get('address1') else ''
        address2 = row.get(mapping.get('address2')) if mapping.get('address2') else ''
        city = row.get(mapping.get('city')) if mapping.get('city') else ''
        state = row.get(mapping.get('state')) if mapping.get('state') else ''
        zipcode = row.get(mapping.get('zipcode')) if mapping.get('zipcode') else ''
        patient_id = row.get(mapping.get('patient_id')) if mapping.get('patient_id') else f"PAT{str(index + 1).zfill(6)}"

        # Normalize DOB
        try:
            if isinstance(dob, str):
                dob_formatted = dob.replace("-", "").replace("/", "")
            elif pd.notna(dob):
                dob_formatted = pd.to_datetime(dob).strftime("%Y%m%d")
            else:
                dob_formatted = ""
        except Exception:
            dob_formatted = str(dob)

        parts = [address1, address2, city, state, zipcode]
        full_address = ", ".join([str(p).strip() for p in parts if p and str(p).strip() != "nan"])

        # Build command
        command = f"""
Trigger Event: {trigger_event}
Patient ID: {patient_id}
Patient Name: {last_name} {first_name}
Date of Birth: {dob_formatted}
Gender: {gender}
Address: {full_address}
Create an {trigger_event} message for patient {first_name} {last_name}, ID {patient_id}, DOB {dob_formatted}, Gender {gender}, Address: {full_address}
"""

        # Generate HL7 message
        try:
            hl7_message = generate_hl7_message(client_wrapper, command)
            validation = validate_required_fields_api(hl7_message)

            results.append({
                "row_number": index + 2,
                "patient_id": patient_id,
                "patient_name": f"{first_name} {last_name}".strip(),
                "hl7_message": hl7_message,
                "validation": validation.model_dump(),
                "status": "success" if validation.is_valid else "validation_failed"
            })

            # Add delay to prevent overwhelming Mirth Connect
            time.sleep(1.0)  # 1 second delay between messages to prevent crashes

        except Exception as e:
            results.append({
                "row_number": index + 2,
                "patient_id": patient_id,
                "patient_name": f"{first_name} {last_name}".strip(),
                "error": str(e),
                "status": "error"
            })

    return results

# ==================== API ENDPOINTS ====================

@app.on_event("startup")
async def startup_event():
    """Initialize client wrapper on startup"""
    global client_wrapper
    client_wrapper = ClientWrapper()
    print("\n" + "=" * 80)
    print("🚀 Smart HL7 Message Generator API Started")
    print("=" * 80)
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print(f"🔗 Mirth Connect: {MIRTH_HOST}:{MIRTH_PORT}")
    print(f"🤖 OpenAI Enabled: {client_wrapper.has_remote}")
    print("=" * 80 + "\n")

@app.get("/", tags=["General"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Smart HL7 Message Generator API",
        "version": "2.0.0",
        "description": "Generate, validate, and send HL7 v2.x messages",
        "documentation": "/docs",
        "health": "/health",
        "features": [
            "HL7 message generation from text",
            "Bulk processing from Excel/CSV",
            "HL7 message validation",
            "Mirth Connect integration",
            "AI-powered generation (OpenAI GPT-4)"
        ]
    }

@app.get("/health", tags=["General"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "openai_available": client_wrapper.has_remote if client_wrapper else False,
        "mirth_config": f"{MIRTH_HOST}:{MIRTH_PORT}"
    }

@app.post("/api/generate-hl7", response_model=HL7GenerationResponse, tags=["HL7 Generation"])
async def generate_hl7_from_command(request: HL7GenerationRequest):
    """
    Generate HL7 message from natural language command

    **Example command:**
    ```
    Create an ADT-A01 message for patient John Doe,
    ID 12345, DOB 1985-03-15, Gender M,
    Address: 123 Main St, Boston, MA 02101
    ```

    **Returns:**
    - Generated HL7 message
    - Validation results
    - Patient information extracted
    """
    try:
        hl7_message = generate_hl7_message(client_wrapper, request.command)
        validation = validate_required_fields_api(hl7_message)

        return HL7GenerationResponse(
            hl7_message=hl7_message,
            validation=validation,
            patient_info={
                "trigger_event": request.trigger_event,
                "command": request.command
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating HL7 message: {str(e)}")

@app.post("/api/validate-hl7", response_model=HL7ValidationResponse, tags=["HL7 Validation"])
async def validate_hl7_message(hl7_message: str = Form(...)):
    """
    Validate an HL7 message

    **Validates:**
    - HL7 structure (parsing)
    - Critical fields (PID, MSH, etc.)
    - Required segments

    **Returns:**
    - Validation status
    - List of missing fields
    - Validation message
    """
    try:
        validation = validate_required_fields_api(hl7_message)
        return validation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating HL7 message: {str(e)}")

@app.post("/api/send-to-mirth", response_model=MirthSendResponse, tags=["Mirth Integration"])
async def send_hl7_to_mirth(hl7_message: str = Form(...)):
    """
    Send HL7 message to Mirth Connect

    **Sends via:**
    - MLLP protocol (TCP/IP)
    - Port: 6661 (default)

    **Returns:**
    - Success status
    - Acknowledgment message from Mirth
    """
    try:
        success, ack = send_to_mirth(hl7_message)
        return MirthSendResponse(
            success=success,
            message="Message sent successfully" if success else "Failed to send message",
            acknowledgment=ack if ack else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending to Mirth: {str(e)}")

@app.post("/api/upload-excel", response_model=BatchProcessingResponse, tags=["Bulk Processing"])
async def upload_and_process_excel(
    file: UploadFile = File(..., description="Excel or CSV file with patient data"),
    trigger_event: str = Form("ADT-A01", description="HL7 trigger event (e.g., ADT-A01, ADT-A04)"),
    send_to_mirth_flag: bool = Form(True, description="Automatically send to Mirth after generation (default: True)")
):
    """
    Upload Excel/CSV file, generate HL7 messages, and send to Mirth Connect

    **Workflow:**
    1. Read Excel/CSV file
    2. Generate HL7 messages for each patient
    3. Validate critical fields
    4. **Automatically send to Mirth Connect** (default behavior)
    5. Mirth processes and inserts into OpenEMR database

    **Accepts:**
    - Excel files (.xlsx, .xls)
    - CSV files (.csv)

    **Required Columns (flexible naming):**
    - Patient ID / MRN
    - First Name / Patient First Name
    - Last Name / Patient Last Name
    - DOB / Date of Birth
    - Gender / Sex
    - Address fields (optional)

    **Returns:**
    - Total patients processed
    - Number successful/failed
    - Individual HL7 messages with validation
    - Mirth send status and acknowledgments

    **Note:** Set send_to_mirth_flag=false to only generate HL7 without sending
    """
    try:
        # Read file
        contents = await file.read()

        if file.filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(contents))
        else:
            df = pd.read_excel(BytesIO(contents))

        # Process all patients (generate HL7 messages)
        results = process_excel_batch(df, trigger_event)

        # Send to Mirth (default: True)
        mirth_successful = 0
        mirth_failed = 0

        if send_to_mirth_flag:
            print(f"\n📤 Sending {len(results)} messages to Mirth Connect...")
            for idx, result in enumerate(results, 1):
                if result.get("status") == "success":
                    print(f"  [{idx}/{len(results)}] Sending: {result['patient_name']}...")
                    success, ack = send_to_mirth(result["hl7_message"])
                    result["mirth_sent"] = success
                    result["mirth_ack"] = ack

                    if success:
                        mirth_successful += 1
                        print(f"    ✓ Sent successfully")
                    else:
                        mirth_failed += 1
                        print(f"    ❌ Failed: {ack}")

                    # Delay between sends (already in process_excel_batch, but adding here too)
                    time.sleep(0.2)

            print(f"✓ Mirth sending complete: {mirth_successful} successful, {mirth_failed} failed\n")

        successful = sum(1 for r in results if r.get("status") == "success")
        failed = len(results) - successful

        return BatchProcessingResponse(
            total_patients=len(results),
            successful=successful,
            failed=failed,
            messages=results
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/api/supported-events", tags=["Reference"])
async def get_supported_trigger_events():
    """
    Get list of supported HL7 trigger events

    **Returns:**
    - List of trigger events with descriptions
    - Patient class mappings
    """
    return {
        "trigger_events": {
            "ADT-A01": "Admit/Register Patient (Inpatient)",
            "ADT-A02": "Transfer Patient (Inpatient)",
            "ADT-A03": "Discharge Patient (Inpatient)",
            "ADT-A04": "Register Outpatient",
            "ADT-A05": "Pre-Admit Patient",
            "ADT-A08": "Update Patient Information",
            "ADT-A11": "Cancel Admit",
            "ADT-A13": "Cancel Discharge"
        },
        "patient_class_mapping": TRIGGER_EVENT_MAPPING
    }

# ==================== CONSOLE MODE (Original Functionality) ====================
def upload_excel_file():
    """Upload Excel/CSV file using file dialog"""
    print("\n📁 Opening file dialog...")
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    filename = filedialog.askopenfilename(
        title="Select Excel/CSV File",
        filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")],
    )
    root.destroy()
    if not filename:
        print("❌ No file selected!")
        return None
    print(f"✓ Selected file: {os.path.basename(filename)}")
    try:
        if filename.lower().endswith(".csv"):
            df = pd.read_csv(filename)
        else:
            df = pd.read_excel(filename)
        return df
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

def validate_required_fields(hl7_message_text: str):
    """Validate using 3-tier system - Console version with print statements"""
    print("\n" + "=" * 80)
    print("SMART VALIDATION - CRITICAL FIELDS ONLY")
    print("=" * 80)
    print("ℹ️  System fields (MSH-11, MSH-12, EVN-2) are auto-populated")
    print("ℹ️  Contextual fields (PV1-2, OBR-25, OBX-11) have smart defaults")
    print("ℹ️  Only validating critical patient/clinical data")
    print("=" * 80)

    is_valid_structure, parsed_message = validate_hl7_structure(hl7_message_text)
    if not is_valid_structure:
        print(f"❌ Invalid HL7 structure: {parsed_message}")
        return False, ["Invalid HL7 message structure"]

    missing_critical_fields = []
    validation_passed = True
    critical_fields = FIELD_TIERS["CRITICAL_FIELDS"]

    for segment in parsed_message:
        segment_name = str(segment[0])
        if segment_name in critical_fields:
            print(f"\n✓ Checking {segment_name} segment (Critical Fields)...")
            required_field_indices = critical_fields[segment_name]
            for field_index in required_field_indices:
                try:
                    field_value = str(segment[field_index]).strip()
                    if not field_value:
                        missing_critical_fields.append(f"{segment_name}-{field_index}")
                        print(f"  ❌ {segment_name}-{field_index}: MISSING (User must provide)")
                        validation_passed = False
                    else:
                        display_value = field_value[:50] + "..." if len(field_value) > 50 else field_value
                        print(f"  ✓ {segment_name}-{field_index}: {display_value}")
                except IndexError:
                    missing_critical_fields.append(f"{segment_name}-{field_index}")
                    print(f"  ❌ {segment_name}-{field_index}: MISSING")
                    validation_passed = False

    print("\n" + "=" * 80)
    if validation_passed:
        print("✅ VALIDATION PASSED - All critical fields are present!")
    else:
        print("❌ VALIDATION FAILED - Missing critical user data:")
        for field in missing_critical_fields:
            print(f"   - {field}")
    print("=" * 80 + "\n")
    return validation_passed, missing_critical_fields

def display_hl7_details(hl7_message_text: str):
    """Display parsed HL7 segment details"""
    is_valid, parsed_message = validate_hl7_structure(hl7_message_text)
    if not is_valid:
        print("Cannot display details: invalid HL7 structure.")
        return
    print("\n" + "=" * 80)
    print("HL7 MESSAGE DETAILS")
    print("=" * 80)
    for segment in parsed_message:
        segment_name = str(segment[0])
        print(f"\n{segment_name} Segment:")
        def safe(idx):
            try:
                return str(segment[idx])
            except Exception:
                return ""
        if segment_name == "MSH":
            print(f"  Sending Application: {safe(3)}")
            print(f"  Sending Facility: {safe(4)}")
            print(f"  Message Type: {safe(9)}")
            print(f"  Processing ID: {safe(11)} (Auto)")
            print(f"  Version ID: {safe(12)} (Auto)")
        elif segment_name == "EVN":
            print(f"  Event Type: {safe(1)}")
            print(f"  Recorded Date/Time: {safe(2)} (Auto)")
        elif segment_name == "PID":
            print(f"  Patient ID: {safe(3)}")
            print(f"  Patient Name: {safe(5)}")
            print(f"  Date of Birth: {safe(7)}")
            print(f"  Sex: {safe(8)}")
        elif segment_name == "PV1":
            print(f"  Patient Class: {safe(2)} (Inferred)")
    print("=" * 80)

def console_main():
    """Original console mode functionality"""
    global client_wrapper

    print("=" * 80)
    print("SMART HL7 MESSAGE GENERATOR - CONSOLE MODE")
    print("=" * 80)
    print("✨ Auto-populates system fields")
    print("🧠 Infers contextual information")
    print("✅ Validates only critical patient data")
    print(f"🔗 Mirth: {MIRTH_HOST}:{MIRTH_PORT}")
    print("=" * 80)

    client_wrapper = ClientWrapper()
    print("\n✓ Client wrapper initialized (remote available: {})\n".format(client_wrapper.has_remote))

    while True:
        print("\n" + "=" * 80)
        print("UPLOAD EXCEL/CSV FILE")
        print("=" * 80)
        print("📁 Please select your Excel or CSV file")
        print("=" * 80)

        df = upload_excel_file()
        if df is None:
            retry = input("\nWould you like to try uploading again? (yes/no): ").strip().lower()
            if retry not in ("yes", "y"):
                break
            continue

        # Ask for trigger event
        print("\nSelect HL7 trigger event:")
        print("1. ADT-A01 (Admit/Register Patient)")
        print("2. ADT-A04 (Register Outpatient)")
        print("3. ADT-A08 (Update Patient Information)")
        choice = input("Enter choice (1-3, default=1): ").strip() or "1"

        trigger_map = {"1": "ADT-A01", "2": "ADT-A04", "3": "ADT-A08"}
        trigger_event = trigger_map.get(choice, "ADT-A01")

        # Process all patients
        results = process_excel_batch(df, trigger_event)

        print("\n" + "=" * 80)
        print(f"GENERATED {len(results)} HL7 MESSAGES")
        print("=" * 80)

        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['patient_name']} (Row {result['row_number']})")
            if result['status'] == 'success':
                print(f"   ✓ Valid: {result['validation']['is_valid']}")
                if not result['validation']['is_valid']:
                    print(f"   Missing: {', '.join(result['validation']['missing_fields'])}")
            else:
                print(f"   ❌ Error: {result.get('error', 'Unknown')}")

        # Ask to send to Mirth
        send = input("\nSend all valid messages to Mirth? (yes/no): ").strip().lower()
        if send in ("yes", "y"):
            for result in results:
                if result['status'] == 'success' and result['validation']['is_valid']:
                    print(f"\nSending: {result['patient_name']}")
                    success, ack = send_to_mirth(result['hl7_message'])
                    if success:
                        print("✓ Sent successfully")
                    else:
                        print(f"❌ Failed: {ack}")

        another = input("\nProcess another file? (yes/no): ").strip().lower()
        if another not in ("yes", "y"):
            break

    print("\n✓ Process completed! Goodbye.")

# ==================== MAIN ====================
def main():
    """Main entry point with mode selection"""
    parser = argparse.ArgumentParser(description="Smart HL7 Message Generator")
    parser.add_argument("--api", action="store_true", help="Run in API mode with Swagger")
    parser.add_argument("--console", action="store_true", help="Run in console mode (default)")
    parser.add_argument("--port", type=int, default=8000, help="API port (default: 8000)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="API host (default: 0.0.0.0)")

    args = parser.parse_args()

    # Default to console mode if no args
    if not args.api and not args.console:
        args.console = True

    if args.api:
        print("\n🚀 Starting API Mode...")
        print(f"📚 Swagger UI will be available at: http://localhost:{args.port}/docs")
        print(f"📖 ReDoc will be available at: http://localhost:{args.port}/redoc")
        print("\nPress CTRL+C to stop the server\n")
        uvicorn.run(app, host=args.host, port=args.port)
    else:
        console_main()

if __name__ == "__main__":
    main()
