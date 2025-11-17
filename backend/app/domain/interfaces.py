"""Domain interfaces (ports) for dependency inversion."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.domain.entities import (
    UserCommand,
    OperationResult,
    Patient,
    LabResult,
    HL7Message,
    ConversationContext,
)


class INLPService(ABC):
    """Interface for Natural Language Processing service."""

    @abstractmethod
    async def interpret_command(
        self, raw_text: str, context: Optional[ConversationContext] = None
    ) -> UserCommand:
        """
        Interpret natural language command and extract intent and parameters.

        Args:
            raw_text: The raw user input
            context: Optional conversation context

        Returns:
            UserCommand with interpreted type and parameters
        """
        pass

    @abstractmethod
    async def generate_response(
        self, operation_result: OperationResult, context: Optional[ConversationContext] = None
    ) -> str:
        """
        Generate a human-friendly response based on operation result.

        Args:
            operation_result: The result of the operation
            context: Optional conversation context

        Returns:
            Human-friendly response text
        """
        pass


class IHL7Service(ABC):
    """Interface for HL7 v2 messaging service."""

    @abstractmethod
    async def create_patient_message(self, patient: Patient) -> HL7Message:
        """Create an HL7 ADT message for patient creation."""
        pass

    @abstractmethod
    async def create_lab_result_message(self, lab_result: LabResult) -> HL7Message:
        """Create an HL7 ORU message for lab results."""
        pass

    @abstractmethod
    async def create_admit_message(self, patient: Patient, admission_data: Dict[str, Any]) -> HL7Message:
        """Create an HL7 ADT^A01 message for patient admission."""
        pass

    @abstractmethod
    async def create_discharge_message(self, patient: Patient, discharge_data: Dict[str, Any]) -> HL7Message:
        """Create an HL7 ADT^A03 message for patient discharge."""
        pass

    @abstractmethod
    async def send_message(self, message: HL7Message) -> HL7Message:
        """Send HL7 message via MLLP and wait for ACK."""
        pass

    @abstractmethod
    async def parse_ack(self, ack_content: str) -> Dict[str, Any]:
        """Parse ACK message and extract status."""
        pass


class IFHIRService(ABC):
    """Interface for FHIR API service."""

    @abstractmethod
    async def create_patient(self, patient: Patient) -> Dict[str, Any]:
        """Create a patient using FHIR API."""
        pass

    @abstractmethod
    async def get_patient(self, patient_id: str) -> Optional[Patient]:
        """Retrieve a patient using FHIR API."""
        pass

    @abstractmethod
    async def search_patients(self, search_params: Dict[str, Any]) -> List[Patient]:
        """Search for patients using FHIR API."""
        pass

    @abstractmethod
    async def create_observation(self, lab_result: LabResult) -> Dict[str, Any]:
        """Create an observation (lab result) using FHIR API."""
        pass

    @abstractmethod
    async def get_observations(self, patient_id: str, params: Optional[Dict[str, Any]] = None) -> List[LabResult]:
        """Retrieve observations for a patient."""
        pass


class IDataGeneratorService(ABC):
    """Interface for test data generation service."""

    @abstractmethod
    def generate_patient(self, parameters: Optional[Dict[str, Any]] = None) -> Patient:
        """Generate a fake patient with realistic data."""
        pass

    @abstractmethod
    def generate_patients(self, count: int, parameters: Optional[Dict[str, Any]] = None) -> List[Patient]:
        """Generate multiple fake patients."""
        pass

    @abstractmethod
    def generate_lab_result(self, patient_id: str, parameters: Optional[Dict[str, Any]] = None) -> LabResult:
        """Generate a fake lab result."""
        pass


class IMessageRepository(ABC):
    """Interface for message persistence repository."""

    @abstractmethod
    async def save_message(self, message: HL7Message) -> None:
        """Save an HL7 message to the repository."""
        pass

    @abstractmethod
    async def get_message(self, message_id: str) -> Optional[HL7Message]:
        """Retrieve a message by ID."""
        pass

    @abstractmethod
    async def get_messages_by_session(self, session_id: str) -> List[HL7Message]:
        """Retrieve all messages for a session."""
        pass


class IOperationRepository(ABC):
    """Interface for operation result persistence."""

    @abstractmethod
    async def save_operation(self, operation: OperationResult) -> None:
        """Save an operation result."""
        pass

    @abstractmethod
    async def get_operation(self, operation_id: str) -> Optional[OperationResult]:
        """Retrieve an operation by ID."""
        pass

    @abstractmethod
    async def get_operations_by_session(self, session_id: str) -> List[OperationResult]:
        """Retrieve all operations for a session."""
        pass


class IContextRepository(ABC):
    """Interface for conversation context persistence."""

    @abstractmethod
    async def save_context(self, context: ConversationContext) -> None:
        """Save conversation context."""
        pass

    @abstractmethod
    async def get_context(self, session_id: str) -> Optional[ConversationContext]:
        """Retrieve conversation context by session ID."""
        pass

    @abstractmethod
    async def update_context(self, context: ConversationContext) -> None:
        """Update existing conversation context."""
        pass
