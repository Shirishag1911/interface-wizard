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
import uuid
import asyncio
import logging
from datetime import datetime, timedelta
from tkinter import Tk, filedialog
from typing import List, Optional, Dict, Any, Tuple
from io import BytesIO
import json

import pandas as pd
import hl7  # pip install hl7
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
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

# ==================== LOGGING CONFIGURATION ====================
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('interface_wizard.log')
    ]
)
logger = logging.getLogger(__name__)

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

# ==================== NEW MODELS FOR PREVIEW/CONFIRMATION WORKFLOW ====================
class PatientRecord(BaseModel):
    """Individual patient record with UUID for preview"""
    index: int
    uuid: str  # Generated UUID for tracking
    firstName: str
    lastName: str
    dateOfBirth: str  # YYYY-MM-DD format
    gender: str  # "Male" | "Female" | "Other"
    mrn: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    validation_status: str  # "valid" | "invalid" | "warning"
    validation_messages: List[str] = []

class ValidationError(BaseModel):
    """Validation error details"""
    row: int
    field: str
    error: str
    value: Any
    severity: str  # "error" | "warning"

class UploadSession(BaseModel):
    """Upload session data stored in memory"""
    session_id: str
    upload_id: str
    file_name: str
    file_type: str  # "csv" | "excel"
    uploaded_at: str
    expires_at: str
    total_records: int
    parsed_records: List[PatientRecord]
    validation_errors: List[ValidationError]
    column_mapping: Dict[str, str]
    status: str  # "pending" | "processing" | "completed" | "failed"
    trigger_event: str

class UploadResponse(BaseModel):
    """Response for file upload with preview data"""
    session_id: str
    file_name: str
    file_type: str
    total_records: int
    valid_records: int
    invalid_records: int
    patients: List[PatientRecord]  # All parsed patient records
    validation_errors: List[ValidationError]
    column_mapping: Dict[str, str]
    expires_at: str
    timestamp: str

class ConfirmUploadRequest(BaseModel):
    """Request for confirming upload (Phase 2)"""
    session_id: str
    selected_indices: List[int] = []  # Empty array = all patients
    send_to_mirth: bool = True

class ConfirmUploadResponse(BaseModel):
    """Response for confirm and process"""
    upload_id: str
    status: str
    total_selected: int
    message: str
    stream_url: str

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

# ==================== CORS CONFIGURATION ====================
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
    allow_methods=["*"],              # Allow all HTTP methods
    allow_headers=["*"],              # Allow all headers
)

# Initialize client wrapper globally
client_wrapper = None

# ==================== IN-MEMORY STORAGE ====================
# Upload sessions storage (in-memory)
upload_sessions: Dict[str, Dict[str, Any]] = {}

# Dashboard statistics (in-memory)
dashboard_stats = {
    "total_processed": 0,
    "hl7_messages_generated": 0,
    "successful_sends": 0,
    "failed_sends": 0
}

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

# ==================== ENHANCED COLUMN MAPPING (FROM IMPLEMENTATION_PLAN) ====================
COLUMN_MAPPINGS = {
    "firstName": [
        "first name", "first_name", "firstname", "fname",
        "given name", "given_name", "givenname",
        "patient first name", "pateint first name"  # Support user's Excel format + typo
    ],
    "lastName": [
        "last name", "last_name", "lastname", "lname",
        "family name", "family_name", "familyname", "surname",
        "patient last name"  # Support user's Excel format
    ],
    "dateOfBirth": [
        "date of birth", "date_of_birth", "dob", "birth date",
        "birth_date", "birthdate", "birthday"
    ],
    "gender": [
        "gender", "sex", "m/f"
    ],
    "mrn": [
        "mrn", "medical record number", "medical_record_number",
        "patient id", "patient_id", "patientid"
    ],
    "phone": [
        "phone", "phone number", "phone_number", "telephone",
        "tel", "mobile", "cell"
    ],
    "email": [
        "email", "e-mail", "email address", "email_address"
    ],
    "address": [
        "address", "street", "street address", "street_address",
        "address line 1", "address_line_1", "address 1"  # Support "Address 1"
    ],
    "city": [
        "city", "town"
    ],
    "state": [
        "state", "province", "region"
    ],
    "zip": [
        "zip", "zip code", "zip_code", "zipcode", "postal code",
        "postal_code", "postalcode"
    ]
}

def normalize_column_name(column: str) -> Optional[str]:
    """
    Convert any column name variation to standard field name using intelligent fuzzy matching.

    Strategy:
    1. Exact match against predefined variations (backward compatibility)
    2. Fuzzy matching using key terms extraction
    3. Substring matching for compound words

    Args:
        column: Raw column name from CSV/Excel

    Returns:
        Standard field name (e.g., "firstName") or None if no match
    """
    if not column:
        return None

    normalized = column.lower().strip()

    # Strategy 1: Exact match (fastest, most reliable)
    for standard_field, variations in COLUMN_MAPPINGS.items():
        if normalized in variations:
            return standard_field

    # Strategy 2: Fuzzy matching with keyword detection
    # Define noise words to remove
    noise_words = {"patient", "person", "record", "data", "info", "information",
                   "field", "column", "value", "the", "a", "an"}

    # Define key terms for each field (ordered by priority - most specific first)
    field_keywords = {
        "firstName": ["first", "given", "fname"],
        "lastName": ["last", "family", "surname", "lname"],
        "dateOfBirth": ["birth", "dob", "born"],
        "gender": ["gender", "sex"],
        "email": ["email", "e-mail", "mail"],  # Check email before address (to avoid "email address" → "address")
        "phone": ["phone", "tel", "mobile", "cell"],
        "mrn": ["mrn"],  # Remove "number" to avoid false matches
        "address": ["address", "street", "addr"],
        "city": ["city", "town"],
        "state": ["state", "province", "region"],
        "zip": ["zip", "postal", "postcode"]
    }

    # Extract meaningful words from column name
    # Remove punctuation and split by common delimiters
    import re
    words = re.split(r'[_\s\-/]+', normalized)
    meaningful_words = [w for w in words if w and w not in noise_words]

    # First pass: Try exact keyword matches (most reliable)
    for standard_field, keywords in field_keywords.items():
        for keyword in keywords:
            for word in meaningful_words:
                if keyword == word:
                    logger.info(f"🔍 Fuzzy Match (exact): '{column}' → '{standard_field}' (keyword: '{keyword}')")
                    return standard_field

    # Second pass: Try substring matches (less reliable, more permissive)
    for standard_field, keywords in field_keywords.items():
        for keyword in keywords:
            for word in meaningful_words:
                # Only match if keyword is substantial part of word (avoid short substring matches)
                if len(keyword) >= 3 and (keyword in word or word in keyword):
                    logger.info(f"🔍 Fuzzy Match (substring): '{column}' → '{standard_field}' ('{keyword}' ↔ '{word}')")
                    return standard_field

    # Strategy 3: Special handling for common patterns
    # Handle "name" field (could be first or last)
    if normalized == "name" or normalized == "patient name":
        logger.warning(f"⚠️  Ambiguous column '{column}' - treating as firstName (consider renaming to 'first name' or 'last name')")
        return "firstName"

    # No match found
    logger.warning(f"❌ Could not map column '{column}' to any standard field")
    return None

