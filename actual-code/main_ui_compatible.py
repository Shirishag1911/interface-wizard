#!/usr/bin/env python3
"""
Interface Wizard - UI-Compatible Backend API
Version: 4.0 (UI Integration)
Created: December 30, 2025

This backend provides all endpoints expected by the React UI frontend while
maintaining compatibility with the existing CSV/Excel upload functionality.

Architecture:
- Wraps existing upload functionality in UI-expected endpoint formats
- Adds session management for chat-like interface
- Includes authentication system
- Provides command processing endpoint
- Maintains backward compatibility with v3.0 endpoints

Key Differences from v3.0:
1. Uses /api/v1 prefix instead of /api
2. Adds authentication endpoints
3. Adds session/message management
4. Transforms responses to match UI expectations
5. Adds command processing for natural language inputs
"""

import sys
import os
import logging
import asyncio
import uuid
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
from pathlib import Path

# FastAPI imports
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, validator

# Data processing imports
import pandas as pd
from io import BytesIO

# HL7 and existing imports
import hl7

# Import existing backend functionality
# We'll reuse the core logic from main_with_fastapi.py
from main_with_fastapi import (
    parse_csv_file,
    parse_excel_file,
    build_hl7_message_programmatically,
    send_to_mirth as send_to_mirth_original,
    map_columns_with_llm,
    normalize_column_name,
    PatientRecord,
    MIRTH_HOST,
    MIRTH_PORT,
)

# ==================== LOGGING CONFIGURATION ====================
# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('interface_wizard_ui.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================
SECRET_KEY = "your-secret-key-change-in-production"  # TODO: Use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ==================== FASTAPI APP INITIALIZATION ====================
app = FastAPI(
    title="Interface Wizard UI-Compatible API",
    description="Backend API matching React UI expectations",
    version="4.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ==================== CORS MIDDLEWARE ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== DATA MODELS (UI-EXPECTED FORMATS) ====================

# Authentication Models
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

# Command Processing Models
class CommandRequest(BaseModel):
    command: str
    session_id: Optional[str] = None

class OperationResponse(BaseModel):
    operation_id: str
    status: str  # 'pending' | 'processing' | 'success' | 'failed' | 'partial_success'
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    protocol_used: Optional[str] = "hl7v2"
    records_affected: int = 0
    records_succeeded: int = 0
    records_failed: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

# Preview/Confirm Models
class PatientPreview(BaseModel):
    name: str
    mrn: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class PreviewResponse(BaseModel):
    preview_id: str
    operation_type: str
    total_records: int
    preview_records: List[PatientPreview]
    validation_warnings: List[str] = []
    estimated_time_seconds: Optional[int] = None
    message: str

class ConfirmRequest(BaseModel):
    preview_id: str
    confirmed: bool

# Session Models
class Message(BaseModel):
    id: str
    role: str  # 'user' | 'assistant'
    content: str
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class Session(BaseModel):
    id: str
    title: Optional[str] = None
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    messages: Optional[List[Message]] = []

class SessionInfo(BaseModel):
    session_id: str
    created_at: str
    last_activity: str
    command_count: int = 0
    operation_count: int = 0

# Health Models
class HealthStatus(BaseModel):
    status: str
    version: str = "4.0"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# ==================== IN-MEMORY STORAGE ====================
# In production, use Redis or database
sessions_db: Dict[str, Session] = {}
messages_db: Dict[str, List[Message]] = {}
operations_db: Dict[str, OperationResponse] = {}
preview_cache: Dict[str, Dict[str, Any]] = {}  # Stores preview data
users_db: Dict[str, Dict[str, Any]] = {
    "admin": {
        "id": "user_1",
        "username": "admin",
        "email": "admin@example.com",
        "password": "admin123"  # In production, hash passwords!
    }
}

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

# ==================== AUTHENTICATION HELPERS ====================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password (simplified - use bcrypt in production)"""
    return plain_password == hashed_password

def get_user(username: str) -> Optional[Dict[str, Any]]:
    """Get user from database"""
    return users_db.get(username)

def create_access_token(data: dict) -> str:
    """Create JWT access token (simplified - use proper JWT in production)"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # In production, use: jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return f"token_{data['sub']}_{int(time.time())}"

async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[Dict[str, Any]]:
    """Get current user from token (optional authentication)"""
    if not token:
        return None
    # In production, decode JWT and validate
    username = token.split("_")[1] if "_" in token else None
    if username:
        return get_user(username)
    return None

# ==================== TRANSFORMATION HELPERS ====================

def transform_patient_to_preview(patient: PatientRecord) -> PatientPreview:
    """Transform PatientRecord to PatientPreview (UI format)"""
    name = f"{patient.firstName} {patient.lastName}".strip()
    return PatientPreview(
        name=name if name else "Unknown",
        mrn=patient.mrn,
        date_of_birth=patient.dateOfBirth,
        gender=patient.gender,
        phone=patient.phone,
        email=patient.email,
        address=patient.address
    )

def transform_upload_to_preview(upload_data: Dict[str, Any]) -> PreviewResponse:
    """Transform /api/upload response to /api/v1/preview format"""
    preview_id = str(uuid.uuid4())

    # Store original data for later confirmation
    preview_cache[preview_id] = {
        "session_id": upload_data.get("session_id"),
        "patients": upload_data.get("patients", []),
        "file_name": upload_data.get("file_name"),
        "trigger_event": "ADT-A04",
        "timestamp": datetime.now().isoformat()
    }

    # Transform patients to preview format
    preview_records = [
        transform_patient_to_preview(PatientRecord(**p))
        for p in upload_data.get("patients", [])
        if p.get("validation_status") == "valid"
    ]

    # Collect validation warnings
    warnings = []
    for error in upload_data.get("validation_errors", []):
        warnings.append(f"Row {error['row']}: {error['error']} in field '{error['field']}'")

    # Add mapping warnings if any
    if upload_data.get("mapping_warnings"):
        warnings.extend(upload_data["mapping_warnings"])

    total_records = upload_data.get("total_records", 0)
    estimated_time = max(1, int(total_records * 0.1))  # ~0.1 seconds per record

    return PreviewResponse(
        preview_id=preview_id,
        operation_type="bulk_patient_registration",
        total_records=total_records,
        preview_records=preview_records[:10],  # Show first 10 in preview
        validation_warnings=warnings,
        estimated_time_seconds=estimated_time,
        message=f"Found {upload_data.get('valid_records', 0)} valid patients out of {total_records} total records"
    )

def transform_confirm_to_operation(confirm_result: Dict[str, Any], preview_data: Dict[str, Any]) -> OperationResponse:
    """Transform confirm result to OperationResponse format"""
    operation_id = confirm_result.get("upload_id", str(uuid.uuid4()))

    # Store operation
    operation = OperationResponse(
        operation_id=operation_id,
        status="processing",
        message=confirm_result.get("message", "Processing patients"),
        records_affected=confirm_result.get("total_selected", 0),
        records_succeeded=0,  # Will be updated
        records_failed=0,
        created_at=datetime.now().isoformat()
    )

    operations_db[operation_id] = operation

    return operation

# ==================== API ENDPOINTS ====================

# ========== AUTHENTICATION ENDPOINTS ==========

@app.post("/auth/login", response_model=AuthResponse, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    User login endpoint

    Accepts form data with username and password.
    Returns JWT access token and user information.
    """
    logger.info(f"Login attempt for user: {form_data.username}")

    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user["username"]})

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user["id"],
            "username": user["username"],
            "email": user["email"]
        }
    )

