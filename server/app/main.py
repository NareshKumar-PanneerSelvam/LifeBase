from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.middleware.logging import LoggingMiddleware
from app.api.v1.auth.router import router as auth_router
from app.api.v1.users.router import router as users_router
from app.api.v1.health.router import router as health_router
import structlog

# Set up logging structure early in the loading process
setup_logging()
logger = structlog.get_logger("app.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event manager covering application bootstrap and cleanup phases."""
    logger.info("Initializing LifeBase FastAPI Server...", app_name=settings.APP_NAME)
    yield
    logger.info("Terminating LifeBase FastAPI Server session...")

app = FastAPI(
    title=settings.APP_NAME,
    description="Production-grade FastAPI modular monolith backend for LifeBase",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Centralized error and validation handlers mapping
register_exception_handlers(app)

# Structured request/response logging middleware
app.add_middleware(LoggingMiddleware)

# Cross-Origin Resource Sharing (CORS) setup
if settings.BACKEND_CORS_ORIGINS:
    origins = [str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS]
    logger.info("Mounting CORS Middleware", allowed_origins=origins)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Routing mappings
app.include_router(health_router, prefix=f"{settings.API_V1_STR}/health", tags=["Health"])
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(users_router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
