# WHAT DOES THIS FILE DO: Defines the SQLAlchemy ORM model for storing generated research reports.

# ================== IMPORTS ==================
from datetime import datetime
import uuid

from sqlalchemy import String, JSON, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Database model representing the generated research reports table.
class Report(Base):
    """ SQLAlchemy model for storing final research reports. """

    # FLOW-1: Set up table name and columns
    __tablename__ = "reports"                   # USE: Postgres table name for reports

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)  # USE: Primary database ID key
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.session_id"), index=True, nullable=False)  # USE: Associated session ID foreign key
    query: Mapped[str] = mapped_column(Text, nullable=False)  # USE: Original user search query string
    report_data: Mapped[dict] = mapped_column(JSON, nullable=True)  # USE: Structured report payload contents
    topic: Mapped[str] = mapped_column(String(50), nullable=True)  # USE: Classification topic name
    confidence_score: Mapped[float] = mapped_column(nullable=True)  # USE: Evaluated report accuracy score
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)  # USE: Record creation timestamp

    # FLOW-2: Define relationship back to sessions table
    session: Mapped["Session"] = relationship("Session", back_populates="reports")  # USE: Reference to parent session object
# =========== CLASS ===========