# WHAT DOES THIS FILE DO: Defines the SQLAlchemy ORM model for cross-session, long-term user memory records.

# ================== IMPORTS ==================
from datetime import datetime
import uuid

from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Database model representing a single long-term memory record for a user.
class UserMemory(Base):
    """ SQLAlchemy model for cross-session user preferences and research history. """

    # FLOW-1: Set up table name and columns
    __tablename__ = "user_memories"             # USE: Postgres table name for long-term user memories

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)  # USE: Primary database ID key
    user_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)  # USE: Owning user's identifier
    memory_type: Mapped[str] = mapped_column(String(50), nullable=False)  # USE: "preference" | "topic_history" | "research_style"
    content: Mapped[dict] = mapped_column(JSON, nullable=False)  # USE: Actual memory payload
    embedding_id: Mapped[str] = mapped_column(String(100), nullable=True)  # USE: Corresponding ChromaDB vector ID, if indexed
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)  # USE: Record creation timestamp
    last_accessed: Mapped[datetime] = mapped_column(default=datetime.utcnow)  # USE: Used to identify stale memories for cleanup
# =========== CLASS ===========
