// WHAT DOES THIS FILE DO: Human-in-the-loop gate — lets the user approve (optionally editing the query) or cancel before web search fires.

import { useState } from "react"
import { useResearchStore } from "../../store/researchStore"
import { ResearchStatus } from "../../types"

interface ApprovalModalProps {
  // USE: Owned by App (via useStream) — see QueryInput for why this isn't called locally
  resumeStream: (sessionId: string, modifiedQuery?: string) => void
}

export function ApprovalModal({ resumeStream }: ApprovalModalProps) {
  const [modifiedQuery, setModifiedQuery] = useState("")

  const awaitingApproval = useResearchStore((state) => state.awaitingApproval)
  const query = useResearchStore((state) => state.query)
  const sessionId = useResearchStore((state) => state.sessionId)
  const setAwaitingApproval = useResearchStore((state) => state.setAwaitingApproval)
  const setError = useResearchStore((state) => state.setError)
  const setStatus = useResearchStore((state) => state.setStatus)

  // FLOW-1: Render nothing at all while there's nothing to approve
  if (!awaitingApproval) return null

  const handleApprove = () => {
    if (!sessionId) return

    setAwaitingApproval(false)
    resumeStream(sessionId, modifiedQuery.trim() || undefined)
  }

  const handleCancel = () => {
    setAwaitingApproval(false)
    setError("Research cancelled by user")
    setStatus(ResearchStatus.FAILED)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
      <div className="w-full max-w-md rounded-lg border border-gray-800 bg-gray-900 p-6">
        <h2 className="text-lg font-semibold text-gray-100">Approval needed</h2>

        <p className="mt-3 text-sm text-gray-400">Original query:</p>
        <p className="mt-1 rounded-md bg-gray-950 p-2 text-sm text-gray-200">{query}</p>

        <p className="mt-4 text-sm text-gray-300">Do you want to proceed with web search?</p>

        <label className="mt-4 block text-xs text-gray-500" htmlFor="modified-query">
          Modify query (optional)
        </label>
        <textarea
          id="modified-query"
          value={modifiedQuery}
          onChange={(event) => setModifiedQuery(event.target.value)}
          rows={3}
          placeholder="Leave blank to research the original query"
          className="mt-1 w-full resize-none rounded-md border border-gray-700 bg-gray-950 p-2 text-sm text-gray-100 placeholder-gray-500 outline-none focus:border-purple-500"
        />

        <div className="mt-5 flex justify-end gap-3">
          <button
            type="button"
            onClick={handleCancel}
            className="rounded-md border border-gray-700 px-4 py-2 text-sm text-gray-300 transition hover:bg-gray-800"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleApprove}
            className="rounded-md bg-purple-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-purple-500"
          >
            Approve
          </button>
        </div>
      </div>
    </div>
  )
}
