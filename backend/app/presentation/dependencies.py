"""Dependency injection for FastAPI."""
from functools import lru_cache

from app.application.use_cases import ProcessCommandUseCase
from app.infrastructure.nlp_service import OpenAINLPService
from app.infrastructure.hl7_service import HL7v2Service
from app.infrastructure.fhir_service import FHIRAPIService
from app.infrastructure.data_generator import FakerDataGenerator
from app.infrastructure.csv_service import CSVProcessingService
from app.infrastructure.repositories import (
    InMemoryMessageRepository,
    InMemoryOperationRepository,
    InMemoryContextRepository,
)
from app.infrastructure.health_service import HealthCheckService


# Singleton instances
_nlp_service = None
_hl7_service = None
_fhir_service = None
_data_generator = None
_csv_service = None
_message_repo = None
_operation_repo = None
_context_repo = None
_health_service = None


def get_nlp_service() -> OpenAINLPService:
    """Get NLP service instance."""
    global _nlp_service
    if _nlp_service is None:
        _nlp_service = OpenAINLPService()
    return _nlp_service


def get_hl7_service() -> HL7v2Service:
    """Get HL7 service instance."""
    global _hl7_service
    if _hl7_service is None:
        _hl7_service = HL7v2Service()
    return _hl7_service


def get_fhir_service() -> FHIRAPIService:
    """Get FHIR service instance."""
    global _fhir_service
    if _fhir_service is None:
        _fhir_service = FHIRAPIService()
    return _fhir_service


def get_data_generator() -> FakerDataGenerator:
    """Get data generator instance."""
    global _data_generator
    if _data_generator is None:
        _data_generator = FakerDataGenerator()
    return _data_generator


def get_csv_service() -> CSVProcessingService:
    """Get CSV processing service instance."""
    global _csv_service
    if _csv_service is None:
        _csv_service = CSVProcessingService()
    return _csv_service


def get_message_repository() -> InMemoryMessageRepository:
    """Get message repository instance."""
    global _message_repo
    if _message_repo is None:
        _message_repo = InMemoryMessageRepository()
    return _message_repo


def get_operation_repository() -> InMemoryOperationRepository:
    """Get operation repository instance."""
    global _operation_repo
    if _operation_repo is None:
        _operation_repo = InMemoryOperationRepository()
    return _operation_repo


def get_context_repository() -> InMemoryContextRepository:
    """Get context repository instance."""
    global _context_repo
    if _context_repo is None:
        _context_repo = InMemoryContextRepository()
    return _context_repo


def get_health_service() -> HealthCheckService:
    """Get health check service instance."""
    global _health_service
    if _health_service is None:
        _health_service = HealthCheckService()
    return _health_service


def get_process_command_use_case() -> ProcessCommandUseCase:
    """Get ProcessCommand use case with all dependencies."""
    return ProcessCommandUseCase(
        nlp_service=get_nlp_service(),
        hl7_service=get_hl7_service(),
        fhir_service=get_fhir_service(),
        data_generator=get_data_generator(),
        operation_repo=get_operation_repository(),
        context_repo=get_context_repository(),
        message_repo=get_message_repository(),
    )
