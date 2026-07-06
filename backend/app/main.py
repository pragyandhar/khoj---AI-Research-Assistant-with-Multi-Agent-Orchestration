# WHAT DOES THIS FILE DO: Bootstraps the FastAPI application, registers middleware, configures global exception handlers, and mounts API routers.

# ================== IMPORTS ==================
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import setup_logging, get_logger
from app.db.base import create_all_tables
from app.graph.checkpointer import setup_checkpointer
from app.graph.main_graph import build_graph
from app.middleware.auth import AuthMiddleware
from app.middleware.logging_middleware import CorrelationIdMiddleware
from app.middleware.token_counter import TokenCounterMiddleware
# ================== IMPORTS ==================


# =========== VARIABLES : Main Application Loggers ===========
logger = get_logger(__name__)               # USE: Root application setup logger instance
# =========== VARIABLES : Main Application Loggers ===========


# =========== FUNCTION ===========
# ROLE: Lifespan context manager handling application startup and shutdown events.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Startup and shutdown event pipeline for health and resources setup. """
    
    # FLOW-1: Initialize configurations, DDL generation, and log application start
    setup_logging()                             # USE: Setup structured logger processors
    await create_all_tables()                   # USE: Generate database schemas if not exist
    
    # FLOW-2: Initialize checkpointer and graph in application state
    app.state.checkpointer = await setup_checkpointer()  # USE: Setup PG checkpointer
    app.state.graph = build_graph(app.state.checkpointer)  # USE: Compile and store graph
    
    logger.info("application_started", environment=settings.ENVIRONMENT)  # USE: Startup audit log
    
    yield
# =========== FUNCTION ===========


# =========== VARIABLES : FastAPI Application Setup ===========
app = FastAPI(
    title="AI Research Assistant",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)                                               # USE: Instantiate FastAPI app core

# FLOW-1: Configure Latency tracking middleware first
app.add_middleware(TokenCounterMiddleware)      # USE: Add latency wrapper first

# FLOW-2: Configure Correlation ID tracing middleware second
app.add_middleware(CorrelationIdMiddleware)     # USE: Add request tracing middleware

# FLOW-3: Configure Auth middleware for securing endpoints
app.add_middleware(AuthMiddleware)              # USE: Add request authentication middleware

# FLOW-4: Configure CORS middleware policies
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,        # USE: Allowed origins list from settings
    allow_credentials=True,                     # USE: Allow cookies/auth headers in requests
    allow_methods=["*"],                        # USE: Allow all HTTP verbs
    allow_headers=["*"],                        # USE: Allow all request headers
)

# FLOW-5: Register router endpoints under /api/v1 path prefix
app.include_router(api_router, prefix="/api/v1")  # USE: Include the main API router
# =========== VARIABLES : FastAPI Application Setup ===========


# =========== FUNCTION ===========
# ROLE: Global exception handler for custom AppException classes.
@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    """ Returns standard error format responses for known app errors. """
    
    # FLOW-1: Return structured JSON response using code and message from exception
    return JSONResponse(
        status_code=exc.status_code,            # USE: Status code defined in custom exception
        content={"error_code": exc.error_code, "message": exc.message}  # USE: Serialized error details
    )
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Fallback exception handler for unhandled generic Exception classes.
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc: Exception):
    """ Catch all handler logging actual trace and returning safe messages. """
    
    # FLOW-1: Log actual raw error details securely
    logger.error("unhandled_exception", error=str(exc))  # USE: Write error traceback to logs
    message = "Internal Server Error"           # USE: Safe fallback error message
    
    # FLOW-2: Expose raw details only when running in non-production environments
    if settings.ENVIRONMENT != "production":
        message = str(exc)                      # USE: Detail error message for development debugging
        
    return JSONResponse(
        status_code=500,                        # USE: Generic internal server error status
        content={"error_code": "INTERNAL_SERVER_ERROR", "message": message}  # USE: Payload dict response
    )
# =========== FUNCTION ===========