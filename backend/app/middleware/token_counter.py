# WHAT DOES THIS FILE DO: Defines the TokenCounterMiddleware to monitor and log request latency metrics.

# ================== IMPORTS ==================
import time

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

from app.core.logging import get_logger
# ================== IMPORTS ==================


# =========== VARIABLES : Latency monitoring loggers ===========
logger = get_logger(__name__)               # USE: Setup service latency tracker logger instance
# =========== VARIABLES : Latency monitoring loggers ===========


# =========== CLASS ===========
# ROLE: Middleware tracking total API request latency duration.
class TokenCounterMiddleware(BaseHTTPMiddleware):
    """ Outermost middleware designed to measure request response time latency. """


    # =========== FUNCTION ===========
    # ROLE: Calculate total processing time for requests and insert timing headers.
    async def dispatch(self, request: Request, call_next):
        """ Wraps request processing to record duration and latency logs. """
        
        # FLOW-1: Record start timestamp
        start_time = time.time()                # USE: Record system start time float
        
        # FLOW-2: Execute downstream middleware and router pipeline
        response = await call_next(request)     # USE: Run request through next middleware
        
        # FLOW-3: Compute request duration in milliseconds
        duration_ms = (time.time() - start_time) * 1000  # USE: Convert duration delta to milliseconds
        
        # FLOW-4: Append response time header and log metric details
        response.headers["X-Response-Time-Ms"] = str(round(duration_ms, 2))  # USE: Inject header payload
        correlation_id = response.headers.get("X-Correlation-ID", "none")  # USE: Extract correlation ID for trace alignment
        
        logger.info(
            "request_completed",
            path=request.url.path,
            method=request.method,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
            correlation_id=correlation_id
        )                                       # USE: Write Grafana/dashboard latency log
        
        return response
    # =========== FUNCTION ===========
# =========== CLASS ===========