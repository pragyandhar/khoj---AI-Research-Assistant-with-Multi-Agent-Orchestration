# WHAT DOES THIS FILE DO: Chunks completed research reports and indexes them into ChromaDB for future RAG retrieval.

# ================== IMPORTS ==================
from app.core.logging import get_logger
from app.db.tables.documents import ResearchDocument
from app.models.report import StructuredReport
from app.repositories.document_repository import DocumentRepository
# ================== IMPORTS ==================


# =========== VARIABLES : Embedding Service Logger ===========
logger = get_logger(__name__)               # USE: Embedding service execution logger instance
# =========== VARIABLES : Embedding Service Logger ===========


# =========== CLASS ===========
# ROLE: Service splitting research reports into chunks and indexing them into ChromaDB.
class EmbeddingService:
    """ Indexes completed research reports into ChromaDB, chunk by chunk. """


    # =========== FUNCTION ===========
    # ROLE: Initialize EmbeddingService with its ChromaDB collection and document repository.
    def __init__(self, chroma_collection, document_repository: DocumentRepository):
        """ Store the ChromaDB collection handle and Postgres metadata repository. """

        # FLOW-1: Assign chroma collection and repository dependencies
        self.chroma_collection = chroma_collection  # USE: Async collection wrapper from rag_retriever.get_chroma_collection()
        self.document_repo = document_repository  # USE: Repository syncing PostgreSQL metadata with ChromaDB
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Splits a structured report into meaningful, independently embeddable chunks.
    def _chunk_report(self, report: StructuredReport) -> list[str]:
        """ Turns each report section into one chunk — sections are naturally meaningful units. """

        # FLOW-1: Combine each section's heading and content into a single chunk
        return [f"{section.heading}\n\n{section.content}" for section in report.sections]  # USE: One chunk per section
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Chunks a report and indexes it into ChromaDB, syncing metadata to PostgreSQL.
    async def index_report(self, report: StructuredReport, session_id: str) -> None:
        """ Indexes a completed report's chunks into ChromaDB and records their metadata. """

        # FLOW-1: Chunk the report; nothing to index if it has no sections
        chunks = self._chunk_report(report)     # USE: List of per-section chunk texts

        if not chunks:
            return

        # FLOW-2: Build a stable, unique ChromaDB ID for each chunk
        chroma_ids = [f"{session_id}_chunk_{i}" for i in range(len(chunks))]  # USE: Deterministic per-chunk IDs

        # FLOW-3: Index chunks into ChromaDB and sync their metadata into PostgreSQL.
        # Indexing is best-effort — a ChromaDB hiccup must never fail an already-saved report.
        try:
            await self.chroma_collection.add(
                documents=chunks,
                ids=chroma_ids,
                metadatas=[
                    {
                        "session_id": session_id,
                        "topic": report.topic,
                        "chunk_index": i,
                        "created_at": report.generated_at.isoformat(),
                    }
                    for i in range(len(chunks))
                ],
            )                                   # USE: Store chunk vectors and metadata filters in ChromaDB

            for i, (chunk, chroma_id) in enumerate(zip(chunks, chroma_ids)):
                document = ResearchDocument(
                    session_id=session_id,
                    chroma_id=chroma_id,
                    chunk_index=i,
                    content_preview=chunk[:500],
                    topic=report.topic,
                )                               # USE: Mirror ChromaDB chunk as a Postgres metadata row
                await self.document_repo.create(document)

            logger.info("report_indexed", session_id=session_id, chunk_count=len(chunks))  # USE: Indexing success audit log

        except Exception as e:
            logger.error("report_indexing_failed", session_id=session_id, error=str(e))  # USE: Non-fatal indexing failure log
    # =========== FUNCTION ===========
# =========== CLASS ===========
