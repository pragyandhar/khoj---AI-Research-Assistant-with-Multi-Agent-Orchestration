# WHAT DOES THIS FILE DO: Handles specific database transactions and queries for the reports table.

# ================== IMPORTS ==================
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DatabaseException
from app.db.tables.reports import Report
from app.repositories.base import BaseRepository
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Repository handling database query operations for the Report table.
class ReportRepository(BaseRepository[Report]):
    """ Repository subclass managing SQL transactions on generated reports. """


    # =========== FUNCTION ===========
    # ROLE: Initialize repository and bind the Report model automatically.
    def __init__(self, session: AsyncSession):
        """ Initialize repository with session and target table model. """
        
        # FLOW-1: Call parent class constructor with Report model type
        super().__init__(session, Report)      # USE: Parent constructor initialization
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Retrieve all reports associated with a session ID, ordered by creation date descending.
    async def get_reports_by_session(self, session_id: str) -> list[Report]:
        """ Fetch list of reports generated within a session ID. """
        
        # FLOW-1: Build and execute select query ordered by date descending
        try:
            stmt = select(Report).where(Report.session_id == session_id).order_by(Report.created_at.desc())  # USE: Ordered SELECT statement
            result = await self.session.execute(stmt)  # USE: Async query runner execution
            reports_list = list(result.scalars().all())  # USE: Extract all matching report records
            
            return reports_list
            
        except Exception as e:
            raise DatabaseException(str(e))     # USE: Wrap generic error to DatabaseException
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Retrieve only the single latest report generated for a session.
    async def get_latest_report(self, session_id: str) -> Report | None:
        """ Fetch the single most recent report for a session ID. """
        
        # FLOW-1: Build select query limited to one row ordered by date descending
        try:
            stmt = select(Report).where(Report.session_id == session_id).order_by(Report.created_at.desc()).limit(1)  # USE: SELECT statement with limit 1
            result = await self.session.execute(stmt)  # USE: Execute stmt async
            report_obj = result.scalar_one_or_none()  # USE: Extract single row scalar or None
            
            return report_obj
            
        except Exception as e:
            raise DatabaseException(str(e))     # USE: Exceptions translation wrapper
    # =========== FUNCTION ===========
# =========== CLASS ===========