def map_columns_with_llm(column_names: List[str], use_llm: bool = True) -> Dict[str, Any]:
    """
    Use LLM to intelligently map CSV/Excel column names to standard fields.

    This is the INTELLIGENT approach - LLM understands context and semantics,
    no need to maintain endless keyword lists.

    Args:
        column_names: List of column names from uploaded file
        use_llm: If True, use LLM; if False, fall back to fuzzy matching only

    Returns:
        Dictionary with:
        - mapping: Dict[str, str] - column_name -> standard_field
        - confidence: Dict[str, float] - confidence scores (0.0-1.0)
        - warnings: List[str] - validation warnings
        - unmapped: List[str] - columns that couldn't be mapped
    """

    result = {
        "mapping": {},
        "confidence": {},
        "warnings": [],
        "unmapped": []
    }

    if not use_llm or not OPENAI_SDK_AVAILABLE:
        logger.info("🔧 Using fallback fuzzy matching (LLM disabled or unavailable)")
        # Fall back to existing fuzzy matching
        for col in column_names:
            mapped = normalize_column_name(col)
            if mapped:
                result["mapping"][col] = mapped
                result["confidence"][col] = 0.7  # Fuzzy match confidence
            else:
                result["unmapped"].append(col)
        return result

    # Prepare LLM prompt
    standard_fields = {
        "firstName": "Patient's first/given name",
        "lastName": "Patient's last/family/surname",
        "dateOfBirth": "Date of birth (DOB)",
        "gender": "Gender/sex (Male/Female/Other)",
        "mrn": "Medical Record Number",
        "phone": "Phone/telephone/mobile number",
        "email": "Email address",
        "address": "Street address",
        "city": "City/town",
        "state": "State/province/region",
        "zip": "ZIP/postal code"
    }

    prompt = f"""You are a healthcare data mapping expert. Map the following CSV/Excel column names to standard patient data fields.

Available standard fields:
{json.dumps(standard_fields, indent=2)}

Column names from uploaded file:
{json.dumps(column_names, indent=2)}

Instructions:
1. Map each column to the most appropriate standard field
2. Provide confidence score (0.0-1.0) for each mapping
3. Flag ambiguous or unmappable columns
4. Handle typos intelligently (e.g., "Pateint" → firstName)
5. Handle compound names (e.g., "Email Address" → email)
6. Handle prefixes (e.g., "Patient First Name" → firstName)

Return ONLY a valid JSON object with this exact structure:
{{
  "mappings": [
    {{"column": "column_name", "field": "standard_field", "confidence": 0.95}},
    ...
  ],
  "warnings": ["warning message if ambiguous", ...],
  "unmapped": ["column_name if cannot map", ...]
}}

Example:
Input: ["Patient Last Name", "DOB", "Email Address"]
Output:
{{
  "mappings": [
    {{"column": "Patient Last Name", "field": "lastName", "confidence": 1.0}},
    {{"column": "DOB", "field": "dateOfBirth", "confidence": 1.0}},
    {{"column": "Email Address", "field": "email", "confidence": 0.95}}
  ],
  "warnings": [],
  "unmapped": []
}}"""

    try:
        logger.info(f"🤖 Sending {len(column_names)} column names to LLM for intelligent mapping...")

        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Fast and cost-effective for this task
            messages=[
                {"role": "system", "content": "You are a healthcare data mapping expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,  # Deterministic output
            max_tokens=1000
        )

        llm_output = response.choices[0].message.content.strip()
        logger.info(f"📥 LLM Response: {llm_output[:200]}...")

        # Parse LLM response
        # Remove markdown code blocks if present
        if "```json" in llm_output:
            llm_output = llm_output.split("```json")[1].split("```")[0].strip()
        elif "```" in llm_output:
            llm_output = llm_output.split("```")[1].split("```")[0].strip()

        llm_result = json.loads(llm_output)

        # Process mappings
        for mapping in llm_result.get("mappings", []):
            col = mapping["column"]
            field = mapping["field"]
            confidence = mapping.get("confidence", 0.8)

            result["mapping"][col] = field
            result["confidence"][col] = confidence

            logger.info(f"✅ LLM Mapping: '{col}' → '{field}' (confidence: {confidence:.2f})")

        result["warnings"] = llm_result.get("warnings", [])
        result["unmapped"] = llm_result.get("unmapped", [])

        # Log warnings
        for warning in result["warnings"]:
            logger.warning(f"⚠️  LLM Warning: {warning}")

        # Log unmapped columns
        for unmapped in result["unmapped"]:
            logger.warning(f"❌ LLM could not map: '{unmapped}'")

        logger.info(f"✅ LLM mapping complete: {len(result['mapping'])}/{len(column_names)} columns mapped")

    except Exception as e:
        logger.error(f"❌ LLM mapping failed: {e}")
        logger.info("🔄 Falling back to fuzzy matching...")

        # Fall back to fuzzy matching
        for col in column_names:
            mapped = normalize_column_name(col)
            if mapped:
                result["mapping"][col] = mapped
                result["confidence"][col] = 0.7
            else:
                result["unmapped"].append(col)

    return result

def parse_date_flexible(date_value: Any) -> Optional[str]:
    """
    Parse date from various formats to YYYY-MM-DD

    Supports:
    - MM/DD/YYYY
    - DD-MM-YYYY
    - YYYY-MM-DD
    - Month DD, YYYY
    - Excel serial date

    Returns: YYYY-MM-DD or None
    """
    if pd.isna(date_value):
        return None

    # Handle Excel serial dates
    if isinstance(date_value, (int, float)):
        try:
            dt = datetime(1899, 12, 30) + pd.Timedelta(days=date_value)
            return dt.strftime("%Y-%m-%d")
        except:
            return None

    # Handle string dates
    if isinstance(date_value, str):
        try:
            # Try pandas date parser first
            dt = pd.to_datetime(date_value)
            return dt.strftime("%Y-%m-%d")
        except:
            return None

    # Handle datetime objects
    if isinstance(date_value, datetime):
        return date_value.strftime("%Y-%m-%d")

    return None

def validate_patient_record(patient: Dict[str, Any]) -> tuple[str, List[str]]:
    """
    Validate a patient record and return status and messages

    Returns: (validation_status, validation_messages)
    """
    messages = []
    status = "valid"

    # Check required fields
    required_fields = ["firstName", "lastName", "dateOfBirth", "gender", "mrn"]
    for field in required_fields:
        if not patient.get(field):
            messages.append(f"Missing required field: {field}")
            status = "invalid"

    # Validate date of birth format
    dob = patient.get("dateOfBirth")
    if dob and not re.match(r"^\d{4}-\d{2}-\d{2}$", dob):
        messages.append(f"Invalid date format for DOB: {dob}")
        status = "warning" if status == "valid" else status

    # Validate gender
    gender = patient.get("gender", "").lower()
    if gender and gender not in ["m", "f", "male", "female", "other", "u", "unknown"]:
        messages.append(f"Invalid gender value: {gender}")
        status = "warning" if status == "valid" else status

    return status, messages

def parse_csv_with_preview(df: pd.DataFrame, file_name: str, trigger_event: str = "ADT-A01", use_llm_mapping: bool = True) -> Tuple[List[PatientRecord], List[ValidationError], Dict[str, str]]:
    """
    Parse CSV/Excel file and create PatientRecord objects with UUIDs

    Args:
        df: DataFrame from uploaded CSV/Excel
        file_name: Original filename
        trigger_event: HL7 trigger event type
        use_llm_mapping: If True, use LLM for intelligent column mapping; if False, use fuzzy matching

    Returns:
        - parsed_records: List of PatientRecord objects with UUIDs
        - validation_errors: List of validation errors
        - column_mapping: Mapping of actual columns to standard fields
    """
    parsed_records = []
    validation_errors = []
    column_mapping = {}

    # Build column mapping using LLM or fuzzy matching
    if use_llm_mapping:
        logger.info("🤖 Using LLM-based intelligent column mapping...")
        llm_result = map_columns_with_llm(list(df.columns), use_llm=True)
        column_mapping = llm_result["mapping"]

        # Add warnings to validation errors
        for warning in llm_result["warnings"]:
            validation_errors.append(ValidationError(
                row=0,
                field="column_mapping",
                error=warning,
                value=None,
                severity="warning"
            ))

        # Add unmapped columns to validation errors
        for unmapped in llm_result["unmapped"]:
            validation_errors.append(ValidationError(
                row=0,
                field=unmapped,
                error=f"Could not map column '{unmapped}' to any standard field",
                value=None,
                severity="warning"
            ))
    else:
        logger.info("🔧 Using fuzzy matching for column mapping...")
        for col in df.columns:
            standard_field = normalize_column_name(col)
            if standard_field:
                column_mapping[col] = standard_field

    # Iterate through rows and create PatientRecord objects
    for index, row in df.iterrows():
        try:
            # Extract fields using column mapping
            def get_field(field_name: str) -> Optional[str]:
                """Get field value using column mapping"""
                for col, std_field in column_mapping.items():
                    if std_field == field_name:
                        value = row.get(col)
                        if pd.notna(value):
                            return str(value).strip()
                return None

            # Extract patient data
            first_name = get_field("firstName") or ""
            last_name = get_field("lastName") or ""
            dob_raw = get_field("dateOfBirth")
            gender_raw = get_field("gender") or ""
            mrn = get_field("mrn") or f"MRN{str(index + 1).zfill(6)}"
            phone = get_field("phone")
            email = get_field("email")
            address = get_field("address")
            city = get_field("city")
            state = get_field("state")
            zip_code = get_field("zip")

            # Parse date of birth
            dob_formatted = parse_date_flexible(row.get(list(column_mapping.keys())[list(column_mapping.values()).index("dateOfBirth")]) if "dateOfBirth" in column_mapping.values() else None)
            if not dob_formatted and dob_raw:
                dob_formatted = dob_raw

            # Normalize gender
            gender_normalized = gender_raw.upper()[0] if gender_raw else "U"
            if gender_normalized not in ["M", "F", "O", "U"]:
                gender_normalized = "U"

            # Map to full gender name
            gender_map = {"M": "Male", "F": "Female", "O": "Other", "U": "Unknown"}
            gender = gender_map.get(gender_normalized, "Unknown")

            # Generate UUID for this patient
            patient_uuid = str(uuid.uuid4())

            # Create patient record
            patient_dict = {
                "index": index,
                "uuid": patient_uuid,
                "firstName": first_name,
                "lastName": last_name,
                "dateOfBirth": dob_formatted or "",
                "gender": gender,
                "mrn": mrn,
                "phone": phone,
                "email": email,
                "address": address,
                "city": city,
                "state": state,
                "zip": zip_code,
                "validation_status": "valid",
                "validation_messages": []
            }

            # Validate patient record
            validation_status, validation_msgs = validate_patient_record(patient_dict)
            patient_dict["validation_status"] = validation_status
            patient_dict["validation_messages"] = validation_msgs

            # Add validation errors to list if invalid
            if validation_status == "invalid":
                for msg in validation_msgs:
                    validation_errors.append(ValidationError(
                        row=index + 2,  # Excel row number (header is row 1)
                        field=msg.split(":")[0] if ":" in msg else "unknown",
                        error=msg,
                        value="",
                        severity="error"
                    ))

            # Create PatientRecord
            patient_record = PatientRecord(**patient_dict)
            parsed_records.append(patient_record)

        except Exception as e:
            # Add validation error for this row
            validation_errors.append(ValidationError(
                row=index + 2,
                field="parsing",
                error=f"Error parsing row: {str(e)}",
                value="",
                severity="error"
            ))

    return parsed_records, validation_errors, column_mapping

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
    message_control_id = str(uuid.uuid4())[:20]  # Generate unique message ID

    trig_match = re.search(r"Trigger Event[:\s]*(ADT[- ]?A\d{2}|A\d{2})", command_text, re.IGNORECASE)
    trigger = trig_match.group(1).replace(" ", "-").upper() if trig_match else "ADT-A01"

    # MSH segment with unique Message Control ID (MSH-10)
    msh = ["MSH", "^~\\&", "SMART_APP", "SMART_FAC", "REC_APP", "REC_FAC", now, "", f"{trigger.replace('-', '^')}", message_control_id, "P", "2.5"]

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

    # Correct HL7 v2.5 PID segment format
    # PID|SetID|PatientID(external)|PatientID(internal)|AlternatePatientID|PatientName|MothersMaidenName|DOB|Sex|PatientAlias|Race|PatientAddress
    pid_fields = ["PID", "1", "", pid3, "", pid5, "", pid7, pid8, "", "", pid11]
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
    """Send HL7 message to Mirth Connect via TCP/IP (MLLP) with detailed logging"""
    sock = None

    logger.info("="*80)
    logger.info("🚀 STARTING MIRTH TRANSMISSION")
    logger.info(f"📍 Target: {host}:{port}")
    logger.info(f"📏 HL7 Message Length: {len(hl7_message)} characters")

    # Extract patient info from message for logging
    try:
        lines = hl7_message.split("\n")
        msh_line = next((l for l in lines if l.startswith("MSH|")), "")
        pid_line = next((l for l in lines if l.startswith("PID|")), "")
        zpi_line = next((l for l in lines if l.startswith("ZPI|")), "")

        logger.info(f"📋 MSH Segment: {msh_line[:100]}...")
        logger.info(f"👤 PID Segment: {pid_line[:100]}...")
        if zpi_line:
            logger.info(f"🆔 ZPI Segment (UUID): {zpi_line}")
    except Exception as e:
        logger.warning(f"⚠️  Could not extract message details: {e}")

    try:
        START_BLOCK = b"\x0b"
        END_BLOCK = b"\x1c\x0d"
        hl7_bytes = hl7_message.replace("\n", "\r").encode("utf-8")
        mllp_message = START_BLOCK + hl7_bytes + END_BLOCK

        logger.info(f"📦 MLLP Message Size: {len(mllp_message)} bytes")
        logger.info(f"🔧 MLLP Envelope: START_BLOCK(0x0b) + HL7 + END_BLOCK(0x1c 0x0d)")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15)  # Increased timeout to 15 seconds
        logger.info(f"⏰ Socket timeout set to 15 seconds")

        logger.info(f"🔌 Attempting to connect to {host}:{port}...")
        sock.connect((host, port))
        logger.info(f"✅ CONNECTION ESTABLISHED to {host}:{port}")

        logger.info(f"📤 Sending MLLP message ({len(mllp_message)} bytes)...")
        sock.sendall(mllp_message)
        logger.info(f"✅ MESSAGE SENT SUCCESSFULLY")

        logger.info(f"⏳ Waiting for ACK response from Mirth...")
        response = sock.recv(4096)
        logger.info(f"📨 Received response ({len(response)} bytes)")

        ack_message = ""
        if response:
            ack_message = response.decode("utf-8", errors="ignore").strip("\x0b\x1c\x0d")
            logger.info(f"📬 ACK Message: {ack_message}")

            if "AA" in ack_message or "CA" in ack_message:
                logger.info(f"✅ ACK STATUS: POSITIVE (AA/CA found)")
                logger.info("="*80)
                return True, ack_message
            else:
                logger.warning(f"⚠️  ACK STATUS: NEGATIVE or UNKNOWN")
                logger.warning(f"ACK Content: {ack_message}")
                logger.info("="*80)
                return False, ack_message
        else:
            logger.warning(f"⚠️  No ACK received from Mirth (but message was sent)")
            logger.info("="*80)
            return True, "Message sent successfully (no ACK received)"

    except socket.timeout:
        error_msg = "Connection timeout! Make sure Mirth is running and the channel is started."
        logger.error(f"❌ TIMEOUT ERROR: {error_msg}")
        logger.error(f"   - Checked host: {host}")
        logger.error(f"   - Checked port: {port}")
        logger.error(f"   - Timeout: 15 seconds")
        logger.info("="*80)
        return False, error_msg

    except ConnectionRefusedError:
        error_msg = "Connection refused! Check Mirth is running and channel is listening."
        logger.error(f"❌ CONNECTION REFUSED ERROR")
        logger.error(f"   - Mirth Host: {host}")
        logger.error(f"   - Mirth Port: {port}")
        logger.error(f"   - Possible causes:")
        logger.error(f"     1. Mirth Connect is not running")
        logger.error(f"     2. Channel is not deployed/started")
        logger.error(f"     3. Wrong port number (check Mirth channel settings)")
        logger.error(f"     4. Firewall blocking connection")
        logger.info("="*80)
        return False, error_msg

    except Exception as e:
        error_msg = f"Error sending to Mirth: {str(e)}"
        logger.error(f"❌ UNEXPECTED ERROR: {error_msg}")
        logger.error(f"   - Exception type: {type(e).__name__}")
        logger.error(f"   - Exception details: {str(e)}")
        logger.info("="*80)
        return False, error_msg

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

