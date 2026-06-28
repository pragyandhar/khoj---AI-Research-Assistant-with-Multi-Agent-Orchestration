# WHAT DOES THIS FILE DO: Sets up structured logging with correlation IDs using structlog library.

# ================== IMPORTS ==================
from contextvars import ContextVar
import logging
import structlog

from app.core.config import settings
# ================== IMPORTS ==================


# =========== VARIABLES : Logging Correlation context ===========
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="none")
# =========== VARIABLES : Logging Correlation context ===========


# =========== FUNCTION ===========
# ROLE: Adds correlation ID context variable value to log dict
def add_correlation_id(logger, method_name: str, event_dict: dict) -> dict:
    """ Add correlation ID from ContextVar to the event dict. """
    
    # FLOW-1: Retrieve correlation ID and insert it into log event dict
    event_dict["correlation_id"] = correlation_id_var.get()  # USE: ContextVar correlation_id retrieval
    
    return event_dict
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Sets up structlog configuration based on environment settings.
def setup_logging():
    """ Configure structlog logging processors and output renderers. """
    
    # FLOW-1: Determine which renderer to use based on environment
    if settings.ENVIRONMENT == "production":
        renderer = structlog.processors.JSONRenderer()  # USE: JSON format for production logging
    else:
        renderer = structlog.dev.ConsoleRenderer()      # USE: Colorized terminal format for development
        
    # FLOW-2: Get correct log level object from logging library
    log_level_str = settings.LOG_LEVEL.upper()          # USE: Get configured level name
    log_level = getattr(logging, log_level_str, logging.INFO)  # USE: Resolve to logging level integer
    
    # FLOW-3: Configure structlog with the processor chain
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            add_correlation_id,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            renderer,
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        cache_logger_on_first_use=True,
    )
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Exposes structlog logger instantiation.
def get_logger(name: str):
    """ Returns a named structlog bound logger. """
    
    # FLOW-1: Request a new logger from structlog with the module/component name
    return structlog.get_logger(name)
# =========== FUNCTION ===========