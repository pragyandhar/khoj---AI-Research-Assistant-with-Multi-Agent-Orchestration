# WHAT DOES THIS FILE DO: Orchestrates the execution flow of query routing, research searching, and report summarizing.

# ================== IMPORTS ==================
from typing import AsyncGenerator
import uuid

from app.agents.research_agent import ResearchAgent
from app.agents.router_agent import RouterAgent
from app.agents.summary_agent import SummaryAgent
from app.db.tables.reports import Report
from app.db.tables.sessions import Session
from app.models.research import ResearchRequest, StreamEvent
from app.repositories.report_repository import ReportRepository
from app.repositories.session_repository import SessionRepository
from app.services.cache_service import CacheService
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: High-level service orchestrating research agents execution workflow.
class ResearchService:
    """ Service coordinates query routing, searching, summarizing and report saving. """


    # =========== FUNCTION ===========
    # ROLE: Initialize ResearchService and instantiate target agents.
    def __init__(self, session_repository: SessionRepository, report_repository: ReportRepository, cache_service: CacheService = None):
        """ Setup agents and repositories for orchestrating research flow. """
        
        # FLOW-1: Assign repository dependencies and cache service
        self.session_repo = session_repository  # USE: Session data table access repository
        self.report_repo = report_repository    # USE: Report data table access repository
        self.cache_service = cache_service      # USE: Optional Cache service layer instance
        
        # FLOW-2: Instantiate sub-agents
        self.router_agent = RouterAgent()       # USE: Agent to classify user query topic
        self.research_agent = ResearchAgent()   # USE: Agent to execute web search
        self.summary_agent = SummaryAgent()     # USE: Agent to synthesize final structured JSON
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Process query flow, streaming events and persisting session results.
    async def process(self, request: ResearchRequest) -> AsyncGenerator[StreamEvent, None]:
        """ Run the full research pipeline and yield status update events. """
        
        # FLOW-1: Check cache service first and return cached report if hit
        if self.cache_service:
            cached_report = await self.cache_service.get(request.query)  # USE: Attempt cache retrieve
            
            if cached_report:
                yield StreamEvent(event_type="report", data=cached_report.model_dump())  # USE: Stream cache report response
                
                return
                
        # FLOW-2: Create research session and initialize transaction ID
        session_id = str(uuid.uuid4())          # USE: Generate new UUID string key
        
        try:
            db_session = Session(
                session_id=session_id,
                status="pending"
            )                                   # USE: Create DB session record instance
            await self.session_repo.create(db_session)  # USE: Persist session row in database
            
            # FLOW-3: Yield routing start event and run classification
            yield StreamEvent(event_type="status", data={"status": "routing", "session_id": session_id})  # USE: Stream status update
            topic = await self.router_agent.run(request.query)  # USE: Determine topic category
            
            # FLOW-4: Update DB status to researching and run web search
            await self.session_repo.update_status(session_id, "researching")  # USE: Save progress to database
            yield StreamEvent(event_type="status", data={"status": "researching", "topic": topic})  # USE: Stream search starting event
            research_output = await self.research_agent.run(request.query, topic)  # USE: Run react agent search
            
            # FLOW-5: Update DB status to summarizing and build report schema
            await self.session_repo.update_status(session_id, "summarizing")  # USE: Save progress to database
            yield StreamEvent(event_type="status", data={"status": "summarizing"})  # USE: Stream summarizing start event
            report_data = await self.summary_agent.run(research_output, request.query, topic)  # USE: Run summarizer
            
            # FLOW-6: Save final report, complete session status, cache findings, and yield report payload
            db_report = Report(
                session_id=session_id,
                query=request.query,
                report_data=report_data.model_dump(),  # USE: Dump Pydantic schema model to dict
                topic=topic,
                confidence_score=report_data.confidence_score,
            )                                   # USE: Instantiate Report ORM model
            await self.report_repo.create(db_report)  # USE: Persist final report to database
            await self.session_repo.update_status(session_id, "completed")  # USE: Mark session completed in DB
            
            if self.cache_service:
                await self.cache_service.set(request.query, report_data)  # USE: Save new report to Redis Cache
                
            yield StreamEvent(event_type="report", data=report_data.model_dump())  # USE: Stream final output report
            
        except Exception as e:
            # FLOW-7: Handle any errors, mark session failed and yield error event
            await self.session_repo.update_status(session_id, "failed")  # USE: Update session status to failed in DB
            
            yield StreamEvent(event_type="error", data={"message": str(e)})  # USE: Stream error event details
    # =========== FUNCTION ===========
# =========== CLASS ===========