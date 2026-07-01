# WHAT DOES THIS FILE DO: Alembic database migration script creating the initial sessions and reports schemas.

# ================== IMPORTS ==================
from alembic import op
import sqlalchemy as sa
# ================== IMPORTS ==================


# =========== VARIABLES : Alembic Revision Metadata ===========
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None
# =========== VARIABLES : Alembic Revision Metadata ===========


# =========== FUNCTION ===========
# ROLE: Upgrade migration step creating sessions and reports tables and their indices.
def upgrade() -> None:
    """ Creates sessions and reports tables with constraints and indexes. """
    
    # FLOW-1: Create the sessions table
    op.create_table(
        'sessions',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('user_ip', sa.String(length=45), nullable=True),
        sa.Column('graph_state', sa.JSON(), nullable=True),
        sa.Column('checkpoint_data', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('session_id')
    )                                           # USE: Schema DDL for sessions table
    
    # FLOW-2: Explicitly build index on sessions table session_id column
    op.create_index('ix_sessions_session_id', 'sessions', ['session_id'], unique=True)  # USE: Index sessions table
    
    # FLOW-3: Create the reports table referencing sessions
    op.create_table(
        'reports',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('query', sa.Text(), nullable=False),
        sa.Column('report_data', sa.JSON(), nullable=True),
        sa.Column('topic', sa.String(length=50), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], )
    )                                           # USE: Schema DDL for reports table
    
    # FLOW-4: Explicitly build index on reports table session_id column
    op.create_index('ix_reports_session_id', 'reports', ['session_id'], unique=False)  # USE: Index reports table
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Downgrade migration step dropping sessions and reports tables in reverse order.
def downgrade() -> None:
    """ Drops the reports and sessions tables. """
    
    # FLOW-1: Drop index and table for reports (child table) first
    op.drop_index('ix_reports_session_id', table_name='reports')  # USE: Drop reports index
    op.drop_table('reports')                    # USE: Drop reports table
    
    # FLOW-2: Drop index and table for sessions (parent table) second
    op.drop_index('ix_sessions_session_id', table_name='sessions')  # USE: Drop sessions index
    op.drop_table('sessions')                   # USE: Drop sessions table
# =========== FUNCTION ===========