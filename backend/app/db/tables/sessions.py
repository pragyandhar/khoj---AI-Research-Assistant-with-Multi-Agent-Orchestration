# WHAT DOES THIS FILE DO: Defines the SQLAlchemy ORM model for storing research session details and graph checkpoints.

# ================== IMPORTS ==================
from datetime import datetime
import uuid

from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Database model representing user research session table.
class Session(Base):
    """ SQLAlchemy model for session storage and time-travel tracking. """

    # FLOW-1: Set up table name and columns
    __tablename__ = "sessions"                  # USE: Postgres table name for sessions

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)  # USE: Primary database ID key
    session_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)  # USE: Logical session identifier
    user_ip: Mapped[str] = mapped_column(String(45), nullable=True)  # USE: Client IP address for rate limits checking
    graph_state: Mapped[dict] = mapped_column(JSON, nullable=True)  # USE: Current execution state of the langgraph state machine
    checkpoint_data: Mapped[dict] = mapped_column(JSON, nullable=True)  # USE: Saved checkpoint for time travel feature
    status: Mapped[str] = mapped_column(String(20), default="pending")  # USE: Overall research state (e.g. completed, failed)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)  # USE: Record creation timestamp
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)  # USE: Record modification timestamp

    # FLOW-2: Define relationship to associated reports
    reports: Mapped[list["Report"]] = relationship("Report", back_populates="session")  # USE: One to many relationship mapping
# =========== CLASS ===========