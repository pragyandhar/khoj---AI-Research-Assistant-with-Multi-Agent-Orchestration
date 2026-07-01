# WHAT DOES THIS FILE DO: Defines FastAPI liveness and readiness health check endpoints.

# ================== IMPORTS ==================
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.core.dependencies import DBSession, Cache
# ================== IMPORTS ==================


# =========== VARIABLES : API Router Configuration ===========
router = APIRouter(tags=["health"])             # USE: Router instance for health checks
# =========== VARIABLES : API Router Configuration ===========


# =========== FUNCTION ===========
# ROLE: Fast health check endpoint reporting service status and environment.
@router.get("/health")
async def health_check():
    """ Returns overall API status check response. """
    
    # FLOW-1: Return immediate environment and version metadata
    return {"status": "ok", "environment": settings.ENVIRONMENT, "version": "1.0.0"}  # USE: Liveness probe check response
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Readiness check testing connection stability to Postgres DB and Redis Cache.
@router.get("/ready")
async def readiness_check(db: DBSession, cache: Cache):
    """ Validates downstream resource connections before allowing traffic. """
    
    # FLOW-1: Check database connectivity
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))      # USE: Execute dummy SELECT on DB
        
    except Exception:
        db_status = "error"
        
    # FLOW-2: Check cache server connectivity
    cache_status = "ok"
    try:
        await cache.ping()                      # USE: Ping Redis cache
        
    except Exception:
        cache_status = "error"
        
    # FLOW-3: If any downstream resource fails, return service unavailable status 503
    if db_status == "error" or cache_status == "error":
        return JSONResponse(
            status_code=503,                    # USE: Service unavailable HTTP status
            content={"status": "not ready", "db": db_status, "cache": cache_status}  # USE: Detailed error response dict
        )
        
    # FLOW-4: Return active status if all connections succeed
    return {"status": "ready", "db": "ok", "cache": "ok"}
# =========== FUNCTION ===========