@app.post("/auth/register", response_model=AuthResponse, tags=["Authentication"])
async def register(user_data: UserRegister):
    """
    User registration endpoint

    Creates new user account and returns access token.
    """
    logger.info(f"Registration attempt for user: {user_data.username}")

    # Check if user already exists
    if user_data.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Create new user (in production, hash password!)
    user_id = f"user_{len(users_db) + 1}"
    users_db[user_data.username] = {
        "id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "password": user_data.password  # HASH THIS IN PRODUCTION!
    }

    access_token = create_access_token(data={"sub": user_data.username})

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user_id,
            "username": user_data.username,
            "email": user_data.email
        }
    )

# ========== COMMAND PROCESSING ENDPOINT ==========

@app.post("/api/v1/command", response_model=OperationResponse, tags=["Commands"])
async def process_command(
    command: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: Optional[Dict] = Depends(get_current_user)
):
    """
    Process natural language commands or file uploads

    This endpoint handles both:
    1. Text commands (e.g., "Create patient John Doe")
    2. File uploads (CSV, Excel, PDF)

    For files, it automatically calls the preview workflow.
    For text commands, it processes them directly.
    """
    logger.info(f"Command received: {command}, File: {file.filename if file else None}")

    # Handle file upload
    if file:
        # Redirect to preview endpoint
        try:
            # Read file content
            content = await file.read()
            await file.seek(0)

            # Determine file type
            file_ext = Path(file.filename).suffix.lower()

            if file_ext in ['.csv', '.xlsx', '.xls']:
                # Parse file
                if file_ext == '.csv':
                    df = pd.read_csv(BytesIO(content))
                else:
                    df = pd.read_excel(BytesIO(content))

                # Use existing parsing logic
                from main_with_fastapi import parse_csv_data, map_columns_with_llm

                # Get column names
                column_names = df.columns.tolist()

                # Map columns with LLM
                mapping_result = map_columns_with_llm(column_names, use_llm=True)

                # Parse patient records
                patients = []
                for idx, row in df.iterrows():
                    patient_data = {}
                    for csv_col, std_field in mapping_result["mapping"].items():
                        if csv_col in row:
                            patient_data[std_field] = str(row[csv_col]) if pd.notna(row[csv_col]) else None

                    # Add UUID
                    patient_data["uuid"] = str(uuid.uuid4())
                    patient_data["index"] = idx

                    # Basic validation
                    if patient_data.get("firstName") and patient_data.get("lastName"):
                        patient_data["validation_status"] = "valid"
                        patient_data["validation_messages"] = []
                    else:
                        patient_data["validation_status"] = "invalid"
                        patient_data["validation_messages"] = ["Missing required fields"]

                    patients.append(patient_data)

                # Create preview response
                preview_id = str(uuid.uuid4())
                preview_cache[preview_id] = {
                    "patients": patients,
                    "file_name": file.filename,
                    "trigger_event": "ADT-A04"
                }

                valid_count = sum(1 for p in patients if p.get("validation_status") == "valid")

                return OperationResponse(
                    operation_id=preview_id,
                    status="success",
                    message=f"File uploaded successfully. Found {valid_count} valid patients. Use /api/v1/confirm to process.",
                    records_affected=len(patients),
                    records_succeeded=valid_count,
                    records_failed=len(patients) - valid_count,
                    data={
                        "preview_id": preview_id,
                        "requires_confirmation": True
                    }
                )

            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file_ext}"
                )

        except Exception as e:
            logger.error(f"File processing error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # Handle text command
    elif command:
        operation_id = str(uuid.uuid4())

        # Simple command parsing (in production, use NLP/LLM)
        command_lower = command.lower()

        if "create patient" in command_lower or "add patient" in command_lower:
            # Extract patient info from command
            # This is a simplified example
            return OperationResponse(
                operation_id=operation_id,
                status="success",
                message=f"Command processed: {command}",
                records_affected=1,
                records_succeeded=1,
                records_failed=0,
                data={"command": command, "note": "Natural language processing not fully implemented"}
            )
        else:
            return OperationResponse(
                operation_id=operation_id,
                status="failed",
                message="Command not recognized",
                errors=["Unable to parse command. Try uploading a CSV/Excel file instead."]
            )

    else:
        raise HTTPException(status_code=400, detail="No command or file provided")

# ========== PREVIEW/CONFIRM ENDPOINTS ==========

@app.post("/api/v1/preview", response_model=PreviewResponse, tags=["Preview & Confirm"])
async def preview_operation(
    file: UploadFile = File(...),
    command: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None)
):
    """
    Preview bulk operation before execution

    Uploads file, validates data, and returns preview of records.
    User must confirm via /api/v1/confirm to actually process.
    """
    logger.info(f"Preview request for file: {file.filename}")

    try:
        # Read file
        content = await file.read()

        # Use existing upload logic from main_with_fastapi
        # This will parse, validate, and map columns
        file_ext = Path(file.filename).suffix.lower()

        if file_ext == '.csv':
            df = pd.read_csv(BytesIO(content))
        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")

        # Get column names
        column_names = df.columns.tolist()

        # Map columns with LLM
        mapping_result = map_columns_with_llm(column_names, use_llm=True)

        # Parse all patient records
        patients = []
        validation_errors = []

        for idx, row in df.iterrows():
            patient_data = {
                "index": idx,
                "uuid": str(uuid.uuid4())
            }

            # Map columns
            for csv_col, std_field in mapping_result["mapping"].items():
                if csv_col in row:
                    value = row[csv_col]
                    patient_data[std_field] = str(value) if pd.notna(value) else None

            # Basic validation (simplified)
            validation_messages = []
            if not patient_data.get("firstName"):
                validation_messages.append("Missing first name")
                validation_errors.append({"row": idx, "field": "firstName", "error": "Missing required field", "value": None, "severity": "error"})

            if not patient_data.get("lastName"):
                validation_messages.append("Missing last name")
                validation_errors.append({"row": idx, "field": "lastName", "error": "Missing required field", "value": None, "severity": "error"})

            patient_data["validation_status"] = "valid" if not validation_messages else "invalid"
            patient_data["validation_messages"] = validation_messages

            patients.append(patient_data)

        # Create response in original format
        upload_data = {
            "session_id": str(uuid.uuid4()),
            "file_name": file.filename,
            "file_type": "csv" if file_ext == ".csv" else "excel",
            "total_records": len(patients),
            "valid_records": sum(1 for p in patients if p["validation_status"] == "valid"),
            "invalid_records": sum(1 for p in patients if p["validation_status"] == "invalid"),
            "patients": patients,
            "validation_errors": validation_errors,
            "column_mapping": mapping_result["mapping"],
            "mapping_warnings": mapping_result.get("warnings", [])
        }

        # Transform to UI format
        preview_response = transform_upload_to_preview(upload_data)

        logger.info(f"Preview created: {preview_response.preview_id}")
        return preview_response

    except Exception as e:
        logger.error(f"Preview error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/confirm", response_model=OperationResponse, tags=["Preview & Confirm"])
