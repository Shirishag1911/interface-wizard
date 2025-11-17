"""HL7 v2 Service implementation."""
import socket
import asyncio
from datetime import datetime
from typing import Dict, Any
from hl7apy.core import Message, Segment
from hl7apy.parser import parse_message
from loguru import logger

from app.config import settings
from app.domain.entities import Patient, LabResult, HL7Message, MessageType
from app.domain.interfaces import IHL7Service


class HL7v2Service(IHL7Service):
    """HL7 v2 messaging service implementation."""

    def __init__(self):
        self.facility = "INTERFACE_WIZARD"
        self.application = "IW"
        self.mllp_start = b'\x0b'
        self.mllp_end = b'\x1c\x0d'

    async def create_patient_message(self, patient: Patient) -> HL7Message:
        """Create an HL7 ADT^A28 message for adding person information."""
        try:
            # Create HL7 message
            msg = Message("ADT_A05")
            msg.msh.msh_3 = self.application
            msg.msh.msh_4 = self.facility
            msg.msh.msh_5 = "OpenEMR"
            msg.msh.msh_6 = "OpenEMR"
            msg.msh.msh_7 = datetime.now().strftime("%Y%m%d%H%M%S")
            msg.msh.msh_9 = "ADT^A28^ADT_A05"
            msg.msh.msh_10 = patient.mrn or str(datetime.now().timestamp())
            msg.msh.msh_11 = "P"  # Production
            msg.msh.msh_12 = "2.5"

            # EVN segment
            msg.add_segment("EVN")
            msg.evn.evn_1 = "A28"
            msg.evn.evn_2 = datetime.now().strftime("%Y%m%d%H%M%S")

            # PID segment
            msg.add_segment("PID")
            msg.pid.pid_1 = "1"
            msg.pid.pid_3 = patient.mrn or f"MRN{datetime.now().timestamp()}"

            # Patient name
            if patient.last_name and patient.first_name:
                msg.pid.pid_5 = f"{patient.last_name}^{patient.first_name}"
                if patient.middle_name:
                    msg.pid.pid_5 = f"{patient.last_name}^{patient.first_name}^{patient.middle_name}"

            # Date of birth
            if patient.date_of_birth:
                msg.pid.pid_7 = patient.date_of_birth.strftime("%Y%m%d")

            # Gender
            if patient.gender:
                msg.pid.pid_8 = patient.gender[0].upper()  # M or F

            # Address
            if patient.address:
                address_parts = [
                    patient.address or "",
                    "",  # Other designation
                    patient.city or "",
                    patient.state or "",
                    patient.zip_code or "",
                ]
                msg.pid.pid_11 = "^".join(address_parts)

            # Phone
            if patient.phone:
                msg.pid.pid_13 = patient.phone

            # SSN
            if patient.ssn:
                msg.pid.pid_19 = patient.ssn

            message_content = msg.to_er7()

            return HL7Message(
                message_type=MessageType.ADT_A28,
                message_content=message_content,
            )

        except Exception as e:
            logger.error(f"Error creating patient message: {str(e)}", exc_info=True)
            raise

    async def create_lab_result_message(self, lab_result: LabResult) -> HL7Message:
        """Create an HL7 ORU^R01 message for lab results."""
        try:
            msg = Message("ORU_R01")
            msg.msh.msh_3 = self.application
            msg.msh.msh_4 = self.facility
            msg.msh.msh_5 = "OpenEMR"
            msg.msh.msh_6 = "OpenEMR"
            msg.msh.msh_7 = datetime.now().strftime("%Y%m%d%H%M%S")
            msg.msh.msh_9 = "ORU^R01^ORU_R01"
            msg.msh.msh_10 = lab_result.observation_id or str(datetime.now().timestamp())
            msg.msh.msh_11 = "P"
            msg.msh.msh_12 = "2.5"

            # PID segment
            msg.add_segment("PID")
            msg.pid.pid_1 = "1"
            msg.pid.pid_3 = lab_result.patient_id

            # OBR segment (Observation Request)
            msg.add_segment("OBR")
            msg.obr.obr_1 = "1"
            msg.obr.obr_4 = lab_result.test_code or lab_result.test_name

            if lab_result.observed_datetime:
                msg.obr.obr_7 = lab_result.observed_datetime.strftime("%Y%m%d%H%M%S")

            # OBX segment (Observation Result)
            msg.add_segment("OBX")
            msg.obx.obx_1 = "1"
            msg.obx.obx_2 = "NM"  # Numeric
            msg.obx.obx_3 = lab_result.test_code or lab_result.test_name
            msg.obx.obx_5 = lab_result.result_value
            msg.obx.obx_6 = lab_result.unit or ""
            msg.obx.obx_7 = lab_result.reference_range or ""
            msg.obx.obx_11 = lab_result.status or "F"  # Final

            message_content = msg.to_er7()

            return HL7Message(
                message_type=MessageType.ORU_R01,
                message_content=message_content,
            )

        except Exception as e:
            logger.error(f"Error creating lab result message: {str(e)}", exc_info=True)
            raise

    async def create_admit_message(self, patient: Patient, admission_data: Dict[str, Any]) -> HL7Message:
        """Create an HL7 ADT^A01 message for patient admission."""
        try:
            msg = Message("ADT_A01")
            msg.msh.msh_3 = self.application
            msg.msh.msh_4 = self.facility
            msg.msh.msh_5 = "OpenEMR"
            msg.msh.msh_6 = "OpenEMR"
            msg.msh.msh_7 = datetime.now().strftime("%Y%m%d%H%M%S")
            msg.msh.msh_9 = "ADT^A01^ADT_A01"
            msg.msh.msh_10 = str(datetime.now().timestamp())
            msg.msh.msh_11 = "P"
            msg.msh.msh_12 = "2.5"

            # EVN segment
            msg.add_segment("EVN")
            msg.evn.evn_1 = "A01"
            admission_dt = admission_data.get("admission_datetime", datetime.now())
            msg.evn.evn_2 = admission_dt.strftime("%Y%m%d%H%M%S")

            # PID segment
            msg.add_segment("PID")
            msg.pid.pid_1 = "1"
            msg.pid.pid_3 = patient.patient_id or patient.mrn

            # PV1 segment (Patient Visit)
            msg.add_segment("PV1")
            msg.pv1.pv1_1 = "1"
            msg.pv1.pv1_2 = "I"  # Inpatient
            msg.pv1.pv1_3 = admission_data.get("location", "General Ward")
            msg.pv1.pv1_7 = admission_data.get("attending_doctor", "")
            msg.pv1.pv1_44 = admission_dt.strftime("%Y%m%d%H%M%S")

            message_content = msg.to_er7()

            return HL7Message(
                message_type=MessageType.ADT_A01,
                message_content=message_content,
            )

        except Exception as e:
            logger.error(f"Error creating admit message: {str(e)}", exc_info=True)
            raise

    async def create_discharge_message(self, patient: Patient, discharge_data: Dict[str, Any]) -> HL7Message:
        """Create an HL7 ADT^A03 message for patient discharge."""
        try:
            msg = Message("ADT_A03")
            msg.msh.msh_3 = self.application
            msg.msh.msh_4 = self.facility
            msg.msh.msh_5 = "OpenEMR"
            msg.msh.msh_6 = "OpenEMR"
            msg.msh.msh_7 = datetime.now().strftime("%Y%m%d%H%M%S")
            msg.msh.msh_9 = "ADT^A03^ADT_A03"
            msg.msh.msh_10 = str(datetime.now().timestamp())
            msg.msh.msh_11 = "P"
            msg.msh.msh_12 = "2.5"

            # EVN segment
            msg.add_segment("EVN")
            msg.evn.evn_1 = "A03"
            discharge_dt = discharge_data.get("discharge_datetime", datetime.now())
            msg.evn.evn_2 = discharge_dt.strftime("%Y%m%d%H%M%S")

            # PID segment
            msg.add_segment("PID")
            msg.pid.pid_1 = "1"
            msg.pid.pid_3 = patient.patient_id or patient.mrn

            # PV1 segment
            msg.add_segment("PV1")
            msg.pv1.pv1_1 = "1"
            msg.pv1.pv1_2 = "I"
            msg.pv1.pv1_36 = discharge_data.get("discharge_disposition", "")
            msg.pv1.pv1_45 = discharge_dt.strftime("%Y%m%d%H%M%S")

            message_content = msg.to_er7()

            return HL7Message(
                message_type=MessageType.ADT_A03,
                message_content=message_content,
            )

        except Exception as e:
            logger.error(f"Error creating discharge message: {str(e)}", exc_info=True)
            raise

    async def send_message(self, message: HL7Message) -> HL7Message:
        """Send HL7 message via MLLP and wait for ACK."""
        try:
            # Wrap message with MLLP markers
            mllp_message = self.mllp_start + message.message_content.encode('utf-8') + self.mllp_end

            # Send via TCP socket
            reader, writer = await asyncio.open_connection(
                settings.MLLP_HOST,
                settings.MLLP_PORT
            )

            try:
                # Send message
                writer.write(mllp_message)
                await writer.drain()
                message.sent_at = datetime.utcnow()

                # Wait for ACK with timeout
                ack_data = await asyncio.wait_for(
                    reader.read(4096),
                    timeout=settings.MLLP_TIMEOUT
                )

                # Parse ACK
                ack_content = ack_data.decode('utf-8').strip(self.mllp_start.decode() + self.mllp_end.decode())
                ack_info = await self.parse_ack(ack_content)

                message.ack_received_at = datetime.utcnow()
                message.ack_status = ack_info.get("status")
                message.ack_message = ack_info.get("message")

                logger.info(f"Message sent and ACK received: {message.ack_status}")

            finally:
                writer.close()
                await writer.wait_closed()

            return message

        except asyncio.TimeoutError:
            logger.error("Timeout waiting for ACK")
            message.ack_status = "TIMEOUT"
            message.ack_message = "No ACK received within timeout period"
            return message

        except Exception as e:
            logger.error(f"Error sending message: {str(e)}", exc_info=True)
            message.ack_status = "ERROR"
            message.ack_message = str(e)
            return message

    async def parse_ack(self, ack_content: str) -> Dict[str, Any]:
        """Parse ACK message and extract status."""
        try:
            ack_msg = parse_message(ack_content)

            # Get acknowledgment code from MSA segment
            msa_segment = ack_msg.msa
            ack_code = str(msa_segment.msa_1.value) if msa_segment.msa_1 else "AR"
            ack_text = str(msa_segment.msa_3.value) if msa_segment.msa_3 else ""

            return {
                "status": ack_code,  # AA=accepted, AE=error, AR=rejected
                "message": ack_text,
                "full_ack": ack_content,
            }

        except Exception as e:
            logger.error(f"Error parsing ACK: {str(e)}", exc_info=True)
            return {
                "status": "PARSE_ERROR",
                "message": f"Could not parse ACK: {str(e)}",
                "full_ack": ack_content,
            }
