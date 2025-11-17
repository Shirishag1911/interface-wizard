"""FHIR API Service implementation."""
from typing import List, Optional, Dict, Any
import httpx
from loguru import logger
from datetime import datetime

from app.config import settings
from app.domain.entities import Patient, LabResult
from app.domain.interfaces import IFHIRService


class FHIRAPIService(IFHIRService):
    """FHIR R4 API service implementation."""

    def __init__(self):
        self.base_url = settings.FHIR_BASE_URL
        self.timeout = 30.0

    async def create_patient(self, patient: Patient) -> Dict[str, Any]:
        """Create a patient using FHIR API."""
        try:
            fhir_patient = self._patient_to_fhir(patient)

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/Patient",
                    json=fhir_patient,
                    headers={"Content-Type": "application/fhir+json"},
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Error creating FHIR patient: {str(e)}", exc_info=True)
            raise

    async def get_patient(self, patient_id: str) -> Optional[Patient]:
        """Retrieve a patient using FHIR API."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/Patient/{patient_id}",
                    headers={"Accept": "application/fhir+json"},
                )

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                fhir_data = response.json()
                return self._fhir_to_patient(fhir_data)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            logger.error(f"Error getting FHIR patient: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Error getting FHIR patient: {str(e)}", exc_info=True)
            raise

    async def search_patients(self, search_params: Dict[str, Any]) -> List[Patient]:
        """Search for patients using FHIR API."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/Patient",
                    params=search_params,
                    headers={"Accept": "application/fhir+json"},
                )
                response.raise_for_status()

                bundle = response.json()
                patients = []

                if bundle.get("resourceType") == "Bundle" and bundle.get("entry"):
                    for entry in bundle["entry"]:
                        if entry.get("resource"):
                            patients.append(self._fhir_to_patient(entry["resource"]))

                return patients

        except Exception as e:
            logger.error(f"Error searching FHIR patients: {str(e)}", exc_info=True)
            return []

    async def create_observation(self, lab_result: LabResult) -> Dict[str, Any]:
        """Create an observation (lab result) using FHIR API."""
        try:
            fhir_observation = self._lab_result_to_fhir(lab_result)

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/Observation",
                    json=fhir_observation,
                    headers={"Content-Type": "application/fhir+json"},
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Error creating FHIR observation: {str(e)}", exc_info=True)
            raise

    async def get_observations(
        self, patient_id: str, params: Optional[Dict[str, Any]] = None
    ) -> List[LabResult]:
        """Retrieve observations for a patient."""
        try:
            search_params = {"patient": patient_id}
            if params:
                search_params.update(params)

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/Observation",
                    params=search_params,
                    headers={"Accept": "application/fhir+json"},
                )
                response.raise_for_status()

                bundle = response.json()
                lab_results = []

                if bundle.get("resourceType") == "Bundle" and bundle.get("entry"):
                    for entry in bundle["entry"]:
                        if entry.get("resource"):
                            lab_results.append(self._fhir_to_lab_result(entry["resource"]))

                return lab_results

        except Exception as e:
            logger.error(f"Error getting FHIR observations: {str(e)}", exc_info=True)
            return []

    def _patient_to_fhir(self, patient: Patient) -> Dict[str, Any]:
        """Convert Patient entity to FHIR Patient resource."""
        fhir_patient = {
            "resourceType": "Patient",
            "identifier": [
                {
                    "system": "urn:oid:2.16.840.1.113883.19.5",
                    "value": patient.mrn or "",
                }
            ],
            "name": [
                {
                    "use": "official",
                    "family": patient.last_name or "",
                    "given": [patient.first_name or ""],
                }
            ],
        }

        if patient.middle_name:
            fhir_patient["name"][0]["given"].append(patient.middle_name)

        if patient.gender:
            fhir_patient["gender"] = patient.gender.lower()

        if patient.date_of_birth:
            fhir_patient["birthDate"] = patient.date_of_birth.strftime("%Y-%m-%d")

        if patient.phone:
            fhir_patient["telecom"] = [
                {"system": "phone", "value": patient.phone, "use": "home"}
            ]

        if patient.email:
            if "telecom" not in fhir_patient:
                fhir_patient["telecom"] = []
            fhir_patient["telecom"].append(
                {"system": "email", "value": patient.email}
            )

        if patient.address:
            fhir_patient["address"] = [
                {
                    "use": "home",
                    "line": [patient.address],
                    "city": patient.city or "",
                    "state": patient.state or "",
                    "postalCode": patient.zip_code or "",
                }
            ]

        return fhir_patient

    def _fhir_to_patient(self, fhir_data: Dict[str, Any]) -> Patient:
        """Convert FHIR Patient resource to Patient entity."""
        patient = Patient()

        if fhir_data.get("id"):
            patient.patient_id = fhir_data["id"]

        if fhir_data.get("identifier"):
            patient.mrn = fhir_data["identifier"][0].get("value")

        if fhir_data.get("name") and len(fhir_data["name"]) > 0:
            name = fhir_data["name"][0]
            patient.last_name = name.get("family")
            if name.get("given") and len(name["given"]) > 0:
                patient.first_name = name["given"][0]
                if len(name["given"]) > 1:
                    patient.middle_name = name["given"][1]

        if fhir_data.get("gender"):
            patient.gender = fhir_data["gender"].upper()[0]

        if fhir_data.get("birthDate"):
            patient.date_of_birth = datetime.strptime(fhir_data["birthDate"], "%Y-%m-%d")

        if fhir_data.get("telecom"):
            for telecom in fhir_data["telecom"]:
                if telecom.get("system") == "phone":
                    patient.phone = telecom.get("value")
                elif telecom.get("system") == "email":
                    patient.email = telecom.get("value")

        if fhir_data.get("address") and len(fhir_data["address"]) > 0:
            address = fhir_data["address"][0]
            if address.get("line"):
                patient.address = address["line"][0]
            patient.city = address.get("city")
            patient.state = address.get("state")
            patient.zip_code = address.get("postalCode")

        return patient

    def _lab_result_to_fhir(self, lab_result: LabResult) -> Dict[str, Any]:
        """Convert LabResult entity to FHIR Observation resource."""
        observation = {
            "resourceType": "Observation",
            "status": lab_result.status or "final",
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": lab_result.test_code or "",
                        "display": lab_result.test_name or "",
                    }
                ]
            },
            "subject": {
                "reference": f"Patient/{lab_result.patient_id}"
            },
        }

        if lab_result.result_value:
            observation["valueQuantity"] = {
                "value": float(lab_result.result_value) if lab_result.result_value.replace('.', '').isdigit() else None,
                "unit": lab_result.unit or "",
            }

        if lab_result.observed_datetime:
            observation["effectiveDateTime"] = lab_result.observed_datetime.isoformat()

        if lab_result.reference_range:
            observation["referenceRange"] = [
                {"text": lab_result.reference_range}
            ]

        return observation

    def _fhir_to_lab_result(self, fhir_data: Dict[str, Any]) -> LabResult:
        """Convert FHIR Observation resource to LabResult entity."""
        lab_result = LabResult()

        if fhir_data.get("id"):
            lab_result.observation_id = fhir_data["id"]

        if fhir_data.get("subject") and fhir_data["subject"].get("reference"):
            ref = fhir_data["subject"]["reference"]
            lab_result.patient_id = ref.split("/")[-1]

        if fhir_data.get("code"):
            coding = fhir_data["code"].get("coding", [{}])[0]
            lab_result.test_code = coding.get("code")
            lab_result.test_name = coding.get("display")

        if fhir_data.get("valueQuantity"):
            value_qty = fhir_data["valueQuantity"]
            lab_result.result_value = str(value_qty.get("value", ""))
            lab_result.unit = value_qty.get("unit", "")

        if fhir_data.get("effectiveDateTime"):
            lab_result.observed_datetime = datetime.fromisoformat(
                fhir_data["effectiveDateTime"].replace("Z", "+00:00")
            )

        if fhir_data.get("referenceRange"):
            lab_result.reference_range = fhir_data["referenceRange"][0].get("text")

        lab_result.status = fhir_data.get("status", "final")

        return lab_result
