# WHAT DOES THIS FILE DO: Defines FastAPI dependencies for database, cache, and authentication.

# ================== IMPORTS ==================
from typing import Annotated
from fastapi import Depends, Header, HTTPException
from redis.asyncio import Redis
import redis.asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import async_session_factory
# ================== IMPORTS ==================


# =========== FUNCTION ===========
# ROLE: Yields an active async database session and closes it afterwards.
async def get_db_session():
    """ Async generator for database sessions. """
    
    # FLOW-1: Initialize a session and yield it
    session = async_session_factory()           # USE: Create database session instance
    
    try:
        yield session
        
    finally:
        # FLOW-2: Ensure session is closed even if exception occurs
        await session.close()                   # USE: Close session to release connection
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Creates and returns a Redis async client.
def get_cache():
    """ Returns a redis async client instance. """
    
    # FLOW-1: Instantiate redis connection from setting URL
    return redis.asyncio.from_url(settings.REDIS_URL, decode_responses=True)  # USE: Create redis connection pool
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Authenticates request by validating the Authorization header.
async def get_current_api_key(authorization: str = Header()):
    """ Validates custom Authorization key header. """
    
    # FLOW-1: Validate incoming token against stored API key
    if authorization != settings.API_SECRET_KEY:  # USE: Check matching keys
        raise HTTPException(status_code=401, detail="Invalid API Key")
        
    return authorization
# =========== FUNCTION ===========


# =========== VARIABLES : Dependency injection Annotated types ===========
DBSession = Annotated[AsyncSession, Depends(get_db_session)]
Cache = Annotated[Redis, Depends(get_cache)]
AuthKey = Annotated[str, Depends(get_current_api_key)]
# =========== VARIABLES : Dependency injection Annotated types ===========