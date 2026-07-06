# WHAT DOES THIS FILE DO: Defines the output node function for finalizing the LangGraph workflow execution.

# ================== IMPORTS ==================
from app.graph.state import GraphState
from app.core.logging import get_logger
# ================== IMPORTS ==================


# =========== VARIABLES : Output Node Loggers ===========
logger = get_logger(__name__)               # USE: Output node execution logger instance
# =========== VARIABLES : Output Node Loggers ===========


# =========== FUNCTION ===========
# ROLE: Output node logging and finalizing the workflow state execution status.
async def output_node(state: GraphState) -> dict:
    """ Evaluates final state errors and marks state machine status as completed. """
    
    # FLOW-1: Check if execution encountered errors and return failed status
    if state.get("error"):
        return {"status": "failed"}             # USE: Terminate with failed status
        
    # FLOW-2: Reconstruct final_report by filtering out failed citation URLs
    final_report = state.get("final_report")
    verified_citations = state.get("verified_citations") or []
    citations = state.get("citations") or []
    
    if final_report:
        verified_urls = {c.get("url") for c in verified_citations if c.get("url")}  # USE: Build unique set of verified URLs
        
        for section in final_report.get("sections", []):
            section_citations = section.get("citations", [])
            # Filter section citations to only keep verified ones
            section["citations"] = [c for c in section_citations if c.get("url") in verified_urls]  # USE: Filter citations list
            
        total_citations_count = len(citations)
        original_confidence = float(final_report.get("confidence_score", 1.0))
        
        if total_citations_count > 0:
            new_confidence = (len(verified_citations) / total_citations_count) * original_confidence
        else:
            new_confidence = original_confidence
            
        final_report["total_sources"] = len(verified_citations)
        final_report["confidence_score"] = round(new_confidence, 2)
        
    # FLOW-3: Log graph completion audit metadata
    logger.info(
        "graph_completed",
        session_id=state["session_id"],
        topic=state["topic"],
        status="completed"
    )                                           # USE: Log execution metrics
    
    # FLOW-4: Return final completed status and updated final report
    return {"status": "completed", "final_report": final_report}
# =========== FUNCTION ===========