# ==================== ASYNC BACKGROUND PROCESSING ====================
async def process_confirmed_patients(
    upload_id: str,
    selected_records: List[PatientRecord],
    trigger_event: str = "ADT-A01",
    send_to_mirth: bool = True
):
    """
    Background async task that processes confirmed patients with UUIDs

    This function processes PatientRecord objects that already have UUIDs assigned.

    Steps:
    1. Skip parsing (already done in preview phase)
    2. Skip selection (user already selected)
    3. Generate HL7 messages with UUID in ZPI segment
    4. Send to Mirth (if enabled)
    5. Complete
    """
    global client_wrapper, dashboard_stats

    logger.info("="*80)
    logger.info(f"🎯 STARTING CONFIRMED PATIENT PROCESSING")
    logger.info(f"📝 Upload ID: {upload_id}")
    logger.info(f"👥 Total Patients to Process: {len(selected_records)}")
    logger.info(f"⚙️  Trigger Event: {trigger_event}")
    logger.info(f"🔧 Send to Mirth: {send_to_mirth}")
    logger.info("="*80)

    session = upload_sessions[upload_id]

    try:
        # ========== STEP 1: Start Processing ==========
        session["current_step"] = 1
        session["step_status"] = "Confirmed - starting processing"
        logger.info(f"✅ STEP 1: Processing started")
        await asyncio.sleep(0.3)

        # ========== STEP 2: Generate HL7 Messages with UUIDs ==========
        session["current_step"] = 2
        session["generated_messages"] = []
        generated_count = 0

        logger.info(f"✅ STEP 2: Generating HL7 messages for {len(selected_records)} patients")

        for idx, patient in enumerate(selected_records, 1):
            logger.info(f"📝 Processing patient {idx}/{len(selected_records)}: {patient.firstName} {patient.lastName} (MRN: {patient.mrn}, UUID: {patient.uuid})")
            # Build command for HL7 generation
            command = f"""
Trigger Event: {trigger_event}
Patient ID: {patient.mrn}
Patient UUID: {patient.uuid}
Patient Name: {patient.lastName} {patient.firstName}
Date of Birth: {patient.dateOfBirth}
Gender: {patient.gender}
Address: {patient.address or ''}
City: {patient.city or ''}
State: {patient.state or ''}
Zip: {patient.zip or ''}
Phone: {patient.phone or ''}
Email: {patient.email or ''}
Create an {trigger_event} message for patient {patient.firstName} {patient.lastName}, ID {patient.mrn}, UUID {patient.uuid}, DOB {patient.dateOfBirth}, Gender {patient.gender}
"""

            # Generate HL7 message
            try:
                hl7_message = generate_hl7_message(client_wrapper, command)

                # Add custom ZPI segment with UUID
                hl7_message = add_zpi_segment_with_uuid(hl7_message, patient.uuid)

                validation = validate_required_fields_api(hl7_message)

                message_result = {
                    "row_number": patient.index + 2,
                    "patient_id": patient.mrn,
                    "patient_uuid": patient.uuid,
                    "patient_name": f"{patient.firstName} {patient.lastName}",
                    "hl7_message": hl7_message,
                    "validation": validation.model_dump(),
                    "status": "success" if validation.is_valid else "validation_failed"
                }

                session["generated_messages"].append(message_result)
                generated_count += 1
                session["step_status"] = f"Generated {generated_count}/{len(selected_records)} messages"

                # Update dashboard stats
                dashboard_stats["hl7_messages_generated"] += 1

                # Rate limiting: wait 1 second between messages
                await asyncio.sleep(1.0)

            except Exception as e:
                error_result = {
                    "row_number": patient.index + 2,
                    "patient_id": patient.mrn,
                    "patient_uuid": patient.uuid,
                    "patient_name": f"{patient.firstName} {patient.lastName}",
                    "error": str(e),
                    "status": "error"
                }
                session["generated_messages"].append(error_result)
                generated_count += 1
                session["step_status"] = f"Generated {generated_count}/{len(selected_records)} messages (with errors)"

        # ========== STEP 3: Send to Mirth (if enabled) ==========
        if send_to_mirth:
            session["current_step"] = 3
            session["step_status"] = "Sending to Mirth Connect..."
            session["mirth_successful"] = 0
            session["mirth_failed"] = 0
            sent_count = 0

            logger.info(f"✅ STEP 3: Sending {len(session['generated_messages'])} messages to Mirth Connect")
            logger.info(f"   Target: {MIRTH_HOST}:{MIRTH_PORT}")

            for idx, message in enumerate(session["generated_messages"], 1):
                if message.get("status") == "success":
                    try:
                        logger.info(f"📤 Sending message {idx}/{len(session['generated_messages'])} to Mirth...")
                        logger.info(f"   Patient: {message.get('patient_name')} (MRN: {message.get('patient_id')}, UUID: {message.get('patient_uuid')})")

                        success, ack = send_to_mirth(message["hl7_message"])
                        message["mirth_sent"] = success
                        message["mirth_ack"] = ack

                        if success:
                            session["mirth_successful"] += 1
                            dashboard_stats["successful_sends"] += 1
                            logger.info(f"✅ Message {idx} sent successfully to Mirth")
                            logger.info(f"   ACK received: {ack[:100] if len(ack) > 100 else ack}")
                        else:
                            session["mirth_failed"] += 1
                            dashboard_stats["failed_sends"] += 1
                            logger.error(f"❌ Message {idx} failed to send to Mirth")
                            logger.error(f"   ACK/Error: {ack}")

                        sent_count += 1
                        session["step_status"] = f"Sent {sent_count}/{len(session['generated_messages'])} to Mirth"

                        # Small delay between Mirth sends
                        await asyncio.sleep(0.2)

                    except Exception as e:
                        message["mirth_sent"] = False
                        message["mirth_error"] = str(e)
                        session["mirth_failed"] += 1
                        dashboard_stats["failed_sends"] += 1
                        logger.error(f"❌ Exception sending message {idx} to Mirth: {str(e)}")

            logger.info(f"📊 MIRTH TRANSMISSION SUMMARY:")
            logger.info(f"   ✅ Successful: {session['mirth_successful']}")
            logger.info(f"   ❌ Failed: {session['mirth_failed']}")
        else:
            session["current_step"] = 3
            session["step_status"] = "Skipped Mirth sending (disabled)"
            session["mirth_successful"] = 0
            session["mirth_failed"] = 0
            logger.info(f"⏭️  STEP 3: Skipped - send_to_mirth is disabled")
            await asyncio.sleep(0.3)

        # ========== STEP 4: Complete ==========
        session["current_step"] = 4
        session["status"] = "completed"
        session["step_status"] = "Processing complete!"
        session["completed_at"] = datetime.now().isoformat()

        # Update dashboard stats
        dashboard_stats["total_processed"] += len(selected_records)

        logger.info("="*80)
        logger.info(f"✅ PROCESSING COMPLETED SUCCESSFULLY")
        logger.info(f"📊 FINAL SUMMARY:")
        logger.info(f"   Total Patients: {len(selected_records)}")
        logger.info(f"   HL7 Messages Generated: {len(session['generated_messages'])}")
        if send_to_mirth:
            logger.info(f"   Mirth Successful: {session['mirth_successful']}")
            logger.info(f"   Mirth Failed: {session['mirth_failed']}")
        logger.info(f"   Upload ID: {upload_id}")
        logger.info(f"   Completed At: {session['completed_at']}")
        logger.info("="*80)

    except Exception as e:
        session["status"] = "error"
        session["error"] = str(e)
        session["step_status"] = f"Error: {str(e)}"
        logger.error("="*80)
        logger.error(f"❌ PROCESSING FAILED")
        logger.error(f"   Upload ID: {upload_id}")
        logger.error(f"   Error: {str(e)}")
        logger.error(f"   Exception Type: {type(e).__name__}")
        logger.error("="*80)

