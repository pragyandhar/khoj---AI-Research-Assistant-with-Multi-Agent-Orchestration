# WHAT DOES THIS FILE DO: Defines the research node function for web searching and fact-gathering inside the LangGraph workflow.

# ================== IMPORTS ==================
from app.graph.state import GraphState
from app.agents.research_agent import ResearchAgent
from app.core.logging import get_logger
# ================== IMPORTS ==================


# =========== VARIABLES : Research Node Loggers ===========
logger = get_logger(__name__)               # USE: Research node execution logger instance
# =========== VARIABLES : Research Node Loggers ===========


# =========== FUNCTION ===========
# ROLE: Research node executing facts gathering via search agents in the LangGraph workflow.
async def research_node(state: GraphState) -> dict:
    """ Conducts topic web search research using the research agent. """
    
    # FLOW-1: Instantiate the research agent
    research_agent = ResearchAgent()            # USE: Create research agent instance
    
    # FLOW-2: Run research react agent using query and topic state variables
    try:
        research_output = await research_agent.run(
            query=state["query"],
            topic=state["topic"]
        )                                       # USE: Trigger research workflow search
        
        # FLOW-3: Log research completed status and return partial state update
        logger.info(
            "research_node_completed",
            topic=state["topic"],
            output_length=len(research_output)
        )                                       # USE: Node audit logging
        
        return {"research_output": research_output, "status": "summarizing"}
        
    except Exception as e:
        # FLOW-4: Handle exceptions and return failure status with error details
        logger.error("research_node_failed", query=state["query"], error=str(e))  # USE: Failure log entry
        
        return {"status": "failed", "error": str(e)}
# =========== FUNCTION ===========