# WHAT DOES THIS FILE DO: Orchestrates the execution flow of query routing, research searching, and report summarizing using LangGraph.

# ================== IMPORTS ==================
from typing import AsyncGenerator
from datetime import datetime
import uuid

from app.db.tables.reports import Report
from app.db.tables.sessions import Session
from app.graph.main_graph import graph
from app.graph.state import GraphState
from app.models.research import ResearchRequest, StreamEvent
from app.models.report import StructuredReport
from app.repositories.report_repository import ReportRepository
from app.repositories.session_repository import SessionRepository
from app.services.cache_service import CacheService
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: High-level service orchestrating research agents execution workflow.
class ResearchService:
    """ Service coordinates query routing, searching, summarizing and report saving. """


    # =========== FUNCTION ===========
    # ROLE: Initialize ResearchService with database and cache repositories.
    def __init__(self, session_repository: SessionRepository, report_repository: ReportRepository, cache_service: CacheService = None):
        """ Setup database repositories and cache service layer. """
        
        # FLOW-1: Assign repository and cache service dependencies
        self.session_repo = session_repository  # USE: Session data table access repository
        self.report_repo = report_repository    # USE: Report data table access repository
        self.cache_service = cache_service      # USE: Optional Cache service layer instance
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Process query flow, streaming events and persisting session results.
    async def process(self, request: ResearchRequest) -> AsyncGenerator[StreamEvent, None]:
        """ Run the full research pipeline and yield status update events. """
        
        # FLOW-1: Check cache service first and return cache hit details if exists
        if self.cache_service:
            cached_report = await self.cache_service.get(request.query)  # USE: Attempt cache retrieve
            
            if cached_report:
                yield StreamEvent(
                    event_type="cache_hit",
                    data={"report": cached_report.model_dump()}
                )                               # USE: Stream cache hit response
                
                return
                
        # FLOW-2: Create research session and initialize transaction ID
        session_id = str(uuid.uuid4())          # USE: Generate new UUID string key
        
        try:
            db_session = Session(
                session_id=session_id,
                status="pending"
            )                                   # USE: Create DB session record instance
            await self.session_repo.create(db_session)  # USE: Persist session row in database
            
            # FLOW-3: Build initial GraphState input dictionary
            initial_state = GraphState(
                query=request.query,
                topic="",
                research_output="",
                final_report=None,
                session_id=session_id,
                status="pending",
                error=None,
                messages=[],
                human_approved=False,
                graph_checkpoint_id=None,
                created_at=datetime.utcnow().isoformat()
            )                                   # USE: Instantiate graph input state payload
            
            # FLOW-4: Run streaming graph execution events and yield status updates
            state_accumulator = {}              # USE: Dictionary to collect partial node outputs
            
            async for event in graph.astream_events(initial_state, version="v2"):  # USE: Stream events from graph execution
                if event.get("event") == "on_chain_end":
                    node_name = event.get("name")
                    output = event.get("data", {}).get("output")
                    
                    # If this is one of our registered nodes, accumulate output and update progress
                    if node_name in ["router", "research", "summary", "output"] and isinstance(output, dict):
                        state_accumulator.update(output)  # USE: Accumulate node output state attributes
                        
                        if node_name == "router":
                            topic = output.get("topic", "")
                            await self.session_repo.update_status(session_id, "researching")  # USE: Update session status in DB
                            yield StreamEvent(event_type="status", data={"status": "researching", "topic": topic})  # USE: Stream status event
                            
                        elif node_name == "research":
                            await self.session_repo.update_status(session_id, "summarizing")  # USE: Update session status in DB
                            yield StreamEvent(event_type="status", data={"status": "summarizing"})  # USE: Stream status event
                            
            # FLOW-5: Extract accumulated final report and persist details to DB and cache
            final_report_dict = state_accumulator.get("final_report")
            topic = state_accumulator.get("topic", "")
            
            if not final_report_dict:
                error_msg = state_accumulator.get("error") or "Execution failed to produce a report"
                raise Exception(error_msg)
                
            db_report = Report(
                session_id=session_id,
                query=request.query,
                report_data=final_report_dict,
                topic=topic,
                confidence_score=final_report_dict.get("confidence_score"),
            )                                   # USE: Instantiate Report ORM model
            await self.report_repo.create(db_report)  # USE: Persist report to database
            await self.session_repo.update_status(session_id, "completed")  # USE: Mark session completed in DB
            
            report_obj = StructuredReport.model_validate(final_report_dict)  # USE: Validate dict to Pydantic object
            
            if self.cache_service:
                await self.cache_service.set(request.query, report_obj)  # USE: Save to Redis Cache
                
            yield StreamEvent(event_type="report", data=final_report_dict)  # USE: Stream final output report
            
        except Exception as e:
            # FLOW-6: Handle any errors, mark session failed and yield error event
            await self.session_repo.update_status(session_id, "failed")  # USE: Update session status to failed in DB
            
            yield StreamEvent(event_type="error", data={"message": str(e)})  # USE: Stream error event details
    # =========== FUNCTION ===========
# =========== CLASS ===========