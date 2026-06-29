# WHAT DOES THIS FILE DO: Configures SQLAlchemy async engine, session factory, and base declarative model.

# ================== IMPORTS ==================
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Declarative base class for all SQLAlchemy ORM models.
class Base(DeclarativeBase):
    """ Base class for database models to inherit from. """
    pass
# =========== CLASS ===========


# =========== VARIABLES : Database connection engines and session factories ===========
# FLOW-1: Set up engine with connection pool parameters
engine = create_async_engine(
    settings.DATABASE_URL,                      # USE: Target DB URL to connect
    echo=settings.ENVIRONMENT == "development", # USE: Log SQL commands only in development mode
    pool_size=10,                               # USE: Size of connection pool to keep active
    max_overflow=20,                            # USE: Temporary pool expansion limit
    pool_pre_ping=True,                          # USE: Check connections for health before usage
)

# FLOW-2: Setup async session maker using the engine
async_session_factory = async_sessionmaker(
    engine,                                     # USE: Async database engine to bind
    class_=AsyncSession,                        # USE: SQLAlchemy async session type
    expire_on_commit=False,                     # USE: Retain object attribute values after commit
)
# =========== VARIABLES : Database connection engines and session factories ===========


# =========== FUNCTION ===========
# ROLE: Creates all defined database tables during startup.
async def create_all_tables():
    """ Run DDL generation sync handler on the database. """
    
    # FLOW-1: Begin engine transaction context and run metadata creation
    async with engine.begin() as conn:          # USE: Acquire database transaction connection
        await conn.run_sync(Base.metadata.create_all)  # USE: Run DDL schema creation in sync worker
# =========== FUNCTION ===========