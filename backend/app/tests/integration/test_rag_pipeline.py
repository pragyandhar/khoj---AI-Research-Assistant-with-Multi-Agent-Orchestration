# WHAT DOES THIS FILE DO: Integration tests for ChromaDB report indexing, RAG retrieval, and long-term memory persistence.

# ================== IMPORTS ==================
import pytest

from app.models.report import StructuredReport, ReportSection
from app.repositories.document_repository import DocumentRepository
from app.repositories.memory_repository import UserMemoryRepository
from app.services.embedding_service import EmbeddingService
from app.services.memory_service import MemoryService
from app.tools import rag_retriever
# ================== IMPORTS ==================


# =========== FUNCTION ===========
# ROLE: Provides a ChromaDB collection isolated to a fresh temp directory per test.
@pytest.fixture
async def chroma_test_collection(tmp_path, monkeypatch):
    """ Points ChromaDBClient at a temp directory and resets its singleton around the test,
    so each test gets an empty collection instead of sharing the dev ./chroma_db store. """

    # FLOW-1: Redirect the persistent client path and force a fresh singleton
    monkeypatch.setattr(rag_retriever.settings, "CHROMA_PERSIST_PATH", str(tmp_path / "chroma_test"))
    rag_retriever.ChromaDBClient._instance = None  # USE: Force get_chroma_collection() to build a client bound to tmp_path

    collection = await rag_retriever.get_chroma_collection()  # USE: Fresh, empty collection for this test

    yield collection

    # FLOW-2: Reset the singleton so later tests/processes don't inherit this temp client
    rag_retriever.ChromaDBClient._instance = None
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Builds a StructuredReport with a given number of sections for indexing tests.
def _build_report(topic: str, section_count: int = 3) -> StructuredReport:
    """ Constructs a valid StructuredReport with the requested number of sections. """

    sections = [
        ReportSection(
            heading=f"Section {i}",
            content=f"This is the detailed content for section {i} of the {topic} report, long enough to pass validation.",
            citations=[],
        )
        for i in range(1, section_count + 1)
    ]                                            # USE: One section per requested chunk

    return StructuredReport(
        title=f"{topic.title()} Report",
        summary=f"A short summary of the {topic} report.",
        sections=sections,
        topic=topic,
        confidence_score=0.9,
        total_sources=0,
    )
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Verifies indexing a report creates one ChromaDB chunk per report section.
@pytest.mark.asyncio
async def test_report_indexing_creates_chunks(test_db, chroma_test_collection):
    """ Verifies EmbeddingService.index_report() creates one chunk per section in ChromaDB. """

    # FLOW-1: Index a 3-section report and verify the collection now holds 3 documents
    report = _build_report("science", section_count=3)
    embedding_service = EmbeddingService(chroma_test_collection, DocumentRepository(test_db))

    await embedding_service.index_report(report, session_id="session-1")

    assert await chroma_test_collection.count() == 3
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Verifies rag_search finds content from a previously indexed report.
@pytest.mark.asyncio
async def test_rag_search_returns_relevant_results(test_db, chroma_test_collection, monkeypatch):
    """ Verifies a search for an indexed report's topic returns its chunk content. """

    # FLOW-1: Index a report, then search for the same subject matter
    report = _build_report("science", section_count=2)
    embedding_service = EmbeddingService(chroma_test_collection, DocumentRepository(test_db))
    await embedding_service.index_report(report, session_id="session-1")

    # FLOW-2: Point rag_search's own collection lookup at this same temp collection
    async def _fake_get_chroma_collection():
        return chroma_test_collection

    monkeypatch.setattr(rag_retriever, "get_chroma_collection", _fake_get_chroma_collection)

    result = await rag_retriever.rag_search.ainvoke({"query": "Section 1 detailed content", "topic": "science"})

    assert "Section 1" in result
    assert "Past Research" in result
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Verifies rag_search's topic filter excludes chunks from other topics.
@pytest.mark.asyncio
async def test_rag_search_filters_by_topic(test_db, chroma_test_collection, monkeypatch):
    """ Verifies a topic-filtered search only returns chunks indexed under that topic. """

    # FLOW-1: Index one science report and one technology report
    embedding_service = EmbeddingService(chroma_test_collection, DocumentRepository(test_db))
    await embedding_service.index_report(_build_report("science", section_count=1), session_id="session-science")
    await embedding_service.index_report(_build_report("technology", section_count=1), session_id="session-tech")

    async def _fake_get_chroma_collection():
        return chroma_test_collection

    monkeypatch.setattr(rag_retriever, "get_chroma_collection", _fake_get_chroma_collection)

    # FLOW-2: Search filtered to topic="science" should never surface the technology chunk
    result = await rag_retriever.rag_search.ainvoke({"query": "Section 1 detailed content", "topic": "science"})

    assert "science" in result.lower()
    assert "technology report" not in result.lower()
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Verifies MemoryService persists and retrieves a user's research history.
@pytest.mark.asyncio
async def test_memory_service_saves_and_retrieves(test_db):
    """ Verifies save_research_preference() output is reflected in get_user_context(). """

    # FLOW-1: Save a research preference and read it back as user context
    memory_service = MemoryService(UserMemoryRepository(test_db))

    await memory_service.save_research_preference(user_id="user-1", query="quantum computing basics", topic="science")

    context = await memory_service.get_user_context("user-1")

    assert "quantum computing basics" in context
# =========== FUNCTION ===========
