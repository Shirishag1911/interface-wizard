"""HL7 Validation Service - Validates HL7 messages before transmission."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from hl7apy.core import Message
from hl7apy.validation import Validator
from hl7apy.exceptions import ValidationError
from loguru import logger

from app.domain.entities import Patient
from app.domain.interfaces import IValidationService


@dataclass
class ValidationResult:
    """Result of validation check."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    field_issues: Dict[str, List[str]]


class HL7ValidationService(IValidationService):
    """Service for validating HL7 messages and patient data."""

    def __init__(self):
        self.validator = Validator()
        self.required_patient_fields = ['last_name', 'first_name']
        self.required_hl7_segments = ['MSH', 'EVN', 'PID']

    async def validate_patient_data(self, patient: Patient) -> ValidationResult:
        """
        Validate patient data before creating HL7 message.

        Args:
            patient: Patient entity to validate

        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []
        field_issues = {}

        # Check required fields
        if not patient.first_name and not patient.last_name:
            errors.append("Patient must have at least a first name or last name")
            field_issues['name'] = ["Missing both first and last name"]

        # Validate SSN format if provided
        if patient.ssn:
            if not self._validate_ssn(patient.ssn):
                warnings.append(f"SSN format appears invalid: {patient.ssn}")
                field_issues['ssn'] = ["Invalid format - expected XXX-XX-XXXX or XXXXXXXXX"]

        # Validate date of birth
        if patient.date_of_birth:
            from datetime import datetime
            if patient.date_of_birth > datetime.now():
                errors.append("Date of birth cannot be in the future")
                field_issues['date_of_birth'] = ["Future date not allowed"]

        # Validate gender
        if patient.gender:
            valid_genders = ['Male', 'Female', 'Other', 'M', 'F', 'O', 'Unknown', 'U']
            if patient.gender not in valid_genders:
                warnings.append(f"Gender value '{patient.gender}' will be normalized")
                field_issues['gender'] = [f"Non-standard value: {patient.gender}"]

        # Validate email format
        if patient.email:
            if not self._validate_email(patient.email):
                warnings.append(f"Email format appears invalid: {patient.email}")
                field_issues['email'] = ["Invalid email format"]

        # Validate phone format
        if patient.phone:
            if not self._validate_phone(patient.phone):
                warnings.append(f"Phone format appears non-standard: {patient.phone}")

        # Validate zip code
        if patient.zip_code:
            if not self._validate_zip(patient.zip_code):
                warnings.append(f"Zip code format appears invalid: {patient.zip_code}")

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            field_issues=field_issues
        )

    async def validate_hl7_message(self, hl7_message_content: str) -> ValidationResult:
        """
        Validate HL7 message structure and content.

        Args:
            hl7_message_content: HL7 message in ER7 format

        Returns:
            ValidationResult with any issues found
        """
        errors = []
        warnings = []
        field_issues = {}

        try:
            # Parse message
            from hl7apy.parser import parse_message
            msg = parse_message(hl7_message_content)

            # Validate message structure
            try:
                self.validator.validate(msg)
            except ValidationError as ve:
                errors.append(f"HL7 validation error: {str(ve)}")

            # Check required segments
            msg_segments = [seg.name for seg in msg.children]
            for required_seg in self.required_hl7_segments:
                if required_seg not in msg_segments:
                    errors.append(f"Missing required segment: {required_seg}")
                    field_issues[required_seg] = ["Required segment missing"]

            # Validate MSH segment
            if 'MSH' in msg_segments:
                msh = msg.msh

                # Check message type
                if not msh.msh_9 or str(msh.msh_9).strip() == '':
                    errors.append("Message type (MSH-9) is empty")

                # Check sending application
                if not msh.msh_3 or str(msh.msh_3).strip() == '':
                    warnings.append("Sending application (MSH-3) is empty")

                # Check version
                if msh.msh_12:
                    version = str(msh.msh_12)
                    if version not in ['2.3', '2.3.1', '2.4', '2.5', '2.5.1', '2.6', '2.7']:
                        warnings.append(f"HL7 version {version} may not be supported")

            # Validate PID segment
            if 'PID' in msg_segments:
                pid = msg.pid

                # Check patient identifier
                if not pid.pid_3 or str(pid.pid_3).strip() == '':
                    errors.append("Patient identifier (PID-3) is required")
                    field_issues['PID-3'] = ["Required field missing"]

                # Check patient name
                if not pid.pid_5 or str(pid.pid_5).strip() == '':
                    warnings.append("Patient name (PID-5) is empty")

        except Exception as e:
            logger.error(f"Error validating HL7 message: {str(e)}", exc_info=True)
            errors.append(f"Failed to parse HL7 message: {str(e)}")

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            field_issues=field_issues
        )

    async def check_for_duplicates(
        self,
        patient: Patient,
        existing_mrns: Optional[List[str]] = None
    ) -> ValidationResult:
        """
        Check if patient already exists based on MRN or SSN.

        Args:
            patient: Patient to check
            existing_mrns: Optional list of existing MRNs to check against

        Returns:
            ValidationResult indicating potential duplicates
        """
        errors = []
        warnings = []
        field_issues = {}

        # Check MRN if provided
        if patient.mrn and existing_mrns:
            if patient.mrn in existing_mrns:
                errors.append(f"Patient with MRN {patient.mrn} already exists")
                field_issues['mrn'] = ["Duplicate MRN found"]

        # Note: Actual database check would be done in repository layer
        # This is a placeholder for the validation interface

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            field_issues=field_issues
        )

    def _validate_ssn(self, ssn: str) -> bool:
        """Validate SSN format."""
        import re
        # Accept XXX-XX-XXXX or XXXXXXXXX
        pattern = r'^\d{3}-\d{2}-\d{4}$|^\d{9}$'
        return bool(re.match(pattern, ssn))

    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _validate_phone(self, phone: str) -> bool:
        """Validate phone format."""
        import re
        # Accept various formats: (123) 456-7890, 123-456-7890, 1234567890, etc.
        cleaned = re.sub(r'[^\d]', '', phone)
        return 10 <= len(cleaned) <= 15

    def _validate_zip(self, zip_code: str) -> bool:
        """Validate ZIP code format."""
        import re
        # Accept US ZIP: 12345 or 12345-6789
        pattern = r'^\d{5}(-\d{4})?$'
        return bool(re.match(pattern, zip_code))


class DataSanitizationService:
    """Service for sanitizing user input data."""

    @staticmethod
    def sanitize_patient_data(patient: Patient) -> Patient:
        """
        Sanitize patient data to prevent injection attacks.

        Args:
            patient: Patient entity with potentially unsafe data

        Returns:
            Patient with sanitized data
        """
        import html

        # Sanitize string fields
        if patient.first_name:
            patient.first_name = html.escape(patient.first_name.strip())

        if patient.last_name:
            patient.last_name = html.escape(patient.last_name.strip())

        if patient.middle_name:
            patient.middle_name = html.escape(patient.middle_name.strip())

        if patient.address:
            patient.address = html.escape(patient.address.strip())

        if patient.city:
            patient.city = html.escape(patient.city.strip())

        if patient.state:
            patient.state = html.escape(patient.state.strip())

        if patient.email:
            patient.email = patient.email.strip().lower()

        # Remove non-digit characters from phone
        if patient.phone:
            import re
            patient.phone = re.sub(r'[^\d\-\(\)\s\+]', '', patient.phone)

        # Normalize gender
        if patient.gender:
            gender_map = {
                'M': 'Male', 'MALE': 'Male',
                'F': 'Female', 'FEMALE': 'Female',
                'O': 'Other', 'OTHER': 'Other',
                'U': 'Unknown', 'UNKNOWN': 'Unknown',
            }
            patient.gender = gender_map.get(patient.gender.upper(), patient.gender)

        return patient
