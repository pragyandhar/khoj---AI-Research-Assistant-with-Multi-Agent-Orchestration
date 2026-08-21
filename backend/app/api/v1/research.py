# UPDATE THE CODE:
# Task-1: POST /sessions/{session_id}/approve endpoint add karo — yeh graph ko resume karta hai human approval ke baad
# Task-2: Andar config = {"configurable": {"thread_id": session_id}} banao — LangGraph is config se sahi thread ki state dhundhta hai
# Task-3: await app.state.graph.aupdate_state(config, {"human_approved": True}) call karo — yeh state mein approval set karta hai bina graph dobara start kiye
# Task-4: async for event in app.state.graph.astream(None, config=config) se graph resume karo — None input isliye ki state already updated hai, naya input nahi chahiye
# Task-5: GET /sessions/{session_id}/state endpoint add karo — await app.state.graph.aget_state(config) call karo, current state return karo — frontend graph visualizer ke liye
# Task-6: POST /sessions/{session_id}/rollback stub ko implement karo — checkpoint_id body se lo, await app.state.graph.aupdate_state(config, values, as_node="router") se state rollback karo — as_node batata hai ki kahan se resume hoga

# WHAT DOES THIS FILE DO: Defines FastAPI endpoints for executing research queries and retrieving session/report status.

# ================== IMPORTS ==================
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.dependencies import DBSession, AuthKey, Cache
from app.core.exceptions import SessionNotFoundException
from app.db.tables.reports import Report
from app.models.research import ResearchRequest, StreamEvent
from app.models.report import StructuredReport
from app.models.session import SessionState
from app.repositories.document_repository import DocumentRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.session_repository import SessionRepository
from app.services.cache_service import CacheService
from app.services.embedding_service import EmbeddingService
from app.services.research_service import ResearchService
from app.services.session_service import SessionService
from app.tools.rag_retriever import get_chroma_collection
# ================== IMPORTS ==================


# =========== VARIABLES : API Router Configuration ===========
router = APIRouter(prefix="/research", tags=["research"])  # USE: Router instance for research endpoints
# =========== VARIABLES : API Router Configuration ===========


# =========== CLASS ===========
# ROLE: Request body schema representing rollback target checkpoint metadata.
class RollbackRequest(BaseModel):
    """ Target checkpoint ID for state rollbacks. """
    checkpoint_id: str
# =========== CLASS ===========


# =========== CLASS ===========
# ROLE: Request body schema for the approval endpoint, allowing an optional query edit.
class ApproveRequest(BaseModel):
    """ Optional query modification submitted alongside human approval. """
    modified_query: str | None = None
# =========== CLASS ===========


