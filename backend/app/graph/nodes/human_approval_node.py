# WHAT DOES THIS FILE DO: Defines the human approval node for workflow authorization step.

# ================== IMPORTS ==================
from app.graph.state import GraphState
from app.core.logging import get_logger
# ================== IMPORTS ==================


# =========== VARIABLES : Human Approval Node Loggers ===========
logger = get_logger(__name__)               # USE: Logger for human approval node
# =========== VARIABLES : Human Approval Node Loggers ===========


# =========== FUNCTION ===========
# ROLE: Checks human approval flag and determines whether to pause or advance the graph.
async def human_approval_node(state: GraphState) -> dict:
    """ Evaluates user approval flag to permit or pause execution. """
    
    # FLOW-1: Check if human_approved flag is set in state
    if not state.get("human_approved", False):
        return {"status": "awaiting_approval"}  # USE: Transition status to awaiting approval
        
    # FLOW-2: Log successful user confirmation
    logger.info("human_approved_research", session_id=state["session_id"], query=state["query"])  # USE: Node audit logging
    
    # FLOW-3: Return updated status advancing the workflow
    return {"human_approved": True, "status": "researching"}
# =========== FUNCTION ===========