# WHAT DOES THIS FILE DO: Defines the router node function for query classification inside the LangGraph workflow.

# ================== IMPORTS ==================
from app.graph.state import GraphState
from app.agents.router_agent import RouterAgent
from app.core.logging import get_logger
# ================== IMPORTS ==================


# =========== VARIABLES : Router Node Loggers ===========
logger = get_logger(__name__)               # USE: Router node execution logger instance
# =========== VARIABLES : Router Node Loggers ===========


# =========== FUNCTION ===========
# ROLE: Router node classifying the query topic to direct the workflow execution graph.
async def router_node(state: GraphState) -> dict:
    """ Executes query topic classification using the router agent. """
    
    # FLOW-1: Instantiate the router agent
    router_agent = RouterAgent()                # USE: Create router agent instance
    
    # FLOW-2: Classify the topic category from the user query
    topic = await router_agent.run(query=state["query"])  # USE: Run classification logic
    
    # FLOW-3: Log result and return updated state attributes
    logger.info("router_node_completed", query=state["query"], topic=topic)  # USE: Node audit logging
    
    return {"topic": topic, "status": "researching"}
# =========== FUNCTION ===========