# =========== FUNCTION ===========
# ROLE: Starts research query execution and streams status and report data via SSE.
@router.post("/query")
async def start_research(request: ResearchRequest, raw_request: Request, api_key: AuthKey, db: DBSession, cache: Cache):
    """ Post route to trigger full research pipeline with Server-Sent Events. """
    
    # FLOW-1: Initialize repositories and service class
    session_repo = SessionRepository(db)        # USE: Session repository instance
    report_repo = ReportRepository(db)          # USE: Report repository instance
    cache_service = CacheService(cache)         # USE: Cache service client wrapper instance
    chroma_collection = await get_chroma_collection()  # USE: Shared ChromaDB collection handle
    embedding_service = EmbeddingService(chroma_collection, DocumentRepository(db))  # USE: Indexes completed reports for future RAG
    research_service = ResearchService(
        session_repo,
        report_repo,
        cache_service,
        graph=raw_request.app.state.graph,
        embedding_service=embedding_service
    )                                           # USE: Instantiate service orchestrator
    
    
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
# ROLE: Approving human check and resuming graph workflow execution.
@router.post("/sessions/{session_id}/approve")
async def approve_session(session_id: str, body: ApproveRequest, raw_request: Request, api_key: AuthKey, db: DBSession, cache: Cache):
    """ Approve the human check gate, optionally editing the query, and resume execution streaming. """

    # FLOW-1: Set up thread configuration and resume graph state updates
    config = {"configurable": {"thread_id": session_id}}  # USE: Config referencing the session thread
    state_update = {"human_approved": True}     # USE: Base state update marking approval
    if body.modified_query:
        state_update["modified_query"] = body.modified_query  # USE: Pass user's edited query through to human_approval_node
    await raw_request.app.state.graph.aupdate_state(config, state_update)  # USE: Update approval (and optional query edit) in state
    
    
    # =========== FUNCTION ===========
    # ROLE: Nested generator executing the resumed graph workflow and formatting events to SSE.
    async def approve_generator():
        """ Async generator mapping resumed state updates to SSE JSON format. """
        
        session_repo = SessionRepository(db)    # USE: Instantiate session repository
        report_repo = ReportRepository(db)      # USE: Instantiate report repository
        
        state_accumulator = {}                  # USE: Accumulate output attributes
        
        # FLOW-1: Resume graph run and loop through events.
        # Node order post-approval is human_approval -> research -> summary -> citation_check -> output,
        # so each status reflects the node that runs NEXT after the one that just completed.
        async for event in raw_request.app.state.graph.astream(None, config=config):  # USE: Resume stream with empty input payload
            for node_name, output in event.items():  # USE: Loop over node output dicts
                if isinstance(output, dict):
                    state_accumulator.update(output)  # USE: Accumulate node output dictionary

                    if node_name == "human_approval":
                        await session_repo.update_status(session_id, "researching")  # USE: Update DB status to researching
                        yield f"data: {StreamEvent(event_type='status', data={'status': 'researching'}).model_dump_json()}\n\n"

                    elif node_name == "research":
                        await session_repo.update_status(session_id, "summarizing")  # USE: Update DB status to summarizing
                        yield f"data: {StreamEvent(event_type='status', data={'status': 'summarizing'}).model_dump_json()}\n\n"

                    elif node_name == "summary":
                        await session_repo.update_status(session_id, "citing")  # USE: Update DB status to citing
                        yield f"data: {StreamEvent(event_type='status', data={'status': 'citing'}).model_dump_json()}\n\n"

        # FLOW-2: Retrieve and persist report results
        final_report_dict = state_accumulator.get("final_report")
        if final_report_dict:
            state_info = await raw_request.app.state.graph.aget_state(config)  # USE: Retrieve graph state
            current_state = state_info.values
            topic = current_state.get("topic", "")
            query = current_state.get("query", "")
            
            # Persist report details to DB
            db_report = Report(
                session_id=session_id,
                query=query,
                report_data=final_report_dict,
                topic=topic,
                confidence_score=final_report_dict.get("confidence_score"),
            )                                   # USE: Create Report DB model
            await report_repo.create(db_report)  # USE: Save report record in DB
            await session_repo.update_status(session_id, "completed")  # USE: Update session status to completed
            
            # Cache output in Redis
            report_obj = StructuredReport.model_validate(final_report_dict)  # USE: Parse dict to Pydantic object
            cache_service = CacheService(cache)  # USE: Cache service client wrapper instance
            await cache_service.set(query, report_obj)  # USE: Save report object in cache

            # Index the report into ChromaDB for future RAG retrieval
            chroma_collection = await get_chroma_collection()  # USE: Shared ChromaDB collection handle
            embedding_service = EmbeddingService(chroma_collection, DocumentRepository(db))  # USE: Indexes this report's chunks
            await embedding_service.index_report(report_obj, session_id)

            yield f"data: {StreamEvent(event_type='report', data=final_report_dict).model_dump_json()}\n\n"  # USE: Yield final report SSE payload
    # =========== FUNCTION ===========
    
    
    # FLOW-2: Return StreamingResponse carrying the SSE stream
    return StreamingResponse(
        approve_generator(),                    # USE: Stream generator callable
        media_type="text/event-stream",         # USE: SSE content type header
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}  # USE: Disable proxy buffering headers
    )
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Retrieves the aggregated session state for the frontend graph visualizer.
@router.get("/sessions/{session_id}/state", response_model=SessionState)
async def get_session_state(session_id: str, raw_request: Request, api_key: AuthKey, db: DBSession):
    """ Retrieve session status, current node, and per-agent execution timeline. """

    # FLOW-1: Instantiate session service and delegate state serialization
    session_repo = SessionRepository(db)        # USE: Instantiate session repository
    session_service = SessionService(session_repo, raw_request.app.state.graph)  # USE: Service combining DB + graph state

    return await session_service.get_session_state(session_id)
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Lists every checkpoint recorded for a session, for the frontend time-travel UI.
@router.get("/sessions/{session_id}/checkpoints")
async def list_session_checkpoints(session_id: str, raw_request: Request, api_key: AuthKey, db: DBSession):
    """ Retrieve every checkpoint's ID, timestamp, and producing node, oldest first. """

    # FLOW-1: Instantiate session service and delegate checkpoint history listing
    session_repo = SessionRepository(db)        # USE: Instantiate session repository
    session_service = SessionService(session_repo, raw_request.app.state.graph)  # USE: Service combining DB + graph state

    return await session_service.list_checkpoints(session_id)
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Resets current session state values back to a target checkpoint.
@router.post("/sessions/{session_id}/rollback")
async def rollback_session(session_id: str, body: RollbackRequest, raw_request: Request, api_key: AuthKey, db: DBSession):
    """ Rollback session to a prior state checkpoint. """

    # FLOW-1: Instantiate session service and delegate the rollback operation
    session_repo = SessionRepository(db)        # USE: Instantiate session repository
    session_service = SessionService(session_repo, raw_request.app.state.graph)  # USE: Service combining DB + graph state

    await session_service.rollback_to_checkpoint(session_id, body.checkpoint_id)

    return {"message": "Rollback successful", "session_id": session_id, "next_node": "router"}
# =========== FUNCTION ===========