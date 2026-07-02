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
        
    # FLOW-2: Log graph completion audit metadata
    logger.info(
        "graph_completed",
        session_id=state["session_id"],
        topic=state["topic"],
        status="completed"
    )                                           # USE: Log execution metrics
    
    # FLOW-3: Return final completed status
    return {"status": "completed"}
# =========== FUNCTION ===========