def add_zpi_segment_with_uuid(hl7_message: str, patient_uuid: str) -> str:
    """
    Add custom ZPI segment with patient UUID to HL7 message

    ZPI segment format:
    ZPI|<UUID>

    This is added after the PID segment
    """
    lines = hl7_message.split("\n")
    result_lines = []

    for line in lines:
        result_lines.append(line)
        # Add ZPI segment after PID segment
        if line.startswith("PID|"):
            zpi_segment = f"ZPI|{patient_uuid}"
            result_lines.append(zpi_segment)

    return "\n".join(result_lines)

async def process_csv_with_progress(
    upload_id: str,
    df: pd.DataFrame,
    trigger_event: str = "ADT-A01",
    send_to_mirth_flag: bool = False
):
    """
    Background async task that processes CSV through 6 steps with real-time updates

    Steps:
    1. File uploaded (already done)
    2. Parse CSV data
    3. Select patients (auto-select all)
    4. Generate HL7 messages
    5. Send to Mirth (if enabled)
    6. Complete
    """
    global client_wrapper, dashboard_stats

    session = upload_sessions[upload_id]

    try:
        # ========== STEP 1: File Uploaded ==========
        session["current_step"] = 1
        session["step_status"] = "File uploaded successfully"
        await asyncio.sleep(0.5)

        # ========== STEP 2: Parse CSV Data ==========
        session["current_step"] = 2
        session["step_status"] = "Parsing CSV data..."
        await asyncio.sleep(0.3)

        # Parse CSV using existing column mapping logic
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

        parsed_patients = []
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

            parsed_patients.append({
                "row_number": index + 2,
                "patient_id": patient_id,
                "first_name": first_name,
                "last_name": last_name,
                "patient_name": f"{first_name} {last_name}".strip(),
                "dob": dob_formatted,
                "gender": gender,
                "address": full_address,
                "selected": True
            })

        session["parsed_patients"] = parsed_patients
        session["total_patients"] = len(parsed_patients)
        session["step_status"] = f"Parsed {len(parsed_patients)} patients"
        await asyncio.sleep(0.5)

        # ========== STEP 3: Select Patients (Auto-select all) ==========
        session["current_step"] = 3
        session["step_status"] = f"Selected {len(parsed_patients)} patients"
        session["selected_patient_ids"] = [p["patient_id"] for p in parsed_patients]
        await asyncio.sleep(0.5)

        # ========== STEP 4: Generate HL7 Messages ==========
        session["current_step"] = 4
        session["generated_messages"] = []
        generated_count = 0

        for patient in parsed_patients:
            # Build command
            command = f"""
Trigger Event: {trigger_event}
Patient ID: {patient['patient_id']}
Patient Name: {patient['last_name']} {patient['first_name']}
Date of Birth: {patient['dob']}
Gender: {patient['gender']}
Address: {patient['address']}
Create an {trigger_event} message for patient {patient['first_name']} {patient['last_name']}, ID {patient['patient_id']}, DOB {patient['dob']}, Gender {patient['gender']}, Address: {patient['address']}
"""

            # Generate HL7 message
            try:
                hl7_message = generate_hl7_message(client_wrapper, command)
                validation = validate_required_fields_api(hl7_message)

                message_result = {
                    "row_number": patient["row_number"],
                    "patient_id": patient["patient_id"],
                    "patient_name": patient["patient_name"],
                    "hl7_message": hl7_message,
                    "validation": validation.model_dump(),
                    "status": "success" if validation.is_valid else "validation_failed"
                }

                session["generated_messages"].append(message_result)
                generated_count += 1
                session["step_status"] = f"Generated {generated_count}/{len(parsed_patients)} messages"

                # Update dashboard stats
                dashboard_stats["hl7_messages_generated"] += 1

                # Rate limiting: wait 1 second between messages to prevent overwhelming Mirth
                await asyncio.sleep(1.0)

            except Exception as e:
                error_result = {
                    "row_number": patient["row_number"],
                    "patient_id": patient["patient_id"],
                    "patient_name": patient["patient_name"],
                    "error": str(e),
                    "status": "error"
                }
                session["generated_messages"].append(error_result)
                generated_count += 1
                session["step_status"] = f"Generated {generated_count}/{len(parsed_patients)} messages (with errors)"

        # ========== STEP 5: Send to Mirth (if enabled) ==========
        if send_to_mirth_flag:
            session["current_step"] = 5
            session["step_status"] = "Sending to Mirth Connect..."
            session["mirth_successful"] = 0
            session["mirth_failed"] = 0
            sent_count = 0

            for message in session["generated_messages"]:
                if message.get("status") == "success":
                    try:
                        success, ack = send_to_mirth(message["hl7_message"])
                        message["mirth_sent"] = success
                        message["mirth_ack"] = ack

                        if success:
                            session["mirth_successful"] += 1
                            dashboard_stats["successful_sends"] += 1
                        else:
                            session["mirth_failed"] += 1
                            dashboard_stats["failed_sends"] += 1

                        sent_count += 1
                        session["step_status"] = f"Sent {sent_count}/{len(session['generated_messages'])} to Mirth"

                        # Small delay between Mirth sends
                        await asyncio.sleep(0.2)

                    except Exception as e:
                        message["mirth_sent"] = False
                        message["mirth_error"] = str(e)
                        session["mirth_failed"] += 1
                        dashboard_stats["failed_sends"] += 1
        else:
            session["current_step"] = 5
            session["step_status"] = "Skipped Mirth sending (disabled)"
            session["mirth_successful"] = 0
            session["mirth_failed"] = 0
            await asyncio.sleep(0.3)

        # ========== STEP 6: Complete ==========
        session["current_step"] = 6
        session["status"] = "completed"
        session["step_status"] = "Processing complete!"
        session["completed_at"] = datetime.now().isoformat()

        # Update dashboard stats
        dashboard_stats["total_processed"] += len(parsed_patients)

    except Exception as e:
        session["status"] = "error"
        session["error"] = str(e)
        session["step_status"] = f"Error: {str(e)}"

