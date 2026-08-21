# WHAT DOES THIS FILE DO: Handles specific database transactions and queries for the research_documents table.

# ================== IMPORTS ==================
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.tables.documents import ResearchDocument
from app.repositories.base import BaseRepository
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Repository handling database query operations for the ResearchDocument table.
class DocumentRepository(BaseRepository[ResearchDocument]):
    """ Repository subclass managing SQL transactions on indexed report chunk metadata. """


    # =========== FUNCTION ===========
    # ROLE: Initialize repository and bind the ResearchDocument model automatically.
    def __init__(self, session: AsyncSession):
        """ Initialize repository with session and target table model. """

        # FLOW-1: Call parent class constructor with ResearchDocument model type
        super().__init__(session, ResearchDocument)  # USE: Parent constructor initialization
    # =========== FUNCTION ===========
# =========== CLASS ===========
