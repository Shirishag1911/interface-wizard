"""API routes for Interface Wizard."""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from app.config import settings
from app.application.use_cases import ProcessCommandUseCase
from app.presentation.dependencies import (
    get_process_command_use_case,
    get_context_repository,
    get_operation_repository,
)
from app.presentation.schemas import (
    CommandRequest,
    OperationResponse,
    HealthResponse,
    SessionResponse,
    ErrorResponse,
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
    request: CommandRequest,
    use_case: ProcessCommandUseCase = Depends(get_process_command_use_case),
):
    """
    Process a natural language command.

    This is the main endpoint where users submit their commands.
    The system will interpret the command, execute the appropriate action,
    and return the result.
    """
    try:
        logger.info(f"Processing command: {request.command} (session: {request.session_id})")

        result = await use_case.execute(
            raw_command=request.command,
            session_id=request.session_id,
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
