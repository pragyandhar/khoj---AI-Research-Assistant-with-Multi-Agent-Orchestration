# WHAT DOES THIS FILE DO: Defines Pydantic models representing session and per-agent execution state for API responses.

# ================== IMPORTS ==================
from datetime import datetime
from pydantic import BaseModel
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Model representing a single node/agent's execution window within a session.
class AgentExecution(BaseModel):
    """ Tracks one node's execution span inside the research graph. """

    agent_name: str                             # USE: Name of the graph node/agent that ran
    started_at: datetime                        # USE: When this node started executing
    completed_at: datetime | None = None        # USE: When this node finished, if it has
    status: str                                 # USE: Execution status (e.g. completed, running)
    output_length: int | None = None            # USE: Best-effort size of the node's output, if applicable
# =========== CLASS ===========


# =========== CLASS ===========
# ROLE: Model representing the full current state of a research session for API/frontend consumption.
class SessionState(BaseModel):
    """ Aggregated session state exposed to the frontend graph visualizer. """

    session_id: str                             # USE: Logical session identifier
    current_node: str | None = None             # USE: Node the graph is currently paused/scheduled on
    selected_agent: str | None = None           # USE: Specialist agent chosen for this session's research
    status: str                                 # USE: Overall session status
    agent_executions: list[AgentExecution] = []  # USE: Timeline of nodes executed so far
    human_approved: bool                        # USE: Whether the human approval gate has been passed
    created_at: datetime                        # USE: Session creation timestamp
    updated_at: datetime                        # USE: Last state modification timestamp
# =========== CLASS ===========