# ==================== SESSION CLEANUP SCHEDULER ====================
async def cleanup_expired_sessions():
    """
    Background task to clean up expired upload sessions

    Runs every 5 minutes and removes sessions older than 1 hour
    """
    while True:
        try:
            await asyncio.sleep(300)  # Run every 5 minutes

            now = datetime.now()
            expired_sessions = []

            for session_id, session_data in upload_sessions.items():
                # Check if session has expires_at field (new preview sessions)
                if isinstance(session_data, dict) and "expires_at" in session_data:
                    try:
                        expires_at = datetime.fromisoformat(session_data["expires_at"])
                        if now > expires_at:
                            expired_sessions.append(session_id)
                    except (ValueError, KeyError):
                        pass

            # Remove expired sessions
            for session_id in expired_sessions:
                del upload_sessions[session_id]
                print(f"🧹 Cleaned up expired session: {session_id}")

            if expired_sessions:
                print(f"✓ Removed {len(expired_sessions)} expired session(s)")

        except Exception as e:
            print(f"⚠ Error in session cleanup: {e}")

# ==================== API ENDPOINTS ====================

@app.on_event("startup")
async def startup_event():
    """Initialize client wrapper and start background tasks"""
    global client_wrapper
    client_wrapper = ClientWrapper()

    # Start session cleanup background task
    asyncio.create_task(cleanup_expired_sessions())

    print("\n" + "=" * 80)
    print("🚀 Smart HL7 Message Generator API Started")
    print("=" * 80)
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print(f"🔗 Mirth Connect: {MIRTH_HOST}:{MIRTH_PORT}")
    print(f"🤖 OpenAI Enabled: {client_wrapper.has_remote}")
    print(f"🧹 Session Cleanup: Running (every 5 minutes)")
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

