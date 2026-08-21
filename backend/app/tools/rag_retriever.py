# WHAT DOES THIS FILE DO: Provides a ChromaDB-backed tool for retrieving relevant past research before a fresh web search.

# ================== IMPORTS ==================
import asyncio

import chromadb
from langchain_core.tools import tool

from app.core.config import settings
from app.core.logging import get_logger
# ================== IMPORTS ==================


# =========== VARIABLES : ChromaDB collection name and logger ===========
logger = get_logger(__name__)
COLLECTION_NAME = "research_documents"      # USE: Shared ChromaDB collection name for indexed report chunks
# =========== VARIABLES : ChromaDB collection name and logger ===========


# =========== CLASS ===========
# ROLE: Presents a uniform async query()/add() interface over a chromadb collection,
# regardless of whether the underlying client is the sync PersistentClient (dev) or the
# native async AsyncHttpClient (prod) — callers never need to know which mode is active.
class _AsyncCollectionWrapper:
    """ Wraps a chromadb collection so callers always await query()/add(). """

    def __init__(self, collection, is_async: bool):
        """ Store the underlying collection and whether it is natively async. """
        self._collection = collection           # USE: Underlying chromadb collection object
        self._is_async = is_async               # USE: Whether the collection's methods are already coroutines


    async def query(self, **kwargs):
        """ Run a similarity query, off-loading sync PersistentClient calls to a thread. """

        if self._is_async:
            return await self._collection.query(**kwargs)  # USE: Native async query call

        return await asyncio.to_thread(self._collection.query, **kwargs)  # USE: Run sync query without blocking the event loop


    async def add(self, **kwargs):
        """ Add documents, off-loading sync PersistentClient calls to a thread. """

        if self._is_async:
            return await self._collection.add(**kwargs)  # USE: Native async add call

        return await asyncio.to_thread(self._collection.add, **kwargs)  # USE: Run sync add without blocking the event loop


    async def count(self) -> int:
        """ Returns the number of documents currently stored in the collection. """

        if self._is_async:
            return await self._collection.count()  # USE: Native async count call

        return await asyncio.to_thread(self._collection.count)  # USE: Run sync count without blocking the event loop
# =========== CLASS ===========


# =========== CLASS ===========
# ROLE: Process-wide singleton lazily holding the ChromaDB client connection.
class ChromaDBClient:
    """ Singleton over a persistent local client (dev) or an HTTP client (prod). """

    _instance = None                            # USE: Shared singleton instance holder


    # =========== FUNCTION ===========
    # ROLE: Ensure only one ChromaDBClient instance exists per process.
    def __new__(cls):
        """ Return the existing singleton instance, creating it on first use. """

        if cls._instance is None:
            instance = super().__new__(cls)
            instance.client = None              # USE: Lazily created underlying chromadb client
            instance.is_async = False           # USE: Whether `client` exposes native async methods
            cls._instance = instance

        return cls._instance
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Lazily create (once) and return the underlying chromadb client for this process.
    async def get_client(self):
        """ Connects to a ChromaDB server if CHROMA_HOST is set, else uses a local persistent store. """

        if self.client is not None:
            return self.client                  # USE: Reuse the already-connected client

        if settings.CHROMA_HOST:
            # FLOW-1: Production — connect to a standalone ChromaDB server
            self.client = await chromadb.AsyncHttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)  # USE: Async HTTP client
            self.is_async = True
        else:
            # FLOW-2: Development — persist vectors to a local on-disk store
            self.client = await asyncio.to_thread(chromadb.PersistentClient, path=settings.CHROMA_PERSIST_PATH)  # USE: Sync persistent client, off the event loop
            self.is_async = False

        return self.client
    # =========== FUNCTION ===========
# =========== CLASS ===========


# =========== FUNCTION ===========
# ROLE: Returns the shared research_documents collection, creating it if it does not exist.
async def get_chroma_collection() -> _AsyncCollectionWrapper:
    """ Fetches (or creates) the research_documents collection, wrapped for uniform async access. """

    # FLOW-1: Get the process-wide client and resolve the collection through it
    chroma = ChromaDBClient()                   # USE: Shared singleton instance
    client = await chroma.get_client()          # USE: Underlying persistent or HTTP client

    if chroma.is_async:
        collection = await client.get_or_create_collection(COLLECTION_NAME)  # USE: Native async collection lookup
    else:
        collection = await asyncio.to_thread(client.get_or_create_collection, COLLECTION_NAME)  # USE: Sync lookup, off the event loop

    return _AsyncCollectionWrapper(collection, chroma.is_async)
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Searches past indexed research for content relevant to the current query.
@tool
async def rag_search(query: str, topic: str = "") -> str:
    """ Search past research sessions for relevant information before doing web search.

    Args:
        query: The research question to find semantically similar past findings for.
        topic: Optional topic filter (e.g. "science", "technology") to narrow results.

    Returns:
        A formatted string of past research excerpts, or a message indicating none were found.
    """

    # FLOW-1: Query ChromaDB for semantically similar past research chunks
    try:
        collection = await get_chroma_collection()  # USE: Shared collection handle

        results = await collection.query(
            query_texts=[query],
            n_results=5,
            where={"topic": topic} if topic else None,
        )                                       # USE: Semantic similarity search, optionally topic-filtered

        documents = (results.get("documents") or [[]])[0]  # USE: Matched chunk texts for this query
        metadatas = (results.get("metadatas") or [[]])[0]  # USE: Matched chunk metadata for this query

        # FLOW-2: No matches means the agent should fall back to a fresh web search
        if not documents:
            return "No relevant past research found."

        # FLOW-3: Format matches so the agent can clearly tell this is past, not live, data
        formatted_results = []
        for content, metadata in zip(documents, metadatas):
            date = (metadata or {}).get("created_at", "unknown date")  # USE: Chunk's indexed timestamp
            formatted_results.append(f"[Past Research - {date}]: {content}")

        return "\n".join(formatted_results)

    except Exception as e:
        # FLOW-4: Graceful degradation — ChromaDB being unavailable should never block research
        logger.error("rag_search_failed", query=query, topic=topic, error=str(e))  # USE: Log the underlying failure
        return "RAG unavailable, proceeding with web search."
# =========== FUNCTION ===========
