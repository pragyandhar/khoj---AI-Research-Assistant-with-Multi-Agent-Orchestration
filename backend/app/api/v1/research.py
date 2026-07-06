# UPDATE THE CODE:
# Task-1: POST /sessions/{session_id}/approve endpoint add karo — yeh graph ko resume karta hai human approval ke baad
# Task-2: Andar config = {"configurable": {"thread_id": session_id}} banao — LangGraph is config se sahi thread ki state dhundhta hai
# Task-3: await app.state.graph.aupdate_state(config, {"human_approved": True}) call karo — yeh state mein approval set karta hai bina graph dobara start kiye
# Task-4: async for event in app.state.graph.astream(None, config=config) se graph resume karo — None input isliye ki state already updated hai, naya input nahi chahiye
# Task-5: GET /sessions/{session_id}/state endpoint add karo — await app.state.graph.aget_state(config) call karo, current state return karo — frontend graph visualizer ke liye
# Task-6: POST /sessions/{session_id}/rollback stub ko implement karo — checkpoint_id body se lo, await app.state.graph.aupdate_state(config, values, as_node="router") se state rollback karo — as_node batata hai ki kahan se resume hoga

# WHAT DOES THIS FILE DO: Defines FastAPI endpoints for executing research queries and retrieving session/report status.

# ================== IMPORTS ==================
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.core.dependencies import DBSession, AuthKey, Cache
from app.core.exceptions import SessionNotFoundException
from app.models.research import ResearchRequest
from app.repositories.report_repository import ReportRepository
from app.repositories.session_repository import SessionRepository
from app.services.cache_service import CacheService
from app.services.research_service import ResearchService
# ================== IMPORTS ==================


# =========== VARIABLES : API Router Configuration ===========
router = APIRouter(prefix="/research", tags=["research"])  # USE: Router instance for research endpoints
# =========== VARIABLES : API Router Configuration ===========


# =========== FUNCTION ===========
# ROLE: Starts research query execution and streams status and report data via SSE.
@router.post("/query")
async def start_research(request: ResearchRequest, api_key: AuthKey, db: DBSession, cache: Cache):
    """ Post route to trigger full research pipeline with Server-Sent Events. """
    
    # FLOW-1: Initialize repositories and service class
    session_repo = SessionRepository(db)        # USE: Session repository instance
    report_repo = ReportRepository(db)          # USE: Report repository instance
    cache_service = CacheService(cache)         # USE: Cache service client wrapper instance
    research_service = ResearchService(session_repo, report_repo, cache_service)  # USE: Instantiate service orchestrator
    
    
    # =========== FUNCTION ===========
    # ROLE: Nested generator converting research service output to SSE formatting.
    async def event_generator():
        """ Async generator mapping StreamEvents to data string format. """
        
        # FLOW-1: Loop through process generator output and format as SSE string
        async for event in research_service.process(request):  # USE: Loop over service process events
            yield f"data: {event.model_dump_json()}\n\n"  # USE: SSE format serialization yielding
    # =========== FUNCTION ===========
    
    
    # FLOW-2: Return streaming response with appropriate SSE headers
    return StreamingResponse(
        event_generator(),                      # USE: Stream generator callable
        media_type="text/event-stream",         # USE: SSE content type header
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}  # USE: Disable proxy buffering headers
    )
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Retrieves stored session details by session_id.
@router.get("/sessions/{session_id}")
async def get_session(session_id: str, db: DBSession):
    """ Retrieves session status and checkpointer details. """
    
    # FLOW-1: Query session from repository and handle 404
    session_repo = SessionRepository(db)        # USE: Instantiate session repository
    session_obj = await session_repo.get_by_session_id(session_id)  # USE: Fetch DB record by string key
    
    if not session_obj:
        raise SessionNotFoundException(f"Session {session_id} not found")  # USE: Raise 404 error
        
    return session_obj
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Retrieves the latest generated report for a given session.
@router.get("/sessions/{session_id}/report")
async def get_latest_report(session_id: str, db: DBSession):
    """ Fetch the latest completed report for a session_id. """
    
    # FLOW-1: Retrieve report from repository and handle 404
    report_repo = ReportRepository(db)          # USE: Instantiate report repository
    report_obj = await report_repo.get_latest_report(session_id)  # USE: Query latest record from DB
    
    if not report_obj:
        raise SessionNotFoundException(f"Report for session {session_id} not found")  # USE: Raise 404 error if missing
        
    return report_obj
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Rollback session to previous checkpoint (Phase 3 stub).
@router.post("/sessions/{session_id}/rollback")
async def rollback_session(session_id: str):
    """ Rollback session to a prior state checkpoint. """
    
    # FLOW-1: Return a phase 3 placeholder message
    return {"message": "Coming in Phase 3"}
# =========== FUNCTION ===========