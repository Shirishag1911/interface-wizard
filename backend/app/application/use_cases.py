"""Use cases - Application business logic."""
from typing import Optional, List
from datetime import datetime
from loguru import logger

from app.domain.entities import (
    UserCommand,
    OperationResult,
    OperationStatus,
    CommandType,
    Protocol,
    ConversationContext,
    Patient,
)
from app.domain.interfaces import (
    INLPService,
    IHL7Service,
    IFHIRService,
    IDataGeneratorService,
    IOperationRepository,
    IContextRepository,
    IMessageRepository,
)


class ProcessCommandUseCase:
    """Use case for processing natural language commands."""

    def __init__(
        self,
        nlp_service: INLPService,
        hl7_service: IHL7Service,
        fhir_service: IFHIRService,
        data_generator: IDataGeneratorService,
        operation_repo: IOperationRepository,
        context_repo: IContextRepository,
        message_repo: IMessageRepository,
    ):
        self.nlp_service = nlp_service
        self.hl7_service = hl7_service
        self.fhir_service = fhir_service
        self.data_generator = data_generator
        self.operation_repo = operation_repo
        self.context_repo = context_repo
        self.message_repo = message_repo

    async def execute(
        self,
        raw_command: str,
        session_id: Optional[str] = None,
        csv_patients: Optional[List[Patient]] = None
    ) -> OperationResult:
        """
        Execute the command processing use case.

        Args:
            raw_command: Natural language command from user
            session_id: Optional session ID for context
            csv_patients: Optional list of patients parsed from CSV file

        Returns:
            OperationResult with execution status and details
        """
        try:
            # Load or create conversation context
            context = None
            if session_id:
                context = await self.context_repo.get_context(session_id)
            if not context:
                context = ConversationContext(session_id=session_id or "")

            # Handle CSV upload directly without NLP interpretation
            if csv_patients:
                logger.info(f"Processing {len(csv_patients)} patients from CSV upload")
                result = await self._handle_csv_upload(csv_patients, raw_command)

                # Save context and operation result
                context.add_operation_result(result)
                await self.context_repo.save_context(context)
                await self.operation_repo.save_operation(result)

                return result

            # Interpret the command using NLP
            logger.info(f"Interpreting command: {raw_command}")
            user_command = await self.nlp_service.interpret_command(raw_command, context)
            context.add_command(user_command)

            # Route to appropriate handler based on command type
            result = await self._route_command(user_command, context)

            # Save context and operation result
            context.add_operation_result(result)
            await self.context_repo.save_context(context)
            await self.operation_repo.save_operation(result)

            # Generate human-friendly response
            result.message = await self.nlp_service.generate_response(result, context)

            return result

        except Exception as e:
            logger.error(f"Error processing command: {str(e)}", exc_info=True)
            return OperationResult(
                command_id=raw_command[:50],
                status=OperationStatus.FAILED,
                message=f"An error occurred while processing your command: {str(e)}",
                errors=[str(e)],
            )

    async def _route_command(self, command: UserCommand, context: ConversationContext) -> OperationResult:
        """Route command to appropriate handler."""
        handlers = {
            CommandType.CREATE_PATIENT: self._handle_create_patient,
            CommandType.CREATE_BULK: self._handle_create_bulk,
            CommandType.RETRIEVE_PATIENT: self._handle_retrieve_patient,
            CommandType.RETRIEVE_LAB_RESULT: self._handle_retrieve_lab_result,
            CommandType.ADMIT_PATIENT: self._handle_admit_patient,
            CommandType.DISCHARGE_PATIENT: self._handle_discharge_patient,
        }

        handler = handlers.get(command.command_type)
        if handler:
            return await handler(command, context)
        else:
            return OperationResult(
                command_id=command.command_id,
                status=OperationStatus.FAILED,
                message="I couldn't understand that command. Could you please rephrase it?",
                errors=["Unknown command type"],
            )

    async def _handle_create_patient(self, command: UserCommand, context: ConversationContext) -> OperationResult:
        """Handle creating a single patient."""
        try:
            # Generate patient data if not fully specified
            patient = self.data_generator.generate_patient(command.parameters)

            # Use HL7 to create patient
            hl7_message = await self.hl7_service.create_patient_message(patient)
            sent_message = await self.hl7_service.send_message(hl7_message)

            # Save message
            await self.message_repo.save_message(sent_message)

            # Check ACK status
            if sent_message.ack_status == "AA":
                return OperationResult(
                    command_id=command.command_id,
                    status=OperationStatus.SUCCESS,
                    message=f"Successfully created patient: {patient.first_name} {patient.last_name}",
                    data=patient.to_dict(),
                    protocol_used=Protocol.HL7V2,
                    records_affected=1,
                    records_succeeded=1,
                    completed_at=datetime.utcnow(),
                )
            else:
                return OperationResult(
                    command_id=command.command_id,
                    status=OperationStatus.FAILED,
                    message="Failed to create patient",
                    errors=[sent_message.ack_message or "Unknown error"],
                    protocol_used=Protocol.HL7V2,
                    records_affected=1,
                    records_failed=1,
                    completed_at=datetime.utcnow(),
                )

        except Exception as e:
            logger.error(f"Error creating patient: {str(e)}", exc_info=True)
            return OperationResult(
                command_id=command.command_id,
                status=OperationStatus.FAILED,
                message="Failed to create patient",
                errors=[str(e)],
                protocol_used=Protocol.HL7V2,
                records_affected=1,
                records_failed=1,
                completed_at=datetime.utcnow(),
            )

    async def _handle_create_bulk(self, command: UserCommand, context: ConversationContext) -> OperationResult:
        """Handle bulk patient creation."""
        try:
            count = command.parameters.get("count", 1)
            patients = self.data_generator.generate_patients(count, command.parameters)

            succeeded = 0
            failed = 0
            errors = []

            for patient in patients:
                try:
                    hl7_message = await self.hl7_service.create_patient_message(patient)
                    sent_message = await self.hl7_service.send_message(hl7_message)
                    await self.message_repo.save_message(sent_message)

                    if sent_message.ack_status == "AA":
                        succeeded += 1
                    else:
                        failed += 1
                        errors.append(f"Patient {patient.first_name} {patient.last_name}: {sent_message.ack_message}")
                except Exception as e:
                    failed += 1
                    errors.append(f"Patient {patient.first_name} {patient.last_name}: {str(e)}")

            status = OperationStatus.SUCCESS if failed == 0 else (
                OperationStatus.PARTIAL_SUCCESS if succeeded > 0 else OperationStatus.FAILED
            )

            return OperationResult(
                command_id=command.command_id,
                status=status,
                message=f"Bulk operation completed: {succeeded} succeeded, {failed} failed",
                protocol_used=Protocol.HL7V2,
                records_affected=count,
                records_succeeded=succeeded,
                records_failed=failed,
                errors=errors[:10],  # Limit errors shown
                completed_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Error in bulk creation: {str(e)}", exc_info=True)
            return OperationResult(
                command_id=command.command_id,
                status=OperationStatus.FAILED,
                message="Failed to complete bulk operation",
                errors=[str(e)],
                protocol_used=Protocol.HL7V2,
                completed_at=datetime.utcnow(),
            )

    async def _handle_retrieve_patient(self, command: UserCommand, context: ConversationContext) -> OperationResult:
        """Handle patient retrieval."""
        try:
            patient_id = command.parameters.get("patient_id")
            mrn = command.parameters.get("mrn")

            if patient_id:
                patient = await self.fhir_service.get_patient(patient_id)
            elif mrn:
                patients = await self.fhir_service.search_patients({"identifier": mrn})
                patient = patients[0] if patients else None
            else:
                return OperationResult(
                    command_id=command.command_id,
                    status=OperationStatus.FAILED,
                    message="Please provide either a patient ID or MRN to retrieve patient information",
                    errors=["Missing patient identifier"],
                )

            if patient:
                return OperationResult(
                    command_id=command.command_id,
                    status=OperationStatus.SUCCESS,
                    message=f"Found patient: {patient.first_name} {patient.last_name}",
                    data=patient.to_dict(),
                    protocol_used=Protocol.FHIR,
                    records_affected=1,
                    records_succeeded=1,
                    completed_at=datetime.utcnow(),
                )
            else:
                return OperationResult(
                    command_id=command.command_id,
                    status=OperationStatus.FAILED,
                    message="Patient not found",
                    protocol_used=Protocol.FHIR,
                    records_affected=0,
                    completed_at=datetime.utcnow(),
                )

        except Exception as e:
            logger.error(f"Error retrieving patient: {str(e)}", exc_info=True)
            return OperationResult(
                command_id=command.command_id,
                status=OperationStatus.FAILED,
                message="Failed to retrieve patient",
                errors=[str(e)],
                protocol_used=Protocol.FHIR,
                completed_at=datetime.utcnow(),
            )

    async def _handle_retrieve_lab_result(self, command: UserCommand, context: ConversationContext) -> OperationResult:
        """Handle lab result retrieval."""
        try:
            patient_id = command.parameters.get("patient_id")
            test_type = command.parameters.get("test_type")

            if not patient_id:
                return OperationResult(
                    command_id=command.command_id,
                    status=OperationStatus.FAILED,
                    message="Please provide a patient ID to retrieve lab results",
                    errors=["Missing patient_id"],
                )

            params = {}
            if test_type:
                params["code"] = test_type

            lab_results = await self.fhir_service.get_observations(patient_id, params)

            if lab_results:
                return OperationResult(
                    command_id=command.command_id,
                    status=OperationStatus.SUCCESS,
                    message=f"Found {len(lab_results)} lab result(s)",
                    data={"lab_results": [vars(lr) for lr in lab_results]},
                    protocol_used=Protocol.FHIR,
                    records_affected=len(lab_results),
                    records_succeeded=len(lab_results),
                    completed_at=datetime.utcnow(),
                )
            else:
                return OperationResult(
                    command_id=command.command_id,
                    status=OperationStatus.SUCCESS,
                    message="No lab results found for this patient",
                    protocol_used=Protocol.FHIR,
                    records_affected=0,
                    completed_at=datetime.utcnow(),
                )

        except Exception as e:
            logger.error(f"Error retrieving lab results: {str(e)}", exc_info=True)
            return OperationResult(
                command_id=command.command_id,
                status=OperationStatus.FAILED,
                message="Failed to retrieve lab results",
                errors=[str(e)],
                protocol_used=Protocol.FHIR,
                completed_at=datetime.utcnow(),
            )

    async def _handle_admit_patient(self, command: UserCommand, context: ConversationContext) -> OperationResult:
        """Handle patient admission."""
        try:
            patient_id = command.parameters.get("patient_id")
            # In real scenario, we'd first retrieve the patient
            patient = Patient(patient_id=patient_id)

            admission_data = {
                "admission_datetime": command.parameters.get("admission_datetime", datetime.utcnow()),
                "location": command.parameters.get("location", "General Ward"),
                "attending_doctor": command.parameters.get("attending_doctor", "Dr. Smith"),
            }

            hl7_message = await self.hl7_service.create_admit_message(patient, admission_data)
            sent_message = await self.hl7_service.send_message(hl7_message)
            await self.message_repo.save_message(sent_message)

            if sent_message.ack_status == "AA":
                return OperationResult(
                    command_id=command.command_id,
                    status=OperationStatus.SUCCESS,
                    message="Patient admitted successfully",
                    protocol_used=Protocol.HL7V2,
                    records_affected=1,
                    records_succeeded=1,
                    completed_at=datetime.utcnow(),
                )
            else:
                return OperationResult(
                    command_id=command.command_id,
                    status=OperationStatus.FAILED,
                    message="Failed to admit patient",
                    errors=[sent_message.ack_message or "Unknown error"],
                    protocol_used=Protocol.HL7V2,
                    records_failed=1,
                    completed_at=datetime.utcnow(),
                )

        except Exception as e:
            logger.error(f"Error admitting patient: {str(e)}", exc_info=True)
            return OperationResult(
                command_id=command.command_id,
                status=OperationStatus.FAILED,
                message="Failed to admit patient",
                errors=[str(e)],
                protocol_used=Protocol.HL7V2,
                completed_at=datetime.utcnow(),
            )

    async def _handle_discharge_patient(self, command: UserCommand, context: ConversationContext) -> OperationResult:
        """Handle patient discharge."""
        try:
            patient_id = command.parameters.get("patient_id")
            patient = Patient(patient_id=patient_id)

            discharge_data = {
                "discharge_datetime": command.parameters.get("discharge_datetime", datetime.utcnow()),
                "discharge_disposition": command.parameters.get("discharge_disposition", "Home"),
            }

            hl7_message = await self.hl7_service.create_discharge_message(patient, discharge_data)
            sent_message = await self.hl7_service.send_message(hl7_message)
            await self.message_repo.save_message(sent_message)

            if sent_message.ack_status == "AA":
                return OperationResult(
                    command_id=command.command_id,
                    status=OperationStatus.SUCCESS,
                    message="Patient discharged successfully",
                    protocol_used=Protocol.HL7V2,
                    records_affected=1,
                    records_succeeded=1,
                    completed_at=datetime.utcnow(),
                )
            else:
                return OperationResult(
                    command_id=command.command_id,
                    status=OperationStatus.FAILED,
                    message="Failed to discharge patient",
                    errors=[sent_message.ack_message or "Unknown error"],
                    protocol_used=Protocol.HL7V2,
                    records_failed=1,
                    completed_at=datetime.utcnow(),
                )

        except Exception as e:
            logger.error(f"Error discharging patient: {str(e)}", exc_info=True)
            return OperationResult(
                command_id=command.command_id,
                status=OperationStatus.FAILED,
                message="Failed to discharge patient",
                errors=[str(e)],
                protocol_used=Protocol.HL7V2,
                completed_at=datetime.utcnow(),
            )

    async def _handle_csv_upload(self, patients: List[Patient], raw_command: str) -> OperationResult:
        """Handle bulk patient creation from CSV upload."""
        try:
            total_count = len(patients)
            succeeded = 0
            failed = 0
            errors = []
            warnings = []
            patient_details = []  # Store first 5 successful patients for summary

            logger.info(f"Processing {total_count} patients from CSV upload")

            for index, patient in enumerate(patients, start=1):
                try:
                    # Generate MRN if not provided
                    if not patient.mrn:
                        import uuid
                        patient.mrn = f"CSV{uuid.uuid4().hex[:8].upper()}"

                    # Create HL7 message for patient
                    hl7_message = await self.hl7_service.create_patient_message(patient)
                    sent_message = await self.hl7_service.send_message(hl7_message)
                    await self.message_repo.save_message(sent_message)

                    # Check ACK status
                    if sent_message.ack_status == "AA":
                        succeeded += 1
                        logger.debug(f"Successfully created patient {index}/{total_count}: {patient.first_name} {patient.last_name}")

                        # Store first 5 successful patients for detailed summary
                        if len(patient_details) < 5:
                            patient_details.append({
                                "name": f"{patient.first_name} {patient.last_name}",
                                "mrn": patient.mrn,
                                "dob": str(patient.date_of_birth) if patient.date_of_birth else "N/A",
                                "gender": patient.gender or "N/A",
                                "diagnosis": patient.metadata.get("primary_diagnosis") or patient.metadata.get("scenario") or "General Care",
                                "allergies": ", ".join(patient.allergies) if patient.allergies else "None"
                            })
                    else:
                        failed += 1
                        error_msg = f"Row {patient.metadata.get('csv_row', index)}: {patient.first_name} {patient.last_name} - {sent_message.ack_message}"
                        errors.append(error_msg)
                        logger.warning(error_msg)

                except Exception as e:
                    failed += 1
                    error_msg = f"Row {patient.metadata.get('csv_row', index)}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(f"Error creating patient {index}/{total_count}: {str(e)}")

            # Determine overall status and create detailed message
            if failed == 0:
                status = OperationStatus.SUCCESS
                summary = f"Successfully processed and added all {succeeded} patients to the system! 🎉"
            elif succeeded == 0:
                status = OperationStatus.FAILED
                summary = f"Unfortunately, all {total_count} patient records failed to process. Please check the CSV format."
            else:
                status = OperationStatus.PARTIAL_SUCCESS
                summary = f"Processed {succeeded} out of {total_count} patients successfully. {failed} records encountered issues."

            # Build detailed message with patient preview
            if patient_details:
                message_parts = [summary, "\n\n**Patient Records Created:**\n"]
                for idx, p in enumerate(patient_details, 1):
                    message_parts.append(f"\n{idx}. **{p['name']}** (MRN: {p['mrn']})")
                    message_parts.append(f"   - Date of Birth: {p['dob']}")
                    message_parts.append(f"   - Gender: {p['gender']}")
                    message_parts.append(f"   - Diagnosis/Condition: {p['diagnosis']}")
                    message_parts.append(f"   - Allergies: {p['allergies']}")

                if succeeded > 5:
                    message_parts.append(f"\n\n...and {succeeded - 5} more patients successfully created.")

                message = "".join(message_parts)
            else:
                message = summary

            return OperationResult(
                command_id=raw_command[:50],
                status=status,
                message=message,
                data={
                    "total_patients": total_count,
                    "successful": succeeded,
                    "failed": failed,
                    "source": "csv_upload",
                    "patient_preview": patient_details
                },
                errors=errors[:10],  # Limit to first 10 errors
                warnings=warnings,
                protocol_used=Protocol.HL7V2,
                records_affected=total_count,
                records_succeeded=succeeded,
                records_failed=failed,
                completed_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Error processing CSV upload: {str(e)}", exc_info=True)
            return OperationResult(
                command_id=raw_command[:50],
                status=OperationStatus.FAILED,
                message=f"Failed to process CSV upload: {str(e)}",
                errors=[str(e)],
                protocol_used=Protocol.HL7V2,
                records_affected=len(patients) if patients else 0,
                records_failed=len(patients) if patients else 0,
                completed_at=datetime.utcnow(),
            )
