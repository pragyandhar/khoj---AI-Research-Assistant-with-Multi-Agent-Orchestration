# WHAT DOES THIS FILE DO: Alembic database migration script creating indexes on checkpoints schema.

# ================== IMPORTS ==================
from alembic import op
import sqlalchemy as sa
# ================== IMPORTS ==================


# =========== VARIABLES : Alembic Revision Metadata ===========
revision = '002_add_checkpointer_index'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None
# =========== VARIABLES : Alembic Revision Metadata ===========


# =========== FUNCTION ===========
# ROLE: Upgrade migration step.
def upgrade() -> None:
    """ Creates index on checkpoints table thread_id column if table exists. """
    
    # FLOW-1: Check if checkpoints table exists and create index
    bind = op.get_bind()                        # USE: Get database connection
    
    if bind.dialect.has_table(bind, "checkpoints"):  # USE: Check table existence
        op.create_index("ix_checkpoints_thread_id", "checkpoints", ["thread_id"])  # USE: Create index
# =========== FUNCTION ===========


# =========== FUNCTION ===========
# ROLE: Downgrade migration step.
def downgrade() -> None:
    """ Drops index on checkpoints table if table exists. """
    
    # FLOW-1: Check if checkpoints table exists and drop index if it does
    bind = op.get_bind()                        # USE: Get database connection
    
    if bind.dialect.has_table(bind, "checkpoints"):  # USE: Check table existence
        op.drop_index("ix_checkpoints_thread_id", table_name="checkpoints")  # USE: Drop index
# =========== FUNCTION ===========