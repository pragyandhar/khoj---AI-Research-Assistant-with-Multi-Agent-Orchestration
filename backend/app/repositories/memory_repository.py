# WHAT DOES THIS FILE DO: Handles specific database transactions and queries for the user_memories table.

# ================== IMPORTS ==================
from datetime import datetime
import uuid

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DatabaseException
from app.db.tables.memory import UserMemory
from app.repositories.base import BaseRepository
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Repository handling database query operations for the UserMemory table.
class UserMemoryRepository(BaseRepository[UserMemory]):
    """ Repository subclass managing SQL transactions on long-term user memories. """


    # =========== FUNCTION ===========
    # ROLE: Initialize repository and bind the UserMemory model automatically.
    def __init__(self, session: AsyncSession):
        """ Initialize repository with session and target table model. """

        # FLOW-1: Call parent class constructor with UserMemory model type
        super().__init__(session, UserMemory)   # USE: Parent constructor initialization
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Retrieve a user's most recently accessed memories of a given type.
    async def get_recent_by_user(self, user_id: str, memory_type: str, limit: int = 5) -> list[UserMemory]:
        """ Fetch the most recently accessed memories for a user, filtered by type. """

        # FLOW-1: Build and execute select query ordered by last_accessed descending
        try:
            stmt = (
                select(UserMemory)
                .where(UserMemory.user_id == user_id, UserMemory.memory_type == memory_type)
                .order_by(UserMemory.last_accessed.desc())
                .limit(limit)
            )                                   # USE: Ordered, limited SELECT statement
            result = await self.session.execute(stmt)  # USE: Async query runner execution

            return list(result.scalars().all())  # USE: Extract all matching memory records

        except Exception as e:
            raise DatabaseException(str(e))     # USE: Wrap generic error to DatabaseException
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Refresh a memory's last_accessed timestamp when it is read.
    async def update_last_accessed(self, memory_id: uuid.UUID) -> None:
        """ Marks a memory record as just-accessed, keeping it eligible to survive cleanup. """

        # FLOW-1: Retrieve the memory record and bump its last_accessed timestamp
        try:
            memory = await self.get_by_id(memory_id)  # USE: Fetch target memory record

            if not memory:
                return

            memory.last_accessed = datetime.utcnow()  # USE: Refresh access timestamp
            await self.session.commit()         # USE: Save the timestamp update

        except Exception as e:
            raise DatabaseException(str(e))     # USE: Wrap generic error to DatabaseException
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Deletes a user's oldest memories beyond a retention cap, to bound table growth.
    async def cleanup_old_memories(self, user_id: str, keep_last: int = 50) -> int:
        """ Deletes the oldest memories past keep_last, returning how many were removed. """

        # FLOW-1: Find the IDs of memories to keep — the most recently accessed keep_last rows
        try:
            keep_stmt = (
                select(UserMemory.id)
                .where(UserMemory.user_id == user_id)
                .order_by(UserMemory.last_accessed.desc())
                .limit(keep_last)
            )                                   # USE: IDs of memories within the retention cap
            keep_result = await self.session.execute(keep_stmt)
            keep_ids = [row[0] for row in keep_result.all()]  # USE: Flatten scalar ID rows

            # FLOW-2: Delete every memory for this user NOT in the keep set
            delete_stmt = delete(UserMemory).where(
                UserMemory.user_id == user_id,
                UserMemory.id.notin_(keep_ids),
            )                                   # USE: Deletes everything past the retention cap
            delete_result = await self.session.execute(delete_stmt)
            await self.session.commit()         # USE: Save deletions to DB

            return delete_result.rowcount or 0

        except Exception as e:
            raise DatabaseException(str(e))     # USE: Wrap generic error to DatabaseException
    # =========== FUNCTION ===========
# =========== CLASS ===========
