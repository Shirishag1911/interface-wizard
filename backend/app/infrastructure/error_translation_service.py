"""Error Translation Service - Converts technical errors to plain language."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from loguru import logger

from app.domain.entities import OperationResult, OperationStatus


@dataclass
class ErrorContext:
    """Context information for error translation."""
    error_code: Optional[str] = None
    error_message: str = ""
    patient_name: Optional[str] = None
    mrn: Optional[str] = None
    operation_type: Optional[str] = None
    technical_details: Optional[Dict[str, Any]] = None


class ErrorTranslationService:
    """
    Service for translating technical errors into user-friendly messages.

    Implements plain language error guidance as per URS FR-4.
    """

    def __init__(self):
        # Map of error patterns to user-friendly messages
        self.error_patterns = {
            'duplicate': {
                'pattern': r'duplicate|already exists|unique constraint',
                'template': "I couldn't create {entity} because {identifier} already exists in the system. {suggestion}",
                'suggestions': [
                    "Would you like to update the existing record instead?",
                    "Try using a different Medical Record Number (MRN).",
                    "Check if this patient was created previously."
                ]
            },
            'missing_field': {
                'pattern': r'required field|missing|cannot be null|not provided',
                'template': "{field_name} is required to {action}. {suggestion}",
                'suggestions': [
                    "Please provide the missing information and try again.",
                    "You can add this information by including it in your command."
                ]
            },
            'invalid_format': {
                'pattern': r'invalid format|malformed|incorrect format',
                'template': "The {field_name} you provided doesn't match the expected format. {suggestion}",
                'suggestions': [
                    "Please check the format and try again.",
                    "For dates, use YYYY-MM-DD format (e.g., 1990-05-15).",
                    "For phone numbers, use XXX-XXX-XXXX format."
                ]
            },
            'connection_error': {
                'pattern': r'connection refused|timeout|network|unreachable',
                'template': "I'm having trouble connecting to the healthcare system. {suggestion}",
                'suggestions': [
                    "Please check if Mirth Connect is running.",
                    "Verify that the MLLP port (6661) is accessible.",
                    "Try again in a moment - this might be a temporary issue."
                ]
            },
            'ack_error': {
                'pattern': r'ACK.*error|AE|AR|rejected',
                'template': "The healthcare system rejected the patient record. {reason} {suggestion}",
                'suggestions': [
                    "Please check the error details and correct any issues.",
                    "Contact your system administrator if this persists."
                ]
            },
            'validation_error': {
                'pattern': r'validation|invalid|not allowed',
                'template': "{field_name} validation failed. {reason} {suggestion}",
                'suggestions': [
                    "Please review the data and make corrections.",
                    "Ensure all required fields are provided with valid values."
                ]
            }
        }

    async def translate_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None
    ) -> str:
        """
        Translate technical error to user-friendly message.

        Args:
            error: Exception that occurred
            context: Additional context about the error

        Returns:
            User-friendly error message with guidance
        """
        error_message = str(error)
        context = context or ErrorContext(error_message=error_message)

        # Try to match error pattern
        for error_type, config in self.error_patterns.items():
            import re
            if re.search(config['pattern'], error_message, re.IGNORECASE):
                return await self._format_error_message(error_type, config, context)

        # Default fallback message
        return self._create_default_message(error_message, context)

    async def translate_ack_error(
        self,
        ack_status: str,
        ack_message: str,
        context: Optional[ErrorContext] = None
    ) -> str:
        """
        Translate HL7 ACK error codes to plain language.

        Args:
            ack_status: ACK status code (AA, AE, AR, etc.)
            ack_message: ACK message content
            context: Additional context

        Returns:
            User-friendly error explanation
        """
        context = context or ErrorContext()

        ack_translations = {
            'AE': "The healthcare system found an error while processing",
            'AR': "The healthcare system rejected",
            'CA': "The healthcare system cancelled",
            'CE': "The healthcare system encountered a processing error",
            'CR': "The healthcare system rejected"
        }

        status_text = ack_translations.get(ack_status, "The healthcare system responded with")

        entity = "the patient record"
        if context.patient_name:
            entity = f"patient {context.patient_name}"

        message = f"{status_text} {entity}."

        # Extract error details from ACK message
        if "duplicate" in ack_message.lower():
            message += " The patient already exists in the system."
            message += " Would you like to update the existing record instead, or use a different identifier?"
        elif "required" in ack_message.lower() or "missing" in ack_message.lower():
            message += " Some required information is missing."
            message += " Please provide all necessary fields and try again."
        elif "invalid" in ack_message.lower():
            message += " Some of the data provided is in an invalid format."
            message += " Please check your input and ensure all fields match the expected format."
        else:
            message += f" Error details: {ack_message}"
            message += " Please review the error and try again."

        return message

    async def create_validation_error_message(
        self,
        validation_errors: List[str],
        validation_warnings: List[str],
        field_issues: Dict[str, List[str]]
    ) -> str:
        """
        Create user-friendly message from validation results.

        Args:
            validation_errors: List of validation errors
            validation_warnings: List of validation warnings
            field_issues: Dictionary of field-specific issues

        Returns:
            Formatted error message with guidance
        """
        if not validation_errors and not validation_warnings:
            return ""

        message_parts = []

        if validation_errors:
            message_parts.append("I found some issues that need to be fixed:")
            for idx, error in enumerate(validation_errors[:5], 1):  # Limit to 5
                message_parts.append(f"  {idx}. {error}")

            # Add field-specific guidance
            if field_issues:
                message_parts.append("\nHere's how to fix them:")
                for field, issues in list(field_issues.items())[:3]:  # Limit to 3 fields
                    message_parts.append(f"  • {field}: {issues[0]}")

        if validation_warnings:
            if validation_errors:
                message_parts.append("\nAlso, I noticed some warnings:")
            else:
                message_parts.append("I noticed some potential issues:")

            for idx, warning in enumerate(validation_warnings[:3], 1):
                message_parts.append(f"  {idx}. {warning}")

        # Add helpful suggestion
        if validation_errors:
            message_parts.append("\nPlease correct these issues and try again.")
        else:
            message_parts.append("\nYou can continue, but you may want to review these warnings.")

        return "\n".join(message_parts)

    async def create_success_message(
        self,
        operation_result: OperationResult,
        include_details: bool = True
    ) -> str:
        """
        Create user-friendly success message.

        Args:
            operation_result: Result of the operation
            include_details: Whether to include detailed information

        Returns:
            Formatted success message
        """
        if operation_result.status != OperationStatus.SUCCESS:
            return operation_result.message

        message_parts = ["✓ Success!"]

        # Add operation-specific message
        if operation_result.data:
            patient_count = operation_result.data.get('total_patients', 0)
            if patient_count > 1:
                message_parts.append(f"Created {patient_count} patient records successfully.")
            elif patient_count == 1:
                patient_name = operation_result.data.get('patient_name', 'the patient')
                message_parts.append(f"Created patient record for {patient_name}.")

        # Add details if requested
        if include_details and operation_result.records_affected:
            message_parts.append(f"\nRecords affected: {operation_result.records_affected}")

            if operation_result.records_succeeded:
                message_parts.append(f"Successful: {operation_result.records_succeeded}")

            if operation_result.records_failed > 0:
                message_parts.append(f"Failed: {operation_result.records_failed}")
                message_parts.append("\nPlease review the failed records and try again.")

        # Add protocol information
        if operation_result.protocol_used:
            message_parts.append(f"\nData sent via {operation_result.protocol_used.value.upper()} protocol.")

        return " ".join(message_parts)

    async def _format_error_message(
        self,
        error_type: str,
        config: Dict[str, Any],
        context: ErrorContext
    ) -> str:
        """Format error message using template and context."""
        import random

        # Select a suggestion
        suggestion = random.choice(config['suggestions'])

        # Build entity description
        entity = "patient record"
        identifier = ""

        if context.patient_name:
            entity = f"patient {context.patient_name}"

        if context.mrn:
            identifier = f"with MRN {context.mrn}"

        # Get field name from context
        field_name = self._extract_field_name(context.error_message)

        # Get action from operation type
        action = context.operation_type or "complete this operation"

        # Format the template
        message = config['template'].format(
            entity=entity,
            identifier=identifier,
            field_name=field_name,
            action=action,
            suggestion=suggestion,
            reason=""
        )

        return message

    def _create_default_message(
        self,
        error_message: str,
        context: ErrorContext
    ) -> str:
        """Create default error message when no pattern matches."""
        entity = "the operation"

        if context.patient_name:
            entity = f"patient {context.patient_name}"

        message = f"I encountered an issue while processing {entity}. "

        # Try to make the error message more user-friendly
        simplified_error = self._simplify_error_message(error_message)
        message += simplified_error

        message += " Please try again or contact support if the issue persists."

        return message

    def _extract_field_name(self, error_message: str) -> str:
        """Extract field name from error message."""
        import re

        # Try to find field name in quotes
        match = re.search(r"'(\w+)'|\"(\w+)\"", error_message)
        if match:
            return match.group(1) or match.group(2)

        # Try to find common field patterns
        field_patterns = {
            r'first.?name': 'First Name',
            r'last.?name': 'Last Name',
            r'date.?of.?birth|dob': 'Date of Birth',
            r'mrn|medical.?record': 'Medical Record Number',
            r'ssn|social.?security': 'Social Security Number',
            r'phone|telephone': 'Phone Number',
            r'email': 'Email Address',
            r'address': 'Address',
        }

        for pattern, name in field_patterns.items():
            if re.search(pattern, error_message, re.IGNORECASE):
                return name

        return "the required field"

    def _simplify_error_message(self, error_message: str) -> str:
        """Simplify technical error message."""
        # Remove technical stack traces
        if '\n' in error_message:
            error_message = error_message.split('\n')[0]

        # Remove SQL statements
        import re
        error_message = re.sub(r'SQL:.*', '', error_message, flags=re.IGNORECASE)

        # Remove file paths
        error_message = re.sub(r'[\/\\][\w\/\\]+\.py', '', error_message)

        # Capitalize first letter
        if error_message:
            error_message = error_message[0].upper() + error_message[1:]

        return error_message
