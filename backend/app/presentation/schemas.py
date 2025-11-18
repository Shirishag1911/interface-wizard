"""Pydantic schemas for API request/response validation."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class CommandRequest(BaseModel):
    """Request model for processing a command."""
    command: str = Field(..., description="Natural language command", min_length=1)
    session_id: Optional[str] = Field(None, description="Session ID for context")


class OperationResponse(BaseModel):
    """Response model for operation results."""
    operation_id: str
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: List[str] = []
    warnings: List[str] = []
    protocol_used: Optional[str] = None
    records_affected: int = 0
    records_succeeded: int = 0
    records_failed: int = 0
    created_at: datetime
    completed_at: Optional[datetime] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime


class SessionResponse(BaseModel):
    """Session information response."""
    session_id: str
    created_at: datetime
    last_activity: datetime
    command_count: int
    operation_count: int


class PatientResponse(BaseModel):
    """Patient information response."""
    patient_id: Optional[str] = None
    mrn: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime


class CSVUploadResponse(BaseModel):
    """CSV upload validation response."""
    valid: bool
    message: str
    headers: Optional[List[str]] = None
    row_count: Optional[int] = None
    mapped_fields: Optional[List[str]] = None
    unmapped_headers: Optional[List[str]] = None
    has_required_fields: Optional[bool] = None
    warnings: List[str] = []
    error: Optional[str] = None
