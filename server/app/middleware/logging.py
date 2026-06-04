import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger("app.middleware.logging")

class LoggingMiddleware(BaseHTTPMiddleware):
    """Custom HTTP middleware capturing and logging structural metadata about API requests."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        
        logger.debug(
            "HTTP Request initiated",
            method=method,
            path=path,
            client_ip=client_ip,
        )
        
        try:
            response = await call_next(request)
            process_time = time.perf_counter() - start_time
            duration_ms = round(process_time * 1000, 2)
            
            logger.info(
                "HTTP Request completed",
                method=method,
                path=path,
                client_ip=client_ip,
                status_code=response.status_code,
                duration_ms=duration_ms,
            )
            return response
        except Exception as exc:
            process_time = time.perf_counter() - start_time
            duration_ms = round(process_time * 1000, 2)
            
            logger.exception(
                "HTTP Request crashed",
                method=method,
                path=path,
                client_ip=client_ip,
                duration_ms=duration_ms,
                error=str(exc),
            )
            raise exc
