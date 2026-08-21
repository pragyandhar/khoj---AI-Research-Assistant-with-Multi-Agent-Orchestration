# WHAT DOES THIS FILE DO: Defines the research node function with specialist agent routing and tenacity-based retry logic for web searching inside LangGraph.

# ================== IMPORTS ==================
from tenacity import retry, stop_after_attempt, wait_exponential

from app.graph.state import GraphState
from app.agents.base_agent import BaseAgent
from app.agents.research_agent import ResearchAgent
from app.agents.science_agent import ScienceResearchAgent
from app.agents.technology_agent import TechnologyResearchAgent
from app.core.logging import get_logger
# ================== IMPORTS ==================


# =========== VARIABLES : Research Node Loggers ===========
logger = get_logger(__name__)               # USE: Research node execution logger instance
# =========== VARIABLES : Research Node Loggers ===========


# =========== VARIABLES : Specialist Agent Factory Map ===========
AGENT_MAP = {
    "science": ScienceResearchAgent,
    "technology": TechnologyResearchAgent,
    "general": ResearchAgent,
}                                            # USE: Maps selected_agent key to its specialist agent class
# =========== VARIABLES : Specialist Agent Factory Map ===========


# =========== FUNCTION ===========
# ROLE: Callback executed when all retry attempts are exhausted.
def retry_error_callback(retry_state):
    """ Logs the retry exhaust metadata and reraises the exception. """

    # FLOW-1: Log failure details and raise the final outcome exception
    logger.error("research_node_all_retries_failed", attempts=3)  # USE: Write error log after 3 attempts
    raise retry_state.outcome.exception()       # USE: Reraise target error
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Callback executed before each retry sleep, logging via the structlog-based logger.
def log_retry_attempt(retry_state) -> None:
    """ Logs a retry attempt. Structlog bound loggers have no stdlib .log(), so
    tenacity's built-in before_sleep_log (which calls logger.log(level, msg)) is
    incompatible here — this callback calls logger.warning(...) directly instead. """

    # FLOW-1: Log the attempt number and upcoming wait duration
    logger.warning(
        "research_node_retrying",
        attempt=retry_state.attempt_number,
        wait_seconds=retry_state.next_action.sleep if retry_state.next_action else None,
    )                                           # USE: Structlog-compatible retry warning
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Helper method wrapped in tenacity retry decorators executing research queries.
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
    before_sleep=log_retry_attempt,
    retry_error_callback=retry_error_callback
)
async def _execute_research(research_agent: BaseAgent, query: str, topic: str) -> str:
    """ Calls the research agent with query and topic payload parameters. """

    # FLOW-1: Run the research agent
    output = await research_agent.run(query=query, topic=topic)  # USE: Run react agent

    return output
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Research node executing facts gathering via the topic-appropriate specialist agent.
async def research_node(state: GraphState) -> dict:
    """ Conducts topic web search research using the selected specialist agent. """

    # FLOW-1: Select the specialist agent class based on router's classification
    selected_agent = state.get("selected_agent", "general")  # USE: Agent key chosen by router_node
    AgentClass = AGENT_MAP.get(selected_agent, ResearchAgent)  # USE: Fall back to general researcher on unknown key
    research_agent = AgentClass()               # USE: Instantiate the chosen specialist agent

    logger.info("research_node_started", selected_agent=selected_agent, topic=state["topic"])  # USE: Node audit logging

    # FLOW-2: Run research react agent with retry logic using helper function
    try:
        research_output = await _execute_research(
            research_agent,
            state["query"],
            state["topic"]
        )                                       # USE: Trigger research with tenacity retries

        # FLOW-3: Log research completed status and return partial state update
        logger.info(
            "research_node_completed",
            selected_agent=selected_agent,
            topic=state["topic"],
            output_length=len(research_output)
        )                                       # USE: Node audit logging

        return {"research_output": research_output, "status": "summarizing"}

    except Exception as e:
        # FLOW-4: Handle exceptions and return failure status with error details
        logger.error("research_node_failed", selected_agent=selected_agent, query=state["query"], error=str(e))  # USE: Failure log entry

        return {"status": "failed", "error": str(e)}
# =========== FUNCTION ===========