async def confirm_operation(request: ConfirmRequest):
    """
    Confirm and execute a previewed operation

    Takes preview_id from /api/v1/preview and processes all valid patients.
    Generates HL7 messages and sends to Mirth Connect.
    """
    logger.info(f"Confirm request for preview: {request.preview_id}")

    # Get cached preview data
    preview_data = preview_cache.get(request.preview_id)

    if not preview_data:
        raise HTTPException(status_code=404, detail="Preview not found or expired")

    if not request.confirmed:
        return OperationResponse(
            operation_id=request.preview_id,
            status="failed",
            message="Operation cancelled by user"
        )

    try:
        # Process patients
        patients = preview_data["patients"]
        valid_patients = [p for p in patients if p.get("validation_status") == "valid"]

        operation_id = f"operation_{int(time.time())}_{str(uuid.uuid4())[:8]}"

        # Process in background
        results = await process_patients_async(valid_patients, operation_id)

        return results

    except Exception as e:
        logger.error(f"Confirm error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_patients_async(patients: List[Dict], operation_id: str) -> OperationResponse:
    """Process patients asynchronously and generate HL7 messages"""

    successful = 0
    failed = 0
    errors = []

    for patient_data in patients:
        try:
            # Create PatientRecord object
            patient = PatientRecord(**patient_data)

            # Generate HL7 message
            hl7_message = build_hl7_message_programmatically(patient, "ADT-A04")

            # Send to Mirth
            success, ack = send_to_mirth_original(hl7_message)

            if success:
                successful += 1
            else:
                failed += 1
                errors.append(f"Failed to send {patient.firstName} {patient.lastName}")

        except Exception as e:
            failed += 1
            errors.append(f"Error processing patient: {str(e)}")

    # Create operation response
    operation = OperationResponse(
        operation_id=operation_id,
        status="success" if failed == 0 else "partial_success" if successful > 0 else "failed",
        message=f"Processed {successful + failed} patients: {successful} succeeded, {failed} failed",
        records_affected=len(patients),
        records_succeeded=successful,
        records_failed=failed,
        errors=errors if errors else None,
        completed_at=datetime.now().isoformat()
    )

    # Store operation
    operations_db[operation_id] = operation

    return operation

# ========== SESSION MANAGEMENT ENDPOINTS ==========

@app.get("/api/v1/sessions", response_model=List[Session], tags=["Sessions"])
async def get_sessions(current_user: Optional[Dict] = Depends(get_current_user)):
    """
    Get all chat sessions

    Returns list of all sessions with their messages.
    """
    return list(sessions_db.values())

@app.post("/api/v1/sessions", response_model=Session, tags=["Sessions"])
async def create_session(current_user: Optional[Dict] = Depends(get_current_user)):
    """
    Create new chat session

    Initializes a new session for message tracking.
    """
    session_id = str(uuid.uuid4())
    session = Session(
        id=session_id,
        title=f"Session {len(sessions_db) + 1}",
        updated_at=datetime.now().isoformat(),
        messages=[]
    )
    sessions_db[session_id] = session
    messages_db[session_id] = []

    logger.info(f"Created session: {session_id}")
    return session

@app.get("/api/v1/sessions/{session_id}/messages", response_model=List[Message], tags=["Sessions"])
async def get_session_messages(session_id: str):
    """
    Get all messages in a session

    Returns message history for the specified session.
    """
    if session_id not in messages_db:
        raise HTTPException(status_code=404, detail="Session not found")

    return messages_db[session_id]

@app.delete("/api/v1/sessions/{session_id}", tags=["Sessions"])
async def delete_session(session_id: str):
    """
    Delete a session

    Removes session and all its messages.
    """
    if session_id in sessions_db:
        del sessions_db[session_id]
    if session_id in messages_db:
        del messages_db[session_id]

    logger.info(f"Deleted session: {session_id}")
    return {"message": "Session deleted"}

# ========== MESSAGE ENDPOINT ==========

@app.post("/api/v1/messages", tags=["Messages"])
async def send_message(
    content: str = Form(...),
    session_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Send a message with optional file attachment

    Adds message to session and processes any attached files.
    """
    # Create session if not provided
    if not session_id or session_id not in sessions_db:
        session = await create_session()
        session_id = session.id

    # Create user message
    user_message = Message(
        id=str(uuid.uuid4()),
        role="user",
        content=content
    )

    messages_db[session_id].append(user_message)

    # Process file if provided
    if file:
        # Redirect to command endpoint
        response = await process_command(command=content, session_id=session_id, file=file)

        # Create assistant response
        assistant_message = Message(
            id=str(uuid.uuid4()),
            role="assistant",
            content=response.message
        )
        messages_db[session_id].append(assistant_message)

        return {"message": "Message sent", "response": response}

    else:
        # Simple text response
        assistant_message = Message(
            id=str(uuid.uuid4()),
            role="assistant",
            content=f"Received: {content}"
        )
        messages_db[session_id].append(assistant_message)

        return {"message": "Message sent"}

# ========== SESSION INFO ENDPOINT ==========

@app.get("/api/v1/session/{session_id}", response_model=SessionInfo, tags=["Sessions"])
async def get_session_info(session_id: str):
    """
    Get session information

    Returns metadata about the session.
    """
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions_db[session_id]

    return SessionInfo(
        session_id=session_id,
        created_at=session.updated_at,
        last_activity=session.updated_at,
        command_count=len(messages_db.get(session_id, [])),
        operation_count=0
    )

# ========== OPERATION DETAILS ENDPOINT ==========

@app.get("/api/v1/operation/{operation_id}", response_model=OperationResponse, tags=["Operations"])
async def get_operation(operation_id: str):
    """
    Get operation details

    Returns current status and results of an operation.
    """
    if operation_id not in operations_db:
        raise HTTPException(status_code=404, detail="Operation not found")

    return operations_db[operation_id]

# ========== HEALTH CHECK ENDPOINTS ==========

@app.get("/api/v1/health", response_model=HealthStatus, tags=["Health"])
async def health_check():
    """
    Basic health check

    Returns API status and version.
    """
    return HealthStatus(status="healthy")

@app.get("/api/v1/health/detailed", tags=["Health"])
async def detailed_health_check():
    """
    Detailed health check

    Returns detailed status including service connectivity.
    """
    import socket

    # Check Mirth connectivity
    mirth_status = "disconnected"
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((MIRTH_HOST, MIRTH_PORT))
        sock.close()
        mirth_status = "connected" if result == 0 else "disconnected"
    except Exception as e:
        logger.error(f"Mirth health check error: {e}")

    return {
        "status": "healthy",
        "version": "4.0",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "mirth_connect": {
                "status": mirth_status,
                "host": MIRTH_HOST,
                "port": MIRTH_PORT
            },
            "sessions": {
                "active_count": len(sessions_db)
            },
            "operations": {
                "total_count": len(operations_db)
            }
        }
    }

# ========== ROOT ENDPOINT ==========

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint

    Returns API information and available endpoints.
    """
    return {
        "name": "Interface Wizard UI-Compatible API",
        "version": "4.0",
        "description": "Backend API matching React UI expectations",
        "docs_url": "/docs",
        "endpoints": {
            "authentication": ["/auth/login", "/auth/register"],
            "commands": ["/api/v1/command"],
            "preview_confirm": ["/api/v1/preview", "/api/v1/confirm"],
            "sessions": ["/api/v1/sessions"],
            "messages": ["/api/v1/messages"],
            "health": ["/api/v1/health", "/api/v1/health/detailed"]
        }
    }

# ==================== MAIN ENTRY POINT ====================

if __name__ == "__main__":
    import uvicorn

    logger.info("="*80)
    logger.info("Starting Interface Wizard UI-Compatible API v4.0")
    logger.info("="*80)
    logger.info("API Documentation: http://localhost:8000/docs")
    logger.info("Base URL: http://localhost:8000")
    logger.info("Mirth Connect: {}:{}".format(MIRTH_HOST, MIRTH_PORT))
    logger.info("="*80)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