# @app.post("/api/generate-hl7", response_model=HL7GenerationResponse, tags=["HL7 Generation"])
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

# ==================== NEW DASHBOARD & REAL-TIME UPLOAD ENDPOINTS ====================

@app.get("/api/dashboard/stats", tags=["Dashboard"])
async def get_dashboard_stats():
    """
    Get dashboard statistics for Figma UI

    **Returns:**
    - total_processed: Total patients processed
    - hl7_messages: Total HL7 messages generated
    - successful_sends: Successfully sent to Mirth
    - failed_sends: Failed to send to Mirth
    - success_rate: Success percentage
    """
    total = dashboard_stats["hl7_messages_generated"]
    success_rate = 0.0
    if total > 0:
        success_rate = (dashboard_stats["successful_sends"] / total) * 100

    return {
        "total_processed": dashboard_stats["total_processed"],
        "hl7_messages": dashboard_stats["hl7_messages_generated"],
        "successful_sends": dashboard_stats["successful_sends"],
        "failed_sends": dashboard_stats["failed_sends"],
        "success_rate": round(success_rate, 1)
    }

@app.get("/api/dashboard/system-status", tags=["Dashboard"])
async def get_system_status():
    """
    Get system status for dashboard indicators

    **Returns:**
    - openemr_connection: Status and last sync time
    - hl7_parser: Parser status (Running/Limited)
    - message_queue: Queue status and pending count
    """
    # Test Mirth connection
    mirth_status = "Offline"
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((MIRTH_HOST, MIRTH_PORT))
        sock.close()
        if result == 0:
            mirth_status = "Active"
    except Exception:
        mirth_status = "Offline"

    return {
        "openemr_connection": {
            "status": mirth_status,
            "last_sync": datetime.now().isoformat()
        },
        "hl7_parser": {
            "status": "Running" if client_wrapper and client_wrapper.has_remote else "Limited"
        },
        "message_queue": {
            "status": "Ready",
            "pending": 0
        }
    }

