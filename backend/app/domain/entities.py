"""Domain entities representing core business objects."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from dataclasses import dataclass, field
from uuid import uuid4


class CommandType(str, Enum):
    """Types of commands the system can process."""
    CREATE_PATIENT = "create_patient"
    UPDATE_PATIENT = "update_patient"
    RETRIEVE_PATIENT = "retrieve_patient"
    CREATE_LAB_RESULT = "create_lab_result"
    RETRIEVE_LAB_RESULT = "retrieve_lab_result"
    ADMIT_PATIENT = "admit_patient"
    DISCHARGE_PATIENT = "discharge_patient"
    TRANSFER_PATIENT = "transfer_patient"
    CREATE_BULK = "create_bulk"
    QUERY = "query"
    UNKNOWN = "unknown"


class MessageType(str, Enum):
    """HL7 message types."""
    ADT_A01 = "ADT^A01"  # Admit patient
    ADT_A03 = "ADT^A03"  # Discharge patient
    ADT_A02 = "ADT^A02"  # Transfer patient
    ADT_A04 = "ADT^A04"  # Register patient
    ADT_A08 = "ADT^A08"  # Update patient
    ADT_A28 = "ADT^A28"  # Add person information
    ORU_R01 = "ORU^R01"  # Observation result
    ORM_O01 = "ORM^O01"  # Order message
    QRY_A19 = "QRY^A19"  # Patient query
    QBP_Q21 = "QBP^Q21"  # Get person demographics


class OperationStatus(str, Enum):
    """Status of an operation."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL_SUCCESS = "partial_success"


class Protocol(str, Enum):
    """Communication protocols."""
    HL7V2 = "hl7v2"
    FHIR = "fhir"


@dataclass
class Patient:
    """Patient entity."""
    patient_id: Optional[str] = None
    mrn: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    ssn: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "patient_id": self.patient_id,
            "mrn": self.mrn,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "middle_name": self.middle_name,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "gender": self.gender,
            "ssn": self.ssn,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "phone": self.phone,
            "email": self.email,
            "blood_type": self.blood_type,
            "allergies": self.allergies,
            "metadata": self.metadata,
        }


@dataclass
class LabResult:
    """Lab result entity."""
    observation_id: Optional[str] = None
    patient_id: Optional[str] = None
    test_name: Optional[str] = None
    test_code: Optional[str] = None
    result_value: Optional[str] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    status: Optional[str] = None
    observed_datetime: Optional[datetime] = None
    reported_datetime: Optional[datetime] = None
    performing_organization: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserCommand:
    """Represents a user's natural language command."""
    command_id: str = field(default_factory=lambda: str(uuid4()))
    raw_text: str = ""
    command_type: CommandType = CommandType.UNKNOWN
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class HL7Message:
    """Represents an HL7 v2 message."""
    message_type: MessageType
    message_content: str
    message_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    ack_received_at: Optional[datetime] = None
    ack_status: Optional[str] = None
    ack_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OperationResult:
    """Result of an operation."""
    command_id: str
    status: OperationStatus
    message: str
    operation_id: str = field(default_factory=lambda: str(uuid4()))
    data: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    protocol_used: Optional[Protocol] = None
    records_affected: int = 0
    records_succeeded: int = 0
    records_failed: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "operation_id": self.operation_id,
            "command_id": self.command_id,
            "status": self.status.value,
            "message": self.message,
            "data": self.data,
            "errors": self.errors,
            "warnings": self.warnings,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "protocol_used": self.protocol_used.value if self.protocol_used else None,
            "records_affected": self.records_affected,
            "records_succeeded": self.records_succeeded,
            "records_failed": self.records_failed,
        }


@dataclass
class ConversationContext:
    """Maintains conversation context for better NLP understanding."""
    session_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: Optional[str] = None
    command_history: List[UserCommand] = field(default_factory=list)
    operation_history: List[OperationResult] = field(default_factory=list)
    context_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)

    def add_command(self, command: UserCommand) -> None:
        """Add a command to history."""
        self.command_history.append(command)
        self.last_activity = datetime.utcnow()

    def add_operation_result(self, result: OperationResult) -> None:
        """Add an operation result to history."""
        self.operation_history.append(result)
        self.last_activity = datetime.utcnow()
