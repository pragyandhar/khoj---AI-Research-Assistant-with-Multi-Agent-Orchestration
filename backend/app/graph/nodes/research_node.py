# WHAT DOES THIS FILE DO: Defines the research node function with specialist agent routing and tenacity-based retry logic for web searching inside LangGraph.

# ================== IMPORTS ==================
from tenacity import retry, stop_after_attempt, wait_exponential

from app.graph.state import GraphState
from app.agents.base_agent import BaseAgent
from app.agents.research_agent import ResearchAgent
from app.agents.science_agent import ScienceResearchAgent
from app.agents.technology_agent import TechnologyResearchAgent
from app.core.logging import get_logger
from app.db.base import async_session_factory
from app.repositories.memory_repository import UserMemoryRepository
from app.services.memory_service import MemoryService
from app.tools.rag_retriever import rag_search
# ================== IMPORTS ==================


# =========== VARIABLES : Research Node Loggers ===========
logger = get_logger(__name__)               # USE: Research node execution logger instance
# =========== VARIABLES : Research Node Loggers ===========


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
async def _execute_research(research_agent: BaseAgent, query: str, topic: str, retrieved_context: str, memory_context: str) -> str:
    """ Calls the research agent with query, topic, and RAG/memory context. """

    # FLOW-1: Run the research agent
    output = await research_agent.run(
        query=query,
        topic=topic,
        retrieved_context=retrieved_context,
        memory_context=memory_context,
    )                                           # USE: Run react agent with prior-research and preference context

    return output
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Fetches a short summary of the user's past research, tolerating DB/store failures.
async def _get_memory_context(user_id: str) -> str:
    """ Opens a short-lived DB session to read the user's recent research topics. """

    try:
        async with async_session_factory() as db_session:
            memory_service = MemoryService(UserMemoryRepository(db_session))  # USE: Postgres-only memory service (no LangGraph store needed here)

            return await memory_service.get_user_context(user_id)

    except Exception as e:
        logger.error("memory_context_fetch_failed", user_id=user_id, error=str(e))  # USE: Non-fatal — research proceeds without memory context
        return ""
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Records the completed query as part of the user's long-term topic history.
async def _save_research_preference(user_id: str, query: str, topic: str) -> None:
    """ Opens a short-lived DB session to persist this query into the user's memory. """

    try:
        async with async_session_factory() as db_session:
            memory_service = MemoryService(UserMemoryRepository(db_session))  # USE: Postgres-only memory service (no LangGraph store needed here)

            await memory_service.save_research_preference(user_id, query, topic)

    except Exception as e:
        logger.error("research_preference_save_failed", user_id=user_id, error=str(e))  # USE: Non-fatal — a save failure must not fail the research node
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Research node executing facts gathering via the topic-appropriate specialist agent.
async def research_node(state: GraphState) -> dict:
    """ Conducts topic web search research using the selected specialist agent. """

    # FLOW-1: Select the specialist agent class based on router's classification.
    # Built here (not module-level) so the class names resolve dynamically each call —
    # this keeps unit tests able to patch e.g. app.graph.nodes.research_node.ResearchAgent.
    agent_map = {
        "science": ScienceResearchAgent,
        "technology": TechnologyResearchAgent,
        "general": ResearchAgent,
    }                                            # USE: Maps selected_agent key to its specialist agent class
    selected_agent = state.get("selected_agent", "general")  # USE: Agent key chosen by router_node
    AgentClass = agent_map.get(selected_agent, ResearchAgent)  # USE: Fall back to general researcher on unknown key
    research_agent = AgentClass()               # USE: Instantiate the chosen specialist agent

    logger.info("research_node_started", selected_agent=selected_agent, topic=state["topic"])  # USE: Node audit logging

    # FLOW-2: Check past research via RAG, and pull the user's long-term context if identified.
    # rag_search degrades gracefully on its own (ChromaDB down -> fallback string), so it is
    # called directly here rather than through the agent's tool-calling loop.
    retrieved_context = await rag_search.ainvoke({"query": state["query"], "topic": state["topic"]})  # USE: Direct tool call, not an agent invocation

    user_id = state.get("user_id")
    memory_context = await _get_memory_context(user_id) if user_id else ""  # USE: Cross-session preferences, if a user is identified

    # FLOW-3: Run research react agent with retry logic using helper function
    try:
        research_output = await _execute_research(
            research_agent,
            state["query"],
            state["topic"],
            retrieved_context,
            memory_context,
        )                                       # USE: Trigger research with tenacity retries

        # FLOW-4: Log research completed status and return partial state update
        logger.info(
            "research_node_completed",
            selected_agent=selected_agent,
            topic=state["topic"],
            output_length=len(research_output)
        )                                       # USE: Node audit logging

        if user_id:
            await _save_research_preference(user_id, state["query"], state["topic"])  # USE: Remember this query for future sessions

        return {
            "research_output": research_output,
            "status": "summarizing",
            "retrieved_context": retrieved_context,
            "memory_context": memory_context,
        }

    except Exception as e:
        # FLOW-5: Handle exceptions and return failure status with error details
        logger.error("research_node_failed", selected_agent=selected_agent, query=state["query"], error=str(e))  # USE: Failure log entry

        return {"status": "failed", "error": str(e), "retrieved_context": retrieved_context, "memory_context": memory_context}
# =========== FUNCTION ===========