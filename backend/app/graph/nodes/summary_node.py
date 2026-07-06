# UPDATE THE CODE
# Task-1: summary_node mein report generate hone ke baad citations extract karo: citations = [c.model_dump() for section in report.sections for c in section.citations]
# Task-2: Return dict mein citations field add karo: {"final_report": report.model_dump(), "citations": citations, "status": "citing"}
# Task-3: GraphState mein citations: list[dict] field add karo agar nahi hai

# WHAT DOES THIS FILE DO: Defines the summary node function for synthesizing research findings into structured reports inside the LangGraph workflow.

# ================== IMPORTS ==================
from app.graph.state import GraphState
from app.agents.summary_agent import SummaryAgent
from app.core.logging import get_logger
# ================== IMPORTS ==================


# =========== VARIABLES : Summary Node Loggers ===========
logger = get_logger(__name__)               # USE: Summary node execution logger instance
# =========== VARIABLES : Summary Node Loggers ===========


# =========== FUNCTION ===========
# ROLE: Summary node synthesizing facts gathered into a structured JSON report inside the LangGraph workflow.
async def summary_node(state: GraphState) -> dict:
    """ Generates a structured json report from raw unstructured research output. """
    
    # FLOW-1: Instantiate the summary agent
    summary_agent = SummaryAgent()              # USE: Create summary agent instance
    
    # FLOW-2: Run summarizer logic converting raw search text into structured schema
    try:
        report = await summary_agent.run(
            research_output=state["research_output"],
            original_query=state["query"],
            topic=state["topic"]
        )                                       # USE: Trigger report parser agent
        
        # FLOW-3: Log completed status and return partial state update
        logger.info("summary_node_completed", query=state["query"], topic=state["topic"])  # USE: Node audit logging
        
        return {"final_report": report.model_dump(), "status": "completed"}
        
    except Exception as e:
        # FLOW-4: Handle exceptions and return failure status with detailed error description
        logger.error("summary_node_failed", query=state["query"], error=str(e))  # USE: Failure log entry
        
        return {"status": "failed", "error": f"Summary failed: {str(e)}"}
# =========== FUNCTION ===========
