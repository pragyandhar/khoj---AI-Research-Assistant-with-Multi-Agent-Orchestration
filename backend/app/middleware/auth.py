# WHAT DOES THIS FILE DO: Defines the AuthMiddleware to validate API keys on incoming HTTP requests.

# ================== IMPORTS ==================
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.config import settings
# ================== IMPORTS ==================


# =========== VARIABLES : Auth Middleware Constants ===========
EXEMPT_PATHS = ["/api/v1/health", "/api/v1/ready", "/api/docs", "/api/redoc", "/openapi.json"]  # USE: Routes that bypass authentication checks
# =========== VARIABLES : Auth Middleware Constants ===========


# =========== CLASS ===========
# ROLE: Middleware validating API keys on all non-exempt incoming requests.
class AuthMiddleware(BaseHTTPMiddleware):
    """ Middleware enforcing API key authentication controls. """


    # =========== FUNCTION ===========
    # ROLE: Intercept requests to check and validate API authorization headers.
    async def dispatch(self, request: Request, call_next):
        """ Checks incoming request paths and validates Authorization headers. """
        
        # FLOW-1: Skip authentication check for exempt paths
        if request.url.path in EXEMPT_PATHS:
            response = await call_next(request)  # USE: Direct propagation of exempt requests
            
            return response
            
        # FLOW-2: Validate existence of Authorization header
        auth_header = request.headers.get("Authorization")  # USE: Get auth header string
        
        if not auth_header:
            return JSONResponse(
                status_code=401,                # USE: Unauthorized HTTP status code
                content={"error_code": "MISSING_AUTH", "message": "Authorization header required"}  # USE: Missing error details
            )
            
        # FLOW-3: Extract bearer token or raw API key from header
        api_key = auth_header
        
        if auth_header.startswith("Bearer "):
            api_key = auth_header[7:]           # USE: Parse out the bearer token prefix
            
        # FLOW-4: Compare with configured secret key and raise 403 on mismatch
        if api_key != settings.API_SECRET_KEY:
            return JSONResponse(
                status_code=403,                # USE: Forbidden HTTP status code
                content={"error_code": "INVALID_API_KEY", "message": "Invalid API key"}  # USE: Invalid credentials error payload
            )
            
        # FLOW-5: Propagate authenticated request to next handler
        response = await call_next(request)     # USE: Forward valid request to router
        
        return response
    # =========== FUNCTION ===========
# =========== CLASS ===========