// WHAT DOES THIS FILE DO: Lists a session's checkpoints and lets the user roll back to any of them (LangGraph time travel).

import { useState } from "react"
import { rollbackToCheckpoint } from "../../api/research"
import { useResearchStore } from "../../store/researchStore"

export function SessionHistory() {
  const [statusMessage, setStatusMessage] = useState<string | null>(null)

  const checkpoints = useResearchStore((state) => state.checkpoints)
  const sessionId = useResearchStore((state) => state.sessionId)
  const reset = useResearchStore((state) => state.reset)

  if (checkpoints.length === 0) {
    return <p className="text-sm text-gray-500">No checkpoints yet</p>
  }

  const currentCheckpointId = checkpoints[checkpoints.length - 1]?.checkpoint_id

  const handleRollback = async (checkpointId: string, node: string | null) => {
    if (!sessionId) return

    await rollbackToCheckpoint(sessionId, checkpointId)
    reset()
    setStatusMessage(`Rolled back to ${node ?? "initial"} checkpoint`)
  }

  return (
    <div>
      {statusMessage && <p className="mb-2 text-xs text-green-400">{statusMessage}</p>}

      <ul className="space-y-2">
        {checkpoints.map((checkpoint) => {
          const isCurrent = checkpoint.checkpoint_id === currentCheckpointId

          return (
            <li
              key={checkpoint.checkpoint_id}
              className="flex items-center justify-between rounded-md border border-gray-800 bg-gray-900 px-3 py-2 text-sm"
            >
              <div className="flex items-center gap-2">
                {isCurrent && <span className="h-2 w-2 rounded-full bg-green-500" title="Current" />}
                <div>
                  <p className="text-gray-200">{checkpoint.node ?? "start"}</p>
                  <p className="text-xs text-gray-500">{new Date(checkpoint.created_at).toLocaleString()}</p>
                </div>
              </div>

              <button
                type="button"
                onClick={() => void handleRollback(checkpoint.checkpoint_id, checkpoint.node)}
                className="rounded-md border border-gray-700 px-3 py-1 text-xs text-gray-300 transition hover:bg-gray-800"
              >
                Rollback
              </button>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