@app.post("/api/upload", response_model=UploadResponse, tags=["Upload & Processing"])
async def upload_csv_file(
    file: UploadFile = File(..., description="CSV or Excel file with patient data"),
    trigger_event: str = Form("ADT-A01", description="HL7 trigger event (default: ADT-A01)"),
    use_llm_mapping: bool = Form(True, description="Use LLM for intelligent column mapping (default: True)")
):
    """
    **Upload CSV/Excel File and Get Preview Data**

    Upload a CSV or Excel file containing patient data. The file will be parsed, validated,
    and all patient records will be returned for preview. No processing or Mirth transmission
    occurs at this stage.

    **Workflow:**
    1. Parse CSV/Excel file with flexible column mapping
    2. Generate unique UUID for each patient record
    3. Validate all required fields (MRN, First Name, Last Name, DOB, Gender)
    4. Store session data in memory (expires after 1 hour)
    5. Return all patient records with validation status

    **Returns:**
    - `session_id`: Use this to confirm and process selected patients
    - `patients`: Array of all parsed patient records with UUIDs
    - `validation_errors`: List of any validation errors found
    - `column_mapping`: Shows how CSV columns were mapped to fields

    **Next Step:**
    Call `POST /api/upload/confirm` with `session_id` and selected patient indices to process
    """
    try:
        # Read file
        contents = await file.read()

        if file.filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(contents))
            file_type = "csv"
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(BytesIO(contents))
            file_type = "excel"
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload CSV or Excel file.")

        # LOG: Show exact column names from uploaded file
        logger.info(f"📊 File Uploaded: {file.filename}")
        logger.info(f"📋 Column Names in File: {list(df.columns)}")
        logger.info(f"🔍 Total Rows: {len(df)}, Total Columns: {len(df.columns)}")

        # Parse CSV with preview (this generates UUIDs)
        parsed_records, validation_errors, column_mapping = parse_csv_with_preview(
            df=df,
            file_name=file.filename,
            trigger_event=trigger_event,
            use_llm_mapping=use_llm_mapping
        )

        # LOG: Show column mapping results
        logger.info(f"🗺️  Column Mapping Results:")
        if column_mapping:
            for excel_col, std_field in column_mapping.items():
                logger.info(f"   '{excel_col}' → '{std_field}'")
        else:
            logger.warning(f"⚠️  No columns were mapped!")

        # LOG: Show unmapped columns
        unmapped_cols = [col for col in df.columns if col not in column_mapping]
        if unmapped_cols:
            logger.warning(f"⚠️  Unmapped Columns: {unmapped_cols}")
            logger.warning(f"   These columns will be ignored during processing")

        # Generate session ID and upload ID
        session_id = str(uuid.uuid4())
        upload_id = str(uuid.uuid4())

        # Calculate expiration time (1 hour from now)
        uploaded_at = datetime.now()
        expires_at = uploaded_at + timedelta(hours=1)

        # Create upload session and store in memory
        session_data = UploadSession(
            session_id=session_id,
            upload_id=upload_id,
            file_name=file.filename,
            file_type=file_type,
            uploaded_at=uploaded_at.isoformat(),
            expires_at=expires_at.isoformat(),
            total_records=len(parsed_records),
            parsed_records=parsed_records,
            validation_errors=validation_errors,
            column_mapping=column_mapping,
            status="pending",
            trigger_event=trigger_event
        )

        # Store session in memory (convert Pydantic model to dict for storage)
        upload_sessions[session_id] = session_data.model_dump()

        # Count valid and invalid records
        valid_count = sum(1 for r in parsed_records if r.validation_status == "valid")
        invalid_count = len(parsed_records) - valid_count

        # Return response with ALL patient records
        return UploadResponse(
            session_id=session_id,
            file_name=file.filename,
            file_type=file_type,
            total_records=len(parsed_records),
            valid_records=valid_count,
            invalid_records=invalid_count,
            patients=parsed_records,  # Return all records, not just first 10
            validation_errors=validation_errors,
            column_mapping=column_mapping,
            expires_at=expires_at.isoformat(),
            timestamp=uploaded_at.isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/api/upload/confirm", response_model=ConfirmUploadResponse, tags=["Upload & Processing"])
async def confirm_and_process_upload(request: ConfirmUploadRequest):
    """
    **Confirm and Process Selected Patients**

    After reviewing the preview data from `/api/upload`, confirm which patients to process
    and send to Mirth Connect. This endpoint generates HL7 messages and transmits them.

    **Workflow:**
    1. Retrieve upload session using `session_id`
    2. Filter to selected patient indices (empty array = process all valid patients)
    3. Generate HL7 ADT messages for each selected patient
    4. Send messages to Mirth Connect via MLLP protocol
    5. Stream real-time progress via Server-Sent Events (SSE)

    **Request Body:**
    - `session_id`: Session ID from `/api/upload` response
    - `selected_indices`: Array of patient indices to process (empty = all valid patients)
    - `send_to_mirth`: Set to `true` to send to Mirth, `false` for dry-run

    **Returns:**
    - `upload_id`: Unique processing job ID
    - `status`: Always "processing" initially
    - `total_selected`: Number of patients being processed
    - `stream_url`: SSE endpoint URL for real-time progress updates

    **Next Step:**
    Connect to the `stream_url` using EventSource to monitor real-time processing progress
    """
    try:
        # Retrieve session from cache
        if request.session_id not in upload_sessions:
            raise HTTPException(status_code=404, detail="Session not found or expired. Please upload the file again.")

        session_data_dict = upload_sessions[request.session_id]

        # Convert dict back to UploadSession model
        session_data = UploadSession(**session_data_dict)

        # Check if session has expired
        expires_at = datetime.fromisoformat(session_data.expires_at)
        if datetime.now() > expires_at:
            del upload_sessions[request.session_id]
            raise HTTPException(status_code=410, detail="Session has expired. Please upload the file again.")

        # Get parsed records
        all_records = session_data.parsed_records

        # Filter to selected indices (empty array = all patients)
        if request.selected_indices:
            selected_records = [r for r in all_records if r.index in request.selected_indices]
        else:
            selected_records = all_records

        if not selected_records:
            raise HTTPException(status_code=400, detail="No patients selected for processing.")

        # Create new upload session for processing
        processing_upload_id = str(uuid.uuid4())

        upload_sessions[processing_upload_id] = {
            "id": processing_upload_id,
            "session_id": request.session_id,
            "filename": session_data.file_name,
            "status": "processing",
            "current_step": 0,
            "step_status": "Starting processing...",
            "total_patients": len(selected_records),
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
            "trigger_event": session_data.trigger_event,
            "send_to_mirth": request.send_to_mirth,
            "selected_records": [r.model_dump() for r in selected_records]  # Convert to dict
        }

        # Start background processing with selected records
        asyncio.create_task(process_confirmed_patients(
            upload_id=processing_upload_id,
            selected_records=selected_records,
            trigger_event=session_data.trigger_event,
            send_to_mirth=request.send_to_mirth
        ))

        return ConfirmUploadResponse(
            upload_id=processing_upload_id,
            status="processing",
            total_selected=len(selected_records),
            message=f"Processing {len(selected_records)} patient(s)",
            stream_url=f"/api/upload/{processing_upload_id}/stream"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error confirming upload: {str(e)}")

@app.post("/api/upload-legacy", tags=["Legacy Upload"])
async def upload_csv_with_realtime_progress(
    file: UploadFile = File(..., description="CSV or Excel file with patient data"),
    trigger_event: str = Form("ADT-A01", description="HL7 trigger event"),
    send_to_mirth: bool = Form(False, description="Send to Mirth after generation")
):
    """
    **Legacy Upload Mode - Direct Processing Without Preview**

    This endpoint uploads a file and immediately starts processing ALL patients without preview.
    Use this for automated workflows where preview/confirmation is not needed.

    **Recommended**: Use `POST /api/upload` + `POST /api/upload/confirm` workflow instead for better control.

    **Workflow:**
    1. Upload file and parse all patients
    2. Automatically process ALL valid patients
    3. Generate HL7 messages for each patient
    4. Send to Mirth Connect (if enabled)
    5. Stream real-time progress via SSE

    **Returns:**
    - `upload_id`: Use to connect to SSE stream
    - `status`: "processing"
    - `message`: Next steps

    **Next Step:**
    Connect to `/api/upload/{upload_id}/stream` for real-time progress
    """
    try:
        # Read file
        contents = await file.read()

        if file.filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(contents))
        else:
            df = pd.read_excel(BytesIO(contents))

        # Create upload session
        upload_id = str(uuid.uuid4())
        upload_sessions[upload_id] = {
            "id": upload_id,
            "filename": file.filename,
            "status": "processing",
            "current_step": 0,
            "step_status": "Initializing...",
            "total_patients": 0,
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
            "trigger_event": trigger_event,
            "send_to_mirth": send_to_mirth
        }

        # Start background processing
        asyncio.create_task(process_csv_with_progress(upload_id, df, trigger_event, send_to_mirth))

        return {
            "upload_id": upload_id,
            "filename": file.filename,
            "status": "processing",
            "message": f"Upload started. Connect to /api/upload/{upload_id}/stream for real-time updates"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/api/upload/{upload_id}/stream", tags=["Real-Time Upload"])
async def stream_upload_progress(upload_id: str):
    """
    Stream real-time progress updates using Server-Sent Events (SSE)

    **Frontend Usage (JavaScript):**
    ```javascript
    const eventSource = new EventSource('/api/upload/{upload_id}/stream');

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Step:', data.current_step);  // 1-6
      console.log('Status:', data.step_status);  // "Generated 5/10 messages"

      if (data.status === 'completed' || data.status === 'error') {
        eventSource.close();
      }
    };
    ```

    **Event Data:**
    - current_step: 1-6 (current wizard step)
    - step_status: Human-readable status message
    - total_patients: Total patient count
    - generated_count: Messages generated so far (step 4)
    - mirth_successful/mirth_failed: Mirth sending counts (step 5)
    - status: "processing", "completed", or "error"
    """
    if upload_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="Upload session not found")

    async def event_generator():
        """Generate SSE events"""
        session = upload_sessions[upload_id]

        # Send events until processing is complete
        while session["status"] == "processing":
            # Build event data
            event_data = {
                "current_step": session.get("current_step", 0),
                "step_status": session.get("step_status", "Processing..."),
                "total_patients": session.get("total_patients", 0),
                "status": session["status"]
            }

            # Add generated count if in step 4
            if session.get("current_step") == 4 and "generated_messages" in session:
                event_data["generated_count"] = len(session["generated_messages"])

            # Add mirth counts if in step 5
            if session.get("current_step") == 5:
                event_data["mirth_successful"] = session.get("mirth_successful", 0)
                event_data["mirth_failed"] = session.get("mirth_failed", 0)

            # Send SSE event
            yield f"data: {json.dumps(event_data)}\n\n"

            # Wait before next update
            await asyncio.sleep(0.5)

        # Send final completion event
        final_data = {
            "current_step": session.get("current_step", 6),
            "step_status": session.get("step_status", "Complete"),
            "total_patients": session.get("total_patients", 0),
            "status": session["status"],
            "upload_id": upload_id
        }

        if session["status"] == "completed":
            final_data["successful"] = sum(1 for m in session.get("generated_messages", []) if m.get("status") == "success")
            final_data["failed"] = session.get("total_patients", 0) - final_data["successful"]

        if session["status"] == "error":
            final_data["error"] = session.get("error", "Unknown error")

        yield f"data: {json.dumps(final_data)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/upload/{upload_id}/status", tags=["Real-Time Upload"])
