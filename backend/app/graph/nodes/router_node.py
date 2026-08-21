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

    # FLOW-4: Topic value doubles as the specialist agent key ("science"/"technology"/"general")
    return {"topic": topic, "selected_agent": topic, "status": "awaiting_approval"}
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Conditional edge function selecting the next node based on the router's agent choice.
def route_after_approval(state: GraphState) -> str:
    """ Returns the routing key LangGraph uses to pick the next node after human approval. """

    # FLOW-1: Map the selected specialist agent to its conditional edge routing key
    routing_map = {
        "science": "science_research",
        "technology": "tech_research",
        "general": "general_research",
    }                                            # USE: Agent key to routing key lookup

    return routing_map.get(state.get("selected_agent"), "general_research")  # USE: Default to general on unknown/missing agent
# =========== FUNCTION ===========