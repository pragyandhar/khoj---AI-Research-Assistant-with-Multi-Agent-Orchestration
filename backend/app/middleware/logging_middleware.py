# WHAT DOES THIS FILE DO: Defines the CorrelationIdMiddleware to track request-level logging correlation IDs.

# ================== IMPORTS ==================
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import structlog

from app.core.logging import correlation_id_var
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Middleware to inject and track a unique correlation ID per request.
class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """ Middleware generating or forwarding request tracing correlation IDs. """


    # =========== FUNCTION ===========
    # ROLE: Intercept HTTP requests to bind correlation IDs and add tracing response headers.
    async def dispatch(self, request: Request, call_next):
        """ Generates and propagates correlation ID throughout request lifecycle. """
        
        # FLOW-1: Check request headers for existing ID, fallback to generating new UUID
        correlation_id = request.headers.get("X-Correlation-ID")  # USE: Extract correlation ID header
        
        if not correlation_id:
            correlation_id = str(uuid.uuid4())  # USE: Generate tracing UUID string if missing
            
        # FLOW-2: Bind correlation ID context variables for logging
        token = correlation_id_var.set(correlation_id)  # USE: Bind context var for custom logs processor
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)  # USE: Bind structlog context
        
        # FLOW-3: Proceed with request execution and append correlation ID to response headers
        try:
            response = await call_next(request)  # USE: Call next request pipeline handler
            response.headers["X-Correlation-ID"] = correlation_id  # USE: Append trace ID to output headers
            
            return response
            
        finally:
            # FLOW-4: Clear context variables to reset slate for subsequent requests
            structlog.contextvars.clear_contextvars()  # USE: Reset structlog context
            correlation_id_var.reset(token)    # USE: Reset contextvar token
    # =========== FUNCTION ===========
# =========== CLASS ===========