async def get_upload_status(upload_id: str):
    """
    Get current upload status (polling alternative to SSE)

    **Use this if SSE is not supported in your environment**

    **Returns:**
    - upload_id: Session ID
    - filename: Original filename
    - status: "processing", "completed", "error"
    - current_step: 1-6
    - step_status: Current status message
    - total_patients: Total patient count
    - created_at: Upload timestamp
    """
    if upload_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="Upload session not found")

    session = upload_sessions[upload_id]

    return {
        "upload_id": session["id"],
        "filename": session["filename"],
        "status": session["status"],
        "current_step": session.get("current_step", 0),
        "step_status": session.get("step_status", ""),
        "total_patients": session.get("total_patients", 0),
        "created_at": session["created_at"],
        "completed_at": session.get("completed_at")
    }

@app.get("/api/upload/{upload_id}/results", tags=["Real-Time Upload"])
async def get_upload_results(upload_id: str):
    """
    Get complete results after processing is finished

    **Returns:**
    - Complete upload session data
    - All generated HL7 messages
    - Validation results for each message
    - Mirth sending results (if enabled)

    **Use this to display final results in Step 6 (Complete screen)**
    """
    if upload_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="Upload session not found")

    session = upload_sessions[upload_id]

    # Calculate summary statistics
    messages = session.get("generated_messages", [])
    successful = sum(1 for m in messages if m.get("status") == "success")
    failed = len(messages) - successful

    return {
        "upload_id": session["id"],
        "filename": session["filename"],
        "status": session["status"],
        "current_step": session.get("current_step", 0),
        "total_patients": session.get("total_patients", 0),
        "successful": successful,
        "failed": failed,
        "mirth_successful": session.get("mirth_successful", 0),
        "mirth_failed": session.get("mirth_failed", 0),
        "created_at": session["created_at"],
        "completed_at": session.get("completed_at"),
        "messages": messages,
        "error": session.get("error")
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
