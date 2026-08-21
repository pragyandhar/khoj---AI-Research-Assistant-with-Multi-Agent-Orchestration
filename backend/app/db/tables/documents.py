# WHAT DOES THIS FILE DO: Defines the SQLAlchemy ORM model tracking ChromaDB document chunk metadata in PostgreSQL.

# ================== IMPORTS ==================
from datetime import datetime
import uuid

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Database model tracking a single indexed report chunk's ChromaDB reference.
class ResearchDocument(Base):
    """ SQLAlchemy model syncing ChromaDB document chunks with their session/report origin. """

    # FLOW-1: Set up table name and columns
    __tablename__ = "research_documents"        # USE: Postgres table name for indexed report chunk metadata

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)  # USE: Primary database ID key
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.session_id"), index=True, nullable=False)  # USE: Originating session's ID
    chroma_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)  # USE: Matching document ID in ChromaDB
    chunk_index: Mapped[int] = mapped_column(nullable=False)  # USE: Position of this chunk within its source report
    content_preview: Mapped[str] = mapped_column(String(500))  # USE: First 500 chars of the chunk, for debugging
    topic: Mapped[str] = mapped_column(String(50), index=True)  # USE: Report topic, for filtered lookups
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)  # USE: Record creation timestamp
# =========== CLASS ===========
