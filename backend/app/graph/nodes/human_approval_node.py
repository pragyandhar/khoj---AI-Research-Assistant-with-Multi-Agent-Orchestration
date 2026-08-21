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
    """ Evaluates user approval flag to permit or pause execution, applying any query edits. """

    # FLOW-1: Check if human_approved flag is set in state
    if not state.get("human_approved", False):
        return {"status": "awaiting_approval"}  # USE: Transition status to awaiting approval

    # FLOW-2: Build the base advancing state update
    result = {"human_approved": True, "status": "researching"}  # USE: Default approved state update

    # FLOW-3: If the user modified the query at approval time, swap it into the active query
    modified_query = state.get("modified_query")
    if modified_query:
        logger.info("query_modified_by_user", original=state["query"], modified=modified_query)  # USE: Audit log of the query edit
        result["query"] = modified_query        # USE: Research proceeds with the user-edited query

    # FLOW-4: Log successful user confirmation
    logger.info("human_approved_research", session_id=state["session_id"], query=result.get("query", state["query"]))  # USE: Node audit logging

    return result
# =========== FUNCTION ===========