# WHAT DOES THIS FILE DO: Defines Pydantic request/response models and status enums for research endpoints.

# ================== IMPORTS ==================
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Data model representing research request payload.
class ResearchRequest(BaseModel):
    """ Payload sent by client to start a research session. """

    # FLOW-1: Set up client query and session tracking fields
    query: str = Field(..., min_length=10, max_length=500, description="Research query")  # USE: The main prompt/question
    topic_hint: str | None = Field(None, description="Optional topic hint")  # USE: Categorization hint
    session_id: str | None = Field(None, description="Existing session ID for continuation")  # USE: Connect to historical state
# =========== CLASS ===========


# =========== CLASS ===========
# ROLE: Enum tracking the different phases of research execution.
class ResearchStatus(str, Enum):
    """ Enumeration of all valid research execution states. """

    # FLOW-1: Declare string enum values for easy DB and JSON serializing
    PENDING = "pending"
    ROUTING = "routing"
    RESEARCHING = "researching"
    SUMMARIZING = "summarizing"
    CITING = "citing"
    COMPLETED = "completed"
    FAILED = "failed"
# =========== CLASS ===========


# =========== CLASS ===========
# ROLE: Model representing a single event block sent in SSE stream.
class StreamEvent(BaseModel):
    """ Server sent event container for token and status streaming. """

    # FLOW-1: Set up event metadata and payload fields
    event_type: str                             # USE: Action type (e.g. status, token)
    data: dict                                  # USE: Arbitrary data payload
    timestamp: datetime = Field(default_factory=datetime.utcnow)  # USE: When event was dispatched
# =========== CLASS ===========


# =========== CLASS ===========
# ROLE: Model representing research final status and output report response.
class ResearchResponse(BaseModel):
    """ Structure for research query final output representation. """

    # FLOW-1: Define response fields for client consumption
    session_id: str                             # USE: Key identification for session
    status: ResearchStatus                      # USE: Current execution phase
    report: dict | None = None                  # USE: Final structured report JSON if done
    error: str | None = None                    # USE: Error description if state is failed
    created_at: datetime                        # USE: Timestamp when response was built
# =========== CLASS ===========