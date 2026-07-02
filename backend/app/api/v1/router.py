# WHAT DOES THIS FILE DO: Combines and exposes all API v1 endpoints under a unified router.

# ================== IMPORTS ==================
from fastapi import APIRouter

from app.api.v1.research import router as research_router
from app.api.v1.health import router as health_router
# ================== IMPORTS ==================


# =========== VARIABLES : Root Router for v1 API ===========
api_router = APIRouter()                    # USE: Primary router mapping all v1 routes

# FLOW-1: Include the research and health routers into the main router
api_router.include_router(research_router)  # USE: Mount research router (already prefix-bound)
api_router.include_router(health_router, prefix="/health")  # USE: Mount health router with /health prefix
api_router.include_router(health_router)    # USE: Mount health router directly without prefix to support /health and /ready routes
# =========== VARIABLES : Root Router for v1 API ===========