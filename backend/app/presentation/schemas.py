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


class PatientPreview(BaseModel):
    """Preview of a patient record for confirmation dialog (URS FR-3)."""
    name: str
    mrn: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


class ConfirmationPreviewResponse(BaseModel):
    """Response with preview data for user confirmation (URS FR-3)."""
    preview_id: str = Field(..., description="Unique ID for this preview session")
    operation_type: str = Field(..., description="Type of operation (e.g., 'create_patients')")
    total_records: int = Field(..., description="Total number of records to process")
    preview_records: List[PatientPreview] = Field(..., description="Sample of records (first 5)")
    validation_warnings: List[str] = Field(default=[], description="Validation warnings")
    estimated_time_seconds: Optional[int] = Field(None, description="Estimated processing time")
    message: str = Field(..., description="Human-readable description")


class ConfirmationRequest(BaseModel):
    """Request to confirm and execute operation (URS FR-3)."""
    preview_id: str = Field(..., description="Preview ID from preview response")
    confirmed: bool = Field(..., description="Whether user confirmed the operation")


class HealthCheckDetailResponse(BaseModel):
    """Detailed health check response for a service (URS IR-1)."""
    service: str
    status: str
    message: str
    response_time_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime


class SystemHealthResponse(BaseModel):
    """Overall system health response (URS IR-1)."""
    overall_status: str = Field(..., description="Overall system status: healthy, degraded, unhealthy")
    services: Dict[str, HealthCheckDetailResponse]
    timestamp: datetime
