# WHAT DOES THIS FILE DO: Provides session state serialization, checkpoint history listing, and time-travel rollback for the research graph.

# ================== IMPORTS ==================
from app.core.exceptions import SessionNotFoundException
from app.models.session import AgentExecution, SessionState
from app.repositories.session_repository import SessionRepository
# ================== IMPORTS ==================


# =========== CLASS ===========
# ROLE: Service layer combining DB session records with live LangGraph checkpoint data.
class SessionService:
    """ Serializes graph checkpoint state into API-facing session models. """


    # =========== FUNCTION ===========
    # ROLE: Initialize SessionService with its DB repository and the compiled graph.
    def __init__(self, session_repository: SessionRepository, graph):
        """ Store repository and graph dependencies used for state lookups. """

        # FLOW-1: Assign repository and graph dependencies
        self.session_repo = session_repository  # USE: Session data table access repository
        self.graph = graph                      # USE: Compiled LangGraph workflow instance
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Fetches the full checkpoint history for a thread, ordered oldest to newest.
    async def _get_ordered_history(self, config: dict) -> list:
        """ LangGraph yields history newest-first; this reverses it to oldest-first. """

        # FLOW-1: Collect every checkpoint snapshot for the thread
        history = [snapshot async for snapshot in self.graph.aget_state_history(config)]  # USE: Pull full checkpoint history

        # FLOW-2: Reverse to chronological order
        history.reverse()                       # USE: Oldest checkpoint first

        return history
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Attributes each checkpoint transition to the node that produced it.
    def _node_for_transition(self, previous_snapshot) -> str | None:
        """ The node that ran between two checkpoints is the node previous_snapshot was about to execute. """

        # FLOW-1: A snapshot's `next` tuple names the node LangGraph was scheduled to run
        if previous_snapshot.next:
            return previous_snapshot.next[0]    # USE: Node that produced the following checkpoint

        return None                             # USE: No node scheduled (graph already finished)
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Best-effort size estimate of a node's output, for AgentExecution visibility.
    def _estimate_output_length(self, node: str, values: dict) -> int | None:
        """ Reads the relevant output field for a known node name, if present. """

        # FLOW-1: Look up the field each node is expected to have written
        if node == "research":
            output = values.get("research_output")
            return len(output) if output else None

        if node == "summary":
            report = values.get("final_report")
            return len(str(report)) if report else None

        return None                             # USE: Other nodes have no single output field to size
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Builds the AgentExecution timeline from an ordered checkpoint history.
    def _build_agent_executions(self, history: list) -> list[AgentExecution]:
        """ Converts consecutive checkpoint pairs into per-node execution records. """

        executions = []                         # USE: Accumulator for completed node executions

        # FLOW-1: Walk consecutive checkpoint pairs, attributing each transition to its node
        for index in range(1, len(history)):
            previous_snapshot = history[index - 1]
            current_snapshot = history[index]
            node = self._node_for_transition(previous_snapshot)  # USE: Node that ran in this transition

            if node is None:
                continue

            executions.append(AgentExecution(
                agent_name=node,
                started_at=previous_snapshot.created_at,
                completed_at=current_snapshot.created_at,
                status="completed",
                output_length=self._estimate_output_length(node, current_snapshot.values or {}),
            ))                                   # USE: Record this node's execution window

        return executions
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Serializes a session's live graph state into the SessionState API model.
    async def get_session_state(self, session_id: str) -> SessionState:
        """ Combines the DB session record with checkpointer state for full session visibility. """

        # FLOW-1: Confirm the session exists in the database
        db_session = await self.session_repo.get_by_session_id(session_id)  # USE: Fetch DB record

        if not db_session:
            raise SessionNotFoundException(f"Session {session_id} not found")  # USE: Raise 404-mapped error

        # FLOW-2: Pull live graph state and full checkpoint history for this thread
        config = {"configurable": {"thread_id": session_id}}  # USE: Thread query config
        state_info = await self.graph.aget_state(config)  # USE: Current checkpoint snapshot
        history = await self._get_ordered_history(config)  # USE: Full checkpoint timeline

        values = state_info.values or {}        # USE: Current channel values

        # FLOW-3: Assemble the SessionState response model
        return SessionState(
            session_id=session_id,
            current_node=state_info.next[0] if state_info.next else None,
            selected_agent=values.get("selected_agent"),
            status=values.get("status", db_session.status),
            agent_executions=self._build_agent_executions(history),
            human_approved=values.get("human_approved", False),
            created_at=db_session.created_at,
            updated_at=db_session.updated_at,
        )
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Lists every checkpoint for a session, for the frontend time-travel UI.
    async def list_checkpoints(self, session_id: str) -> list[dict]:
        """ Returns each checkpoint's ID, timestamp, and producing node, oldest first. """

        # FLOW-1: Walk the ordered checkpoint history and attribute each to its node
        config = {"configurable": {"thread_id": session_id}}  # USE: Thread query config
        history = await self._get_ordered_history(config)  # USE: Full checkpoint timeline

        checkpoints = []                        # USE: Accumulator for checkpoint summaries

        for index, snapshot in enumerate(history):
            node = self._node_for_transition(history[index - 1]) if index > 0 else None  # USE: Node that produced this checkpoint

            checkpoints.append({
                "checkpoint_id": snapshot.config["configurable"]["checkpoint_id"],
                "created_at": snapshot.created_at,
                "node": node,
            })                                   # USE: One checkpoint summary entry

        return checkpoints
    # =========== FUNCTION ===========


    # =========== FUNCTION ===========
    # ROLE: Rolls a session's active state back to the values recorded at a prior checkpoint.
    async def rollback_to_checkpoint(self, session_id: str, checkpoint_id: str) -> None:
        """ Forks a new checkpoint carrying the target checkpoint's values onto the active thread. """

        # FLOW-1: Fetch the state values recorded at the target checkpoint
        rollback_config = {
            "configurable": {"thread_id": session_id, "checkpoint_id": checkpoint_id}
        }                                        # USE: Config pointing to the target checkpoint
        state_at_checkpoint = await self.graph.aget_state(rollback_config)  # USE: Retrieve target checkpoint state

        if not state_at_checkpoint.values:
            raise SessionNotFoundException(f"Checkpoint {checkpoint_id} not found for session {session_id}")  # USE: Raise 404-mapped error

        # FLOW-2: Overwrite the active thread's state with the checkpoint's values
        active_config = {"configurable": {"thread_id": session_id}}  # USE: Config pointing to the active head
        await self.graph.aupdate_state(
            active_config,
            state_at_checkpoint.values,
            as_node="router"
        )                                        # USE: Fork a new checkpoint carrying the rolled-back values
    # =========== FUNCTION ===========
# =========== CLASS ===========
