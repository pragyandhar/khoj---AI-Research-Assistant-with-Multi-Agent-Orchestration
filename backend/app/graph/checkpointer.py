# WHAT DOES THIS FILE DO: Sets up and configures the PostgreSQL checkpointer for LangGraph persistent workflows.

# ================== IMPORTS ==================
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.config import settings
# ================== IMPORTS ==================


# =========== FUNCTION ===========
# ROLE: Setup and configure the PostgreSQL checkpointer instance, ensuring required tables exist.
async def setup_checkpointer() -> AsyncPostgresSaver:
    """ Initialize AsyncPostgresSaver with correct connection string format. """
    
    # FLOW-1: Get the connection string and convert asyncpg driver to standard PostgreSQL driver
    conn_string = settings.DATABASE_URL
    if conn_string.startswith("postgresql+asyncpg://"):
        conn_string = conn_string.replace("postgresql+asyncpg://", "postgresql://")  # USE: Replace asyncpg driver
        
    # FLOW-2: Create AsyncPostgresSaver instance using connection pool under the hood
    checkpointer = AsyncPostgresSaver.from_conn_string(conn_string)  # USE: Connect using plain postgresql URI
    
    # FLOW-3: Create tables automatically if they do not exist
    await checkpointer.setup()                  # USE: Create tables in database schema
    
    return checkpointer
# =========== FUNCTION ===========