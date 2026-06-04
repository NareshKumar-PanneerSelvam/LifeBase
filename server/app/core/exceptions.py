from typing import Any, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import structlog

logger = structlog.get_logger()

class AppException(Exception):
    """Base application exception that generates a structured API error response."""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_SERVER_ERROR"
        self.details = details

class BadRequestException(AppException):
    """400 Bad Request exception."""
    def __init__(self, message: str, error_code: str = "BAD_REQUEST", details: Optional[Any] = None) -> None:
        super().__init__(message, status.HTTP_400_BAD_REQUEST, error_code, details)

class AuthenticationException(AppException):
    """401 Unauthorized exception."""
    def __init__(self, message: str, error_code: str = "UNAUTHORIZED", details: Optional[Any] = None) -> None:
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, error_code, details)

class ForbiddenException(AppException):
    """403 Forbidden exception."""
    def __init__(self, message: str, error_code: str = "FORBIDDEN", details: Optional[Any] = None) -> None:
        super().__init__(message, status.HTTP_403_FORBIDDEN, error_code, details)

class NotFoundException(AppException):
    """404 Not Found exception."""
    def __init__(self, message: str, error_code: str = "NOT_FOUND", details: Optional[Any] = None) -> None:
        super().__init__(message, status.HTTP_404_NOT_FOUND, error_code, details)

def register_exception_handlers(app: FastAPI) -> None:
    """Binds exception handlers to the FastAPI app instance."""
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.warning(
            "Application exception occurred",
            path=request.url.path,
            error_code=exc.error_code,
            message=exc.message,
            status_code=exc.status_code,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                },
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = []
        for error in exc.errors():
            details.append({
                "loc": [str(loc) for loc in error["loc"]],
                "msg": error["msg"],
                "type": error["type"],
            })
        
        logger.warning(
            "Request validation failed",
            path=request.url.path,
            errors=details,
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Validation failed for the request parameters or body.",
                    "details": details,
                },
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "Unhandled server error occurred",
            path=request.url.path,
            error_type=type(exc).__name__,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred. Please try again later.",
                    "details": None,
                },
            },
        )
