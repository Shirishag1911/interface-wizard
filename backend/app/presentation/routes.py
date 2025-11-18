"""API routes for Interface Wizard."""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from loguru import logger

from app.config import settings
from app.application.use_cases import ProcessCommandUseCase
from app.presentation.dependencies import (
    get_process_command_use_case,
    get_context_repository,
    get_operation_repository,
    get_csv_service,
)
from app.presentation.schemas import (
    CommandRequest,
    OperationResponse,
    HealthResponse,
    SessionResponse,
    ErrorResponse,
    CSVUploadResponse,
)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow(),
    )


@router.post("/command", response_model=OperationResponse)
async def process_command(
    command: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    use_case: ProcessCommandUseCase = Depends(get_process_command_use_case),
    csv_service = Depends(get_csv_service),
):
    """
    Process a natural language command with optional CSV file upload.

    This is the main endpoint where users submit their commands.
    The system will interpret the command, execute the appropriate action,
    and return the result.

    If a CSV file is provided, it will be processed and patients will be created from the CSV data.
    """
    # Log incoming request details for debugging
    logger.info("=" * 80)
    logger.info("INCOMING REQUEST to /command endpoint")
    logger.info(f"  Command: {command!r}")
    logger.info(f"  Session ID: {session_id!r}")
    logger.info(f"  File: {file.filename if file else None}")
    logger.info(f"  Content Type: {file.content_type if file else None}")
    logger.info("=" * 80)

    try:
        # Ensure command has a value, even if not provided
        if not command:
            command = ""
            logger.warning("Command is empty, using empty string")

        logger.info(f"Processing command: {command} (session: {session_id}, file: {file.filename if file else None})")

        # Handle file upload (CSV, Excel, PDF)
        csv_patients = None
        if file and file.filename:
            file_ext = file.filename.lower().split('.')[-1]
            logger.info(f"Processing {file_ext.upper()} file: {file.filename}")

            try:
                # Read file content
                file_content = await file.read()

                # Parse based on file type
                if file_ext == 'csv':
                    csv_patients = csv_service.parse_csv(file_content)
                elif file_ext in ['xlsx', 'xls']:
                    csv_patients = csv_service.parse_excel(file_content, file_ext)
                elif file_ext == 'pdf':
                    csv_patients = csv_service.parse_pdf(file_content)
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Unsupported file type: .{file_ext}. Supported types: CSV, Excel (.xlsx, .xls), PDF",
                    )

                logger.info(f"Parsed {len(csv_patients)} patients from {file_ext.upper()} file")

                # Override command to indicate bulk patient creation
                if not command.strip():
                    command = f"Create {len(csv_patients)} patients from uploaded {file_ext.upper()} file"

            except ValueError as ve:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid {file_ext.upper()} file: {str(ve)}",
                )
            except Exception as e:
                logger.error(f"Error processing {file_ext.upper()} file: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to process {file_ext.upper()} file: {str(e)}",
                )

        result = await use_case.execute(
            raw_command=command,
            session_id=session_id,
            csv_patients=csv_patients,
        )

        return OperationResponse(
            operation_id=result.operation_id,
            status=result.status.value,
            message=result.message,
            data=result.data,
            errors=result.errors,
            warnings=result.warnings,
            protocol_used=result.protocol_used.value if result.protocol_used else None,
            records_affected=result.records_affected,
            records_succeeded=result.records_succeeded,
            records_failed=result.records_failed,
            created_at=result.created_at,
            completed_at=result.completed_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing command: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your command: {str(e)}",
        )


@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    context_repo = Depends(get_context_repository),
):
    """Get session information."""
    try:
        context = await context_repo.get_context(session_id)

        if not context:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found",
            )

        return SessionResponse(
            session_id=context.session_id,
            created_at=context.created_at,
            last_activity=context.last_activity,
            command_count=len(context.command_history),
            operation_count=len(context.operation_history),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/operation/{operation_id}", response_model=OperationResponse)
async def get_operation(
    operation_id: str,
    operation_repo = Depends(get_operation_repository),
):
    """Get operation details by ID."""
    try:
        operation = await operation_repo.get_operation(operation_id)

        if not operation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Operation {operation_id} not found",
            )

        return OperationResponse(
            operation_id=operation.operation_id,
            status=operation.status.value,
            message=operation.message,
            data=operation.data,
            errors=operation.errors,
            warnings=operation.warnings,
            protocol_used=operation.protocol_used.value if operation.protocol_used else None,
            records_affected=operation.records_affected,
            records_succeeded=operation.records_succeeded,
            records_failed=operation.records_failed,
            created_at=operation.created_at,
            completed_at=operation.completed_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting operation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
