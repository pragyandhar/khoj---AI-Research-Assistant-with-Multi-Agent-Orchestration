# WHAT DOES THIS FILE DO: Handles specific database transactions and queries for the sessions table.

# ================== IMPORTS ==================
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DatabaseException
from app.db.tables.sessions import Session
from app.repositories.base import BaseRepository
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Repository handling database query operations for Session table.
class SessionRepository(BaseRepository[Session]):
    """ Repository subclass managing SQL transactions on user sessions. """


    # =========== FUNCTION ===========
    # ROLE: Initialize session repository and bind the Session model.
    def __init__(self, session: AsyncSession):
        """ Initialize repository with session and target table model. """
        
        # FLOW-1: Call parent class constructor with Session model type
        super().__init__(session, Session)      # USE: Inherited initialization
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Retrieve a Session record by its unique session_id string.
    async def get_by_session_id(self, session_id: str) -> Session | None:
        """ Fetch a single session using the unique string key. """
        
        # FLOW-1: Query table using select filters on session_id
        try:
            stmt = select(Session).where(Session.session_id == session_id)  # USE: Select query target statement
            result = await self.session.execute(stmt)  # USE: Query runner call
            session_obj = result.scalars().first()  # USE: Extract matching object from response
            
            return session_obj
            
        except Exception as e:
            raise DatabaseException(str(e))     # USE: Wrap generic error to DatabaseException
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Update the execution state checkpoint dictionary for a session.
    async def update_graph_state(self, session_id: str, state: dict) -> Session | None:
        """ Update graph state payload for the designated session ID. """
        
        # FLOW-1: Retrieve existing model record
        try:
            db_session = await self.get_by_session_id(session_id)  # USE: Fetch current record reference
            
            if not db_session:
                return None
                
            # FLOW-2: Modify graph state and update timestamps
            db_session.graph_state = state      # USE: Update checkpoint state dict
            db_session.updated_at = datetime.utcnow()  # USE: Force update modified date timestamp
            await self.session.commit()         # USE: Save modifications to DB
            await self.session.refresh(db_session)  # USE: Load updated data back from DB
            
            return db_session
            
        except Exception as e:
            raise DatabaseException(str(e))     # USE: Exception translator
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Update only status field directly without loading the model first.
    async def update_status(self, session_id: str, status: str) -> None:
        """ Execute direct SQL UPDATE statement for session status column. """
        
        # FLOW-1: Prepare dynamic update query targeting status column
        try:
            stmt = (
                update(Session)
                .where(Session.session_id == session_id)
                .values(status=status, updated_at=datetime.utcnow())
            )                                   # USE: SQL update builder
            await self.session.execute(stmt)    # USE: Direct database statement execution
            await self.session.commit()         # USE: Save update changes to DB
            
        except Exception as e:
            raise DatabaseException(str(e))     # USE: Custom exceptions translation
    # =========== FUNCTION ===========
# =========== CLASS ===========