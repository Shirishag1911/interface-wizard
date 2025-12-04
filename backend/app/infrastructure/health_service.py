"""Health check service for Mirth Connect connectivity (URS IR-1)."""
import asyncio
import socket
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass
from loguru import logger

from app.config import settings


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    service: str
    status: str  # "healthy", "degraded", "unhealthy"
    message: str
    response_time_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class HealthCheckService:
    """Service for checking connectivity to external systems (URS IR-1)."""

    def __init__(self):
        self.mllp_start = b'\x0b'
        self.mllp_end = b'\x1c\x0d'

    async def check_mirth_connectivity(self) -> HealthCheckResult:
        """
        Check connectivity to Mirth Connect MLLP endpoint.

        This implements URS IR-1 requirement for real-time status indicators
        of Mirth Connect availability.

        Returns:
            HealthCheckResult with connectivity status
        """
        start_time = datetime.utcnow()

        try:
            # Attempt to connect to Mirth MLLP endpoint
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(
                    settings.MLLP_HOST,
                    settings.MLLP_PORT
                ),
                timeout=5.0  # 5 second timeout for connection
            )

            try:
                # Create a minimal test message (not sent, just connection test)
                test_msg = "MSH|^~\\&|TEST|TEST|TEST|TEST|20250101000000||ACK|TEST|P|2.5"
                mllp_message = self.mllp_start + test_msg.encode('utf-8') + self.mllp_end

                # Send test message
                writer.write(mllp_message)
                await writer.drain()

                # Try to read response with short timeout
                try:
                    response = await asyncio.wait_for(reader.read(1024), timeout=3.0)
                    has_response = len(response) > 0
                except asyncio.TimeoutError:
                    has_response = False

                # Calculate response time
                end_time = datetime.utcnow()
                response_time_ms = (end_time - start_time).total_seconds() * 1000

                # Connection successful
                return HealthCheckResult(
                    service="mirth_connect",
                    status="healthy",
                    message=f"Successfully connected to Mirth Connect at {settings.MLLP_HOST}:{settings.MLLP_PORT}",
                    response_time_ms=response_time_ms,
                    details={
                        "host": settings.MLLP_HOST,
                        "port": settings.MLLP_PORT,
                        "protocol": "MLLP",
                        "response_received": has_response,
                    }
                )

            finally:
                writer.close()
                await writer.wait_closed()

        except asyncio.TimeoutError:
            end_time = datetime.utcnow()
            response_time_ms = (end_time - start_time).total_seconds() * 1000

            return HealthCheckResult(
                service="mirth_connect",
                status="unhealthy",
                message=f"Connection timeout to Mirth Connect at {settings.MLLP_HOST}:{settings.MLLP_PORT}",
                response_time_ms=response_time_ms,
                details={
                    "host": settings.MLLP_HOST,
                    "port": settings.MLLP_PORT,
                    "error": "timeout",
                    "timeout_seconds": 5.0,
                }
            )

        except ConnectionRefusedError:
            end_time = datetime.utcnow()
            response_time_ms = (end_time - start_time).total_seconds() * 1000

            return HealthCheckResult(
                service="mirth_connect",
                status="unhealthy",
                message=f"Connection refused by Mirth Connect at {settings.MLLP_HOST}:{settings.MLLP_PORT}",
                response_time_ms=response_time_ms,
                details={
                    "host": settings.MLLP_HOST,
                    "port": settings.MLLP_PORT,
                    "error": "connection_refused",
                    "hint": "Ensure Mirth Connect is running and the MLLP listener is active",
                }
            )

        except socket.gaierror as e:
            end_time = datetime.utcnow()
            response_time_ms = (end_time - start_time).total_seconds() * 1000

            return HealthCheckResult(
                service="mirth_connect",
                status="unhealthy",
                message=f"Cannot resolve hostname {settings.MLLP_HOST}",
                response_time_ms=response_time_ms,
                details={
                    "host": settings.MLLP_HOST,
                    "port": settings.MLLP_PORT,
                    "error": "dns_resolution_failed",
                    "error_detail": str(e),
                }
            )

        except Exception as e:
            end_time = datetime.utcnow()
            response_time_ms = (end_time - start_time).total_seconds() * 1000

            logger.error(f"Error checking Mirth connectivity: {str(e)}", exc_info=True)

            return HealthCheckResult(
                service="mirth_connect",
                status="unhealthy",
                message=f"Error connecting to Mirth Connect: {str(e)}",
                response_time_ms=response_time_ms,
                details={
                    "host": settings.MLLP_HOST,
                    "port": settings.MLLP_PORT,
                    "error": type(e).__name__,
                    "error_detail": str(e),
                }
            )

    async def check_openemr_connectivity(self) -> HealthCheckResult:
        """
        Check connectivity to OpenEMR FHIR API.

        Returns:
            HealthCheckResult with connectivity status
        """
        start_time = datetime.utcnow()

        try:
            import httpx

            # Check if FHIR endpoint is reachable
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Try metadata endpoint
                response = await client.get(
                    f"{settings.FHIR_BASE_URL}/metadata",
                    headers={"Accept": "application/fhir+json"}
                )

                end_time = datetime.utcnow()
                response_time_ms = (end_time - start_time).total_seconds() * 1000

                if response.status_code == 200:
                    return HealthCheckResult(
                        service="openemr_fhir",
                        status="healthy",
                        message=f"Successfully connected to OpenEMR FHIR API",
                        response_time_ms=response_time_ms,
                        details={
                            "base_url": settings.FHIR_BASE_URL,
                            "status_code": response.status_code,
                        }
                    )
                else:
                    return HealthCheckResult(
                        service="openemr_fhir",
                        status="degraded",
                        message=f"OpenEMR FHIR API responded with status {response.status_code}",
                        response_time_ms=response_time_ms,
                        details={
                            "base_url": settings.FHIR_BASE_URL,
                            "status_code": response.status_code,
                        }
                    )

        except Exception as e:
            end_time = datetime.utcnow()
            response_time_ms = (end_time - start_time).total_seconds() * 1000

            logger.error(f"Error checking OpenEMR connectivity: {str(e)}", exc_info=True)

            return HealthCheckResult(
                service="openemr_fhir",
                status="unhealthy",
                message=f"Error connecting to OpenEMR: {str(e)}",
                response_time_ms=response_time_ms,
                details={
                    "base_url": settings.FHIR_BASE_URL,
                    "error": type(e).__name__,
                    "error_detail": str(e),
                }
            )

    async def check_all_systems(self) -> Dict[str, HealthCheckResult]:
        """
        Check connectivity to all external systems.

        Returns:
            Dictionary mapping service names to health check results
        """
        results = {}

        # Run all health checks concurrently
        mirth_check, openemr_check = await asyncio.gather(
            self.check_mirth_connectivity(),
            self.check_openemr_connectivity(),
            return_exceptions=True
        )

        # Handle results
        if isinstance(mirth_check, HealthCheckResult):
            results["mirth_connect"] = mirth_check
        else:
            results["mirth_connect"] = HealthCheckResult(
                service="mirth_connect",
                status="unhealthy",
                message=f"Health check failed: {str(mirth_check)}",
            )

        if isinstance(openemr_check, HealthCheckResult):
            results["openemr_fhir"] = openemr_check
        else:
            results["openemr_fhir"] = HealthCheckResult(
                service="openemr_fhir",
                status="unhealthy",
                message=f"Health check failed: {str(openemr_check)}",
            )

        return results

    def get_overall_status(self, results: Dict[str, HealthCheckResult]) -> str:
        """
        Determine overall system health from individual checks.

        Args:
            results: Dictionary of health check results

        Returns:
            Overall status: "healthy", "degraded", or "unhealthy"
        """
        statuses = [result.status for result in results.values()]

        if all(status == "healthy" for status in statuses):
            return "healthy"
        elif any(status == "unhealthy" for status in statuses):
            return "unhealthy"
        else:
            return "degraded"
