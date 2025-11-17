"""Data generator service for creating test data."""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random
from faker import Faker

from app.domain.entities import Patient, LabResult
from app.domain.interfaces import IDataGeneratorService


class FakerDataGenerator(IDataGeneratorService):
    """Test data generator using Faker library."""

    def __init__(self):
        self.faker = Faker()
        self.blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        self.common_allergies = [
            "Penicillin",
            "Peanuts",
            "Latex",
            "Sulfa drugs",
            "Aspirin",
            "Pollen",
            "Shellfish",
            "Eggs",
        ]

    def generate_patient(self, parameters: Optional[Dict[str, Any]] = None) -> Patient:
        """Generate a single patient with realistic data."""
        params = parameters or {}

        # Use provided values or generate fake ones
        first_name = params.get("first_name") or self.faker.first_name()
        last_name = params.get("last_name") or self.faker.last_name()
        gender = params.get("gender") or random.choice(["M", "F"])

        # Generate date of birth
        if "date_of_birth" in params:
            dob = params["date_of_birth"]
        elif "age" in params:
            age = params["age"]
            dob = datetime.now() - timedelta(days=age * 365)
        else:
            dob = self.faker.date_of_birth(minimum_age=18, maximum_age=90)

        # Generate allergies
        allergies = params.get("allergies", [])
        if not allergies and random.random() > 0.5:
            num_allergies = random.randint(1, 3)
            allergies = random.sample(self.common_allergies, num_allergies)

        return Patient(
            mrn=params.get("mrn") or f"MRN{self.faker.random_number(digits=8)}",
            first_name=first_name,
            last_name=last_name,
            middle_name=params.get("middle_name") or (self.faker.first_name() if random.random() > 0.7 else None),
            date_of_birth=dob,
            gender=gender,
            ssn=params.get("ssn") or self.faker.ssn(),
            address=params.get("address") or self.faker.street_address(),
            city=params.get("city") or self.faker.city(),
            state=params.get("state") or self.faker.state_abbr(),
            zip_code=params.get("zip_code") or self.faker.zipcode(),
            phone=params.get("phone") or self.faker.phone_number(),
            email=params.get("email") or self.faker.email(),
            blood_type=params.get("blood_type") or random.choice(self.blood_types),
            allergies=allergies,
            metadata=params.get("metadata", {}),
        )

    def generate_patients(self, count: int, parameters: Optional[Dict[str, Any]] = None) -> List[Patient]:
        """Generate multiple patients."""
        return [self.generate_patient(parameters) for _ in range(count)]

    def generate_lab_result(self, patient_id: str, parameters: Optional[Dict[str, Any]] = None) -> LabResult:
        """Generate a fake lab result."""
        params = parameters or {}

        # Common lab tests
        lab_tests = {
            "CBC": [
                ("WBC", "7.2", "10^9/L", "4.0-11.0"),
                ("RBC", "4.8", "10^12/L", "4.5-5.9"),
                ("Hemoglobin", "14.5", "g/dL", "13.5-17.5"),
                ("Hematocrit", "42", "%", "38-50"),
                ("Platelets", "220", "10^9/L", "150-400"),
            ],
            "BMP": [
                ("Sodium", "140", "mmol/L", "135-145"),
                ("Potassium", "4.0", "mmol/L", "3.5-5.0"),
                ("Chloride", "102", "mmol/L", "98-107"),
                ("CO2", "24", "mmol/L", "22-29"),
                ("Glucose", "95", "mg/dL", "70-100"),
            ],
            "Lipid Panel": [
                ("Total Cholesterol", "185", "mg/dL", "<200"),
                ("HDL", "55", "mg/dL", ">40"),
                ("LDL", "110", "mg/dL", "<100"),
                ("Triglycerides", "100", "mg/dL", "<150"),
            ],
        }

        test_type = params.get("test_type", "CBC")
        test_data = lab_tests.get(test_type, lab_tests["CBC"])
        test_name, result_value, unit, reference_range = random.choice(test_data)

        return LabResult(
            observation_id=f"OBS{self.faker.random_number(digits=10)}",
            patient_id=patient_id,
            test_name=test_name,
            test_code=params.get("test_code", test_name.upper().replace(" ", "_")),
            result_value=result_value,
            unit=unit,
            reference_range=reference_range,
            status="F",  # Final
            observed_datetime=params.get("observed_datetime", datetime.now() - timedelta(hours=random.randint(1, 48))),
            reported_datetime=params.get("reported_datetime", datetime.now()),
            performing_organization="Interface Wizard Test Lab",
            metadata=params.get("metadata", {}),
        )
