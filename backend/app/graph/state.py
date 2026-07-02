# WHAT DOES THIS FILE DO: Defines the GraphState schema used for tracking workflow execution details inside LangGraph.

# ================== IMPORTS ==================
import operator
from typing import Annotated, Optional

from typing_extensions import TypedDict
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Defines the state dict schema used across the LangGraph orchestration flow.
class GraphState(TypedDict):
    """ TypedDict schema tracking execution state inside the LangGraph compilation. """
    
    query: str
    topic: str
    research_output: str
    final_report: Optional[dict]
    session_id: str
    status: str
    error: Optional[str]
    messages: Annotated[list, operator.add]
    human_approved: bool
    checkpoint_id: Optional[str]
    created_at: str
# =========== CLASS ===========