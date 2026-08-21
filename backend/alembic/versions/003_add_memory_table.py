# WHAT DOES THIS FILE DO: Alembic database migration script creating the user_memories table for long-term memory.

# ================== IMPORTS ==================
from alembic import op
import sqlalchemy as sa
# ================== IMPORTS ==================


# =========== VARIABLES : Alembic Revision Metadata ===========
revision = '003_add_memory_table'
down_revision = '002_add_checkpointer_index'
branch_labels = None
depends_on = None
# =========== VARIABLES : Alembic Revision Metadata ===========


# =========== FUNCTION ===========
# ROLE: Upgrade migration step creating the user_memories table and its index.
def upgrade() -> None:
    """ Creates the user_memories table with constraints and indexes. """

    # FLOW-1: Create the user_memories table
    op.create_table(
        'user_memories',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.String(length=100), nullable=False),
        sa.Column('memory_type', sa.String(length=50), nullable=False),
        sa.Column('content', sa.JSON(), nullable=False),
        sa.Column('embedding_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_accessed', sa.DateTime(), nullable=True),
    )                                           # USE: Schema DDL for user_memories table

    # FLOW-2: Explicitly build index on user_memories table user_id column
    op.create_index('ix_user_memories_user_id', 'user_memories', ['user_id'], unique=False)  # USE: Index user_memories table
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Downgrade migration step dropping the user_memories table.
def downgrade() -> None:
    """ Drops the user_memories table and its index. """

    # FLOW-1: Drop index and table
    op.drop_index('ix_user_memories_user_id', table_name='user_memories')  # USE: Drop user_memories index
    op.drop_table('user_memories')              # USE: Drop user_memories table
# =========== FUNCTION ===========
