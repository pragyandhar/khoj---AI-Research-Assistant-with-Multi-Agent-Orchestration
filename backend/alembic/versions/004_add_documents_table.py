# WHAT DOES THIS FILE DO: Alembic database migration script creating the research_documents table for ChromaDB metadata sync.

# ================== IMPORTS ==================
from alembic import op
import sqlalchemy as sa
# ================== IMPORTS ==================


# =========== VARIABLES : Alembic Revision Metadata ===========
revision = '004_add_documents_table'
down_revision = '003_add_memory_table'
branch_labels = None
depends_on = None
# =========== VARIABLES : Alembic Revision Metadata ===========


# =========== FUNCTION ===========
# ROLE: Upgrade migration step creating the research_documents table and its indexes.
def upgrade() -> None:
    """ Creates the research_documents table with constraints and indexes. """

    # FLOW-1: Create the research_documents table referencing sessions
    op.create_table(
        'research_documents',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('chroma_id', sa.String(length=100), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content_preview', sa.String(length=500), nullable=True),
        sa.Column('topic', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], ),
        sa.UniqueConstraint('chroma_id'),
    )                                           # USE: Schema DDL for research_documents table

    # FLOW-2: Explicitly build indexes on session_id and topic columns
    op.create_index('ix_research_documents_session_id', 'research_documents', ['session_id'], unique=False)  # USE: Index session_id lookups
    op.create_index('ix_research_documents_topic', 'research_documents', ['topic'], unique=False)  # USE: Index topic lookups
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Downgrade migration step dropping the research_documents table.
def downgrade() -> None:
    """ Drops the research_documents table and its indexes. """

    # FLOW-1: Drop indexes and table
    op.drop_index('ix_research_documents_topic', table_name='research_documents')  # USE: Drop topic index
    op.drop_index('ix_research_documents_session_id', table_name='research_documents')  # USE: Drop session_id index
    op.drop_table('research_documents')         # USE: Drop research_documents table
# =========== FUNCTION ===========
