# WHAT DOES THIS FILE DO: Defines the CacheService to cache and retrieve validated structured research reports.

# ================== IMPORTS ==================
import hashlib
import json
from typing import Optional

from redis.asyncio import Redis

from app.models.report import StructuredReport
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Service providing caching layer on top of Redis for StructuredReport schemas.
class CacheService:
    """ Service to cache and retrieve validated structured research reports. """


    # =========== FUNCTION ===========
    # ROLE: Initialize CacheService with redis client and ttl config.
    def __init__(self, redis_client: Redis, ttl: int = 3600):
        """ Setup the cache service client and time-to-live settings. """
        
        # FLOW-1: Assign client connection and default TTL
        self.redis_client = redis_client        # USE: Store active redis connection pool reference
        self.ttl = ttl                          # USE: Store TTL config value (default 1 hour)
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Generate deterministic MD5 cache key from user query.
    def _make_key(self, query: str) -> str:
        """ Normalizes and hashes the user query to build a secure cache key. """
        
        # FLOW-1: Clean query text and calculate hash value
        normalized = query.lower().strip()       # USE: Lowercase and strip whitespace
        query_hash = hashlib.md5(normalized.encode("utf-8")).hexdigest()  # USE: MD5 hash calculation
        
        # FLOW-2: Format cache key prefix
        return f"research_cache:{query_hash}"
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Retrieve cached StructuredReport for a given query if it exists.
    async def get(self, query: str) -> Optional[StructuredReport]:
        """ Fetches key from redis, deserializes data, and validates report schema. """
        
        # FLOW-1: Generate cache key for query
        key = self._make_key(query)             # USE: Get key string
        
        # FLOW-2: Retrieve cached data from redis database
        try:
            data = await self.redis_client.get(key)  # USE: Call async redis get
            
            if not data:
                return None
                
            # FLOW-3: Parse cached json and validate against StructuredReport model schema
            raw_data = json.loads(data)         # USE: Decode json string to dictionary
            
            return StructuredReport.model_validate(raw_data)  # USE: Model validation
            
        except Exception:
            return None
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Store serialized StructuredReport in redis with time-to-live expiration.
    async def set(self, query: str, report: StructuredReport) -> None:
        """ Serializes and saves structured report to cache. """
        
        # FLOW-1: Generate cache key for query
        key = self._make_key(query)             # USE: Get key string
        
        # FLOW-2: Serialize model schema to json and save to redis with expiration
        try:
            serialized = report.model_dump_json()  # USE: Dump schema to raw json string
            await self.redis_client.setex(key, self.ttl, serialized)  # USE: Async setex with TTL
            
        except Exception:
            pass
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Invalidate/delete cache entry for a given query.
    async def invalidate(self, query: str) -> None:
        """ Removes query cache entry from redis database. """
        
        # FLOW-1: Generate cache key and delete it
        key = self._make_key(query)             # USE: Get key string
        
        try:
            await self.redis_client.delete(key)  # USE: Call async redis delete key
            
        except Exception:
            pass
    # =========== FUNCTION ===========
# =========== CLASS ===========