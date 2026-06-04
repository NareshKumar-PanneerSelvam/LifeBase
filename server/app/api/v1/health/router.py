from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from app.core.database import get_db_session
from app.schemas.response import APIResponse

logger = structlog.get_logger()
router = APIRouter()

@router.get("", response_model=APIResponse[dict])
async def check_health(db: AsyncSession = Depends(get_db_session)) -> APIResponse[dict]:
    """Health check endpoint checking application uptime and querying database connectivity."""
    try:
        # Dynamic verification of database session
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
        success = True
        status_msg = "healthy"
    except Exception as exc:
        logger.error("Health check database ping failed", error=str(exc))
        db_status = "unhealthy"
        success = False
        status_msg = "degraded"

    return APIResponse(
        success=success,
        data={
            "status": status_msg,
            "database": db_status,
            "version": "1.0.0",
        },
        error=None,
    )
