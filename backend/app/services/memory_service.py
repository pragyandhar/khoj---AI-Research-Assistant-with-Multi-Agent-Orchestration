# WHAT DOES THIS FILE DO: Manages cross-session user preferences and topic history, backed by Postgres and the LangGraph Store.

# ================== IMPORTS ==================
from app.core.logging import get_logger
from app.db.tables.memory import UserMemory
from app.repositories.memory_repository import UserMemoryRepository
# ================== IMPORTS ==================


# =========== VARIABLES : Memory Service Logger ===========
logger = get_logger(__name__)               # USE: Memory service execution logger instance
# =========== VARIABLES : Memory Service Logger ===========


# =========== CLASS ===========
# ROLE: Service managing a user's long-term research preferences across sessions.
class MemoryService:
    """ Reads and writes cross-session user memory via Postgres and the LangGraph Store. """


    # =========== FUNCTION ===========
    # ROLE: Initialize MemoryService with its Postgres repository and the LangGraph Store.
    def __init__(self, memory_repository: UserMemoryRepository, store=None):
        """ Store the user memory repository and LangGraph async store dependencies.

        `store` is optional: save_research_preference()/get_user_context() only need the
        Postgres-backed repository, while store_in_langgraph_store()/get_from_langgraph_store()
        need a real LangGraph store instance.
        """

        # FLOW-1: Assign repository and store dependencies
        self.memory_repo = memory_repository    # USE: PostgreSQL-backed UserMemory repository
        self.store = store                      # USE: LangGraph AsyncPostgresStore instance
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Records a completed research query as part of the user's topic history.
    async def save_research_preference(self, user_id: str, query: str, topic: str, feedback: str | None = None) -> None:
        """ Saves a topic_history memory record for a user's research query. """

        # FLOW-1: Build and persist the topic history memory record
        memory = UserMemory(
            user_id=user_id,
            memory_type="topic_history",
            content={"query": query, "topic": topic, "feedback": feedback},
        )                                       # USE: One research query as a memory record
        await self.memory_repo.create(memory)

        logger.info("research_preference_saved", user_id=user_id, topic=topic)  # USE: Audit log for saved preference
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Builds a readable summary of a user's recent research history for prompt injection.
    async def get_user_context(self, user_id: str) -> str:
        """ Returns a short readable string of the user's last 5 researched queries. """

        # FLOW-1: Fetch the user's most recent topic history memories
        memories = await self.memory_repo.get_recent_by_user(user_id, memory_type="topic_history", limit=5)  # USE: Last 5 topic_history records

        if not memories:
            return ""

        # FLOW-2: Extract the original queries and format them into one summary line
        queries = [memory.content.get("query") for memory in memories if memory.content.get("query")]  # USE: Prior research queries only

        if not queries:
            return ""

        return f"User has previously researched: {', '.join(queries)}"
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Writes a value into the LangGraph Store's native key-value interface.
    async def store_in_langgraph_store(self, user_id: str, key: str, value: dict) -> None:
        """ Puts a value into the LangGraph Store, namespaced per user. """

        # FLOW-1: Store the value under the user's memory namespace
        await self.store.aput(("memories", user_id), key, value)  # USE: LangGraph Store native write
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Reads a value back from the LangGraph Store's native key-value interface.
    async def get_from_langgraph_store(self, user_id: str, key: str) -> dict | None:
        """ Gets a value from the LangGraph Store, namespaced per user. """

        # FLOW-1: Retrieve the stored item and unwrap its value
        item = await self.store.aget(("memories", user_id), key)  # USE: LangGraph Store native read

        return item.value if item else None
    # =========== FUNCTION ===========
# =========== CLASS ===========
