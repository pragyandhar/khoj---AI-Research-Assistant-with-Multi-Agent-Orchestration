# WHAT DOES THIS FILE DO: Sets up and configures the PostgreSQL checkpointer for LangGraph persistent workflows.

# ================== IMPORTS ==================
from contextlib import AsyncExitStack

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.config import settings
# ================== IMPORTS ==================


# =========== FUNCTION ===========
# ROLE: Setup and configure the PostgreSQL checkpointer instance, ensuring required tables exist.
async def setup_checkpointer(exit_stack: AsyncExitStack) -> AsyncPostgresSaver:
    """ Initialize AsyncPostgresSaver with correct connection string format.

    AsyncPostgresSaver.from_conn_string() is an @asynccontextmanager, not a plain
    constructor — it must be entered to get a real saver, and its connection closes
    the moment that context exits. `exit_stack` (owned by the app's lifespan) is
    entered here instead of a bare `async with`, so the connection stays open for
    the process lifetime and is closed automatically on shutdown.
    """

    # FLOW-1: Get the connection string and convert asyncpg driver to standard PostgreSQL driver
    conn_string = settings.DATABASE_URL
    if conn_string.startswith("postgresql+asyncpg://"):
        conn_string = conn_string.replace("postgresql+asyncpg://", "postgresql://")  # USE: Replace asyncpg driver

    # FLOW-2: Enter the checkpointer's async context via the shared exit stack
    checkpointer = await exit_stack.enter_async_context(
        AsyncPostgresSaver.from_conn_string(conn_string)
    )                                             # USE: Obtain the real saver instance with its connection held open

    # FLOW-3: Create tables automatically if they do not exist
    await checkpointer.setup()                  # USE: Create tables in database schema

    return checkpointer
# =========== FUNCTION ===========