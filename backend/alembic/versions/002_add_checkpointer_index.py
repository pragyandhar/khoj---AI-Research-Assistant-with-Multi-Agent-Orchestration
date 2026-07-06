# Task-1: upgrade() mein check karo ki LangGraph ki checkpoints table exist karti hai — op.get_bind().dialect.has_table(op.get_bind(), "checkpoints") se
# Task-2: Table exist karti hai toh op.create_index("ix_checkpoints_thread_id", "checkpoints", ["thread_id"]) create karo
# Task-3: downgrade() mein index drop karo