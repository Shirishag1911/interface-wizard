"""
CSV Processing Service for Interface Wizard
Handles CSV file parsing and conversion to Patient entities
"""
import csv
import io
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from app.domain.entities import Patient


class CSVProcessingService:
    """Service to process CSV files containing patient data"""

    # Mapping of common CSV column names to Patient fields
    FIELD_MAPPINGS = {
        # Patient ID fields
        'patient_id': ['patient_id', 'patientid', 'id', 'patient id'],
        'mrn': ['mrn', 'medical_record_number', 'medical record number', 'patient mrn'],

        # Name fields
        'first_name': ['first_name', 'firstname', 'first name', 'fname', 'given_name'],
        'last_name': ['last_name', 'lastname', 'last name', 'lname', 'family_name', 'surname'],
        'middle_name': ['middle_name', 'middlename', 'middle name', 'mname', 'middle'],

        # Demographics
        'date_of_birth': ['date_of_birth', 'dob', 'birth_date', 'birthdate', 'date of birth'],
        'gender': ['gender', 'sex'],
        'ssn': ['ssn', 'social_security_number', 'social security number'],

        # Contact information
        'address': ['address', 'street', 'street_address', 'address1'],
        'city': ['city'],
        'state': ['state', 'province'],
        'zip_code': ['zip_code', 'zip', 'zipcode', 'postal_code', 'postalcode'],
        'phone': ['phone', 'phone_number', 'telephone', 'mobile', 'contact'],
        'email': ['email', 'email_address', 'e-mail'],

        # Medical information
        'blood_type': ['blood_type', 'bloodtype', 'blood group', 'blood_group'],
        'allergies': ['allergies', 'allergy'],
    }

    def __init__(self):
        """Initialize CSV processing service"""
        logger.info("CSV Processing Service initialized")

    def parse_csv(self, csv_content: bytes, encoding: str = 'utf-8') -> List[Patient]:
        """
        Parse CSV file content and convert to Patient entities

        Args:
            csv_content: Raw CSV file bytes
            encoding: File encoding (default: utf-8)

        Returns:
            List of Patient entities parsed from CSV

        Raises:
            ValueError: If CSV format is invalid or required fields are missing
        """
        try:
            # Decode bytes to string
            csv_string = csv_content.decode(encoding)

            # Parse CSV using DictReader
            csv_file = io.StringIO(csv_string)
            reader = csv.DictReader(csv_file)

            # Check if CSV has headers
            if not reader.fieldnames:
                raise ValueError("CSV file must contain headers")

            logger.info(f"CSV headers detected: {reader.fieldnames}")

            # Build column mapping
            column_mapping = self._build_column_mapping(reader.fieldnames)
            logger.info(f"Column mapping: {column_mapping}")

            # Parse rows
            patients = []
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                try:
                    patient = self._parse_patient_row(row, column_mapping, row_num)
                    if patient:
                        patients.append(patient)
                except Exception as e:
                    logger.warning(f"Skipping row {row_num}: {str(e)}")
                    continue

            logger.info(f"Successfully parsed {len(patients)} patients from CSV")
            return patients

        except UnicodeDecodeError as e:
            raise ValueError(f"Invalid CSV encoding. Please ensure file is {encoding} encoded: {str(e)}")
        except csv.Error as e:
            raise ValueError(f"Invalid CSV format: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing CSV: {str(e)}")
            raise ValueError(f"Failed to parse CSV file: {str(e)}")

    def _build_column_mapping(self, headers: List[str]) -> Dict[str, str]:
        """
        Build mapping from CSV columns to Patient fields

        Args:
            headers: CSV header row

        Returns:
            Dictionary mapping patient field names to CSV column names
        """
        mapping = {}

        for patient_field, csv_variants in self.FIELD_MAPPINGS.items():
            for header in headers:
                # Case-insensitive matching with whitespace normalization
                normalized_header = header.lower().strip()
                if normalized_header in csv_variants:
                    mapping[patient_field] = header
                    break

        return mapping

    def _parse_patient_row(
        self,
        row: Dict[str, str],
        column_mapping: Dict[str, str],
        row_num: int
    ) -> Optional[Patient]:
        """
        Parse a single CSV row into a Patient entity

        Args:
            row: CSV row as dictionary
            column_mapping: Mapping of patient fields to CSV columns
            row_num: Row number for error reporting

        Returns:
            Patient entity or None if row is empty/invalid
        """
        # Check if row is empty
        if not any(row.values()):
            return None

        # Extract values using column mapping
        patient_data = {}

        for patient_field, csv_column in column_mapping.items():
            value = row.get(csv_column, '').strip()
            if value:
                patient_data[patient_field] = value

        # Validate required fields
        if not patient_data.get('first_name') and not patient_data.get('last_name'):
            logger.warning(f"Row {row_num}: Missing required name fields")
            return None

        # Parse date of birth
        dob = None
        if 'date_of_birth' in patient_data:
            dob = self._parse_date(patient_data['date_of_birth'])
            if not dob:
                logger.warning(f"Row {row_num}: Invalid date format for date_of_birth: {patient_data['date_of_birth']}")

        # Parse allergies (comma-separated or semicolon-separated)
        allergies = []
        if 'allergies' in patient_data:
            allergies_str = patient_data['allergies']
            if ';' in allergies_str:
                allergies = [a.strip() for a in allergies_str.split(';') if a.strip()]
            elif ',' in allergies_str:
                allergies = [a.strip() for a in allergies_str.split(',') if a.strip()]
            else:
                allergies = [allergies_str] if allergies_str else []

        # Normalize gender
        gender = self._normalize_gender(patient_data.get('gender'))

        # Create Patient entity
        patient = Patient(
            patient_id=patient_data.get('patient_id'),
            mrn=patient_data.get('mrn'),
            first_name=patient_data.get('first_name'),
            last_name=patient_data.get('last_name'),
            middle_name=patient_data.get('middle_name'),
            date_of_birth=dob,
            gender=gender,
            ssn=patient_data.get('ssn'),
            address=patient_data.get('address'),
            city=patient_data.get('city'),
            state=patient_data.get('state'),
            zip_code=patient_data.get('zip_code'),
            phone=patient_data.get('phone'),
            email=patient_data.get('email'),
            blood_type=patient_data.get('blood_type'),
            allergies=allergies,
            metadata={'csv_row': row_num}
        )

        logger.debug(f"Parsed patient from row {row_num}: {patient.first_name} {patient.last_name}")
        return patient

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string in various formats

        Supported formats:
        - YYYY-MM-DD
        - MM/DD/YYYY
        - DD/MM/YYYY
        - YYYYMMDD

        Args:
            date_str: Date string to parse

        Returns:
            datetime object or None if parsing fails
        """
        date_formats = [
            '%Y-%m-%d',      # 2024-01-15
            '%m/%d/%Y',      # 01/15/2024
            '%d/%m/%Y',      # 15/01/2024
            '%Y%m%d',        # 20240115
            '%m-%d-%Y',      # 01-15-2024
            '%d-%m-%Y',      # 15-01-2024
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None

    def _normalize_gender(self, gender_str: Optional[str]) -> Optional[str]:
        """
        Normalize gender values to standard format

        Args:
            gender_str: Gender value from CSV

        Returns:
            Normalized gender ('Male', 'Female', 'Other') or None
        """
        if not gender_str:
            return None

        gender_lower = gender_str.lower().strip()

        # Male variations
        if gender_lower in ['m', 'male', 'man']:
            return 'Male'

        # Female variations
        if gender_lower in ['f', 'female', 'woman']:
            return 'Female'

        # Other
        if gender_lower in ['o', 'other', 'non-binary', 'nb', 'unknown', 'u']:
            return 'Other'

        # Return as-is if no match (will be logged as warning by caller)
        return gender_str

    def validate_csv_structure(self, csv_content: bytes, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Validate CSV structure and return analysis

        Args:
            csv_content: Raw CSV file bytes
            encoding: File encoding

        Returns:
            Dictionary with validation results
        """
        try:
            csv_string = csv_content.decode(encoding)
            csv_file = io.StringIO(csv_string)
            reader = csv.DictReader(csv_file)

            if not reader.fieldnames:
                return {
                    'valid': False,
                    'error': 'CSV file must contain headers'
                }

            # Build column mapping
            column_mapping = self._build_column_mapping(reader.fieldnames)

            # Count rows
            row_count = sum(1 for _ in reader)

            # Check for required fields
            has_name_field = 'first_name' in column_mapping or 'last_name' in column_mapping

            return {
                'valid': True,
                'headers': list(reader.fieldnames),
                'row_count': row_count,
                'mapped_fields': list(column_mapping.keys()),
                'unmapped_headers': [h for h in reader.fieldnames if h not in column_mapping.values()],
                'has_required_fields': has_name_field,
                'warnings': [] if has_name_field else ['No name fields detected (first_name or last_name)']
            }

        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
