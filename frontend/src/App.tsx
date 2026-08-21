// WHAT DOES THIS FILE DO: Assembles every component into the app's final two-column layout.

import { useEffect } from "react"
import { ApprovalModal } from "./components/ApprovalModal/ApprovalModal"
import { GraphVisualizer } from "./components/GraphVisualizer/GraphVisualizer"
import { QueryInput } from "./components/QueryInput/QueryInput"
import { SessionHistory } from "./components/SessionHistory/SessionHistory"
import { StreamOutput } from "./components/StreamOutput/StreamOutput"
import { useSession } from "./hooks/useSession"
import { useStream } from "./hooks/useStream"
import { useResearchStore } from "./store/researchStore"
import { ResearchStatus } from "./types"

function App() {
  // FLOW-1: Both hooks are initialized once, here, and their actions passed down — a second
  // useStream()/useSession() call elsewhere would create its own independent abort/interval
  // refs, which would no longer be the ones this page actually cleans up on unmount.
  const { startStream, resumeStream } = useStream()
  const { pollSessionState, fetchCheckpoints } = useSession()

  const sessionId = useResearchStore((state) => state.sessionId)
  const status = useResearchStore((state) => state.status)
  const error = useResearchStore((state) => state.error)
  const setError = useResearchStore((state) => state.setError)

  // FLOW-2: Once a session exists, start watching its live state and checkpoint history
  useEffect(() => {
    if (sessionId) {
      pollSessionState(sessionId)
      fetchCheckpoints(sessionId)
    }
  }, [sessionId, pollSessionState, fetchCheckpoints])

  // FLOW-3: Refresh the checkpoint list at points a new checkpoint is likely to exist
  useEffect(() => {
    if (sessionId && (status === ResearchStatus.COMPLETED || status === ResearchStatus.AWAITING_APPROVAL)) {
      fetchCheckpoints(sessionId)
    }
  }, [status, sessionId, fetchCheckpoints])

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <header className="flex items-center gap-3 border-b border-gray-800 px-6 py-4">
        <h1 className="text-xl font-semibold">AI Research Assistant</h1>
        <span className="rounded-full border border-purple-700 bg-purple-950/50 px-2 py-0.5 text-xs text-purple-300">
          Powered by Claude
        </span>
      </header>

      {error && (
        <div className="flex items-center justify-between border-b border-red-800 bg-red-950/60 px-6 py-2 text-sm text-red-200">
          <span>{error}</span>
          <button type="button" onClick={() => setError(null)} className="text-red-300 hover:text-red-100">
            Dismiss
          </button>
        </div>
      )}

      <main className="grid grid-cols-1 gap-6 p-6 lg:grid-cols-10">
        <section className="space-y-4 lg:col-span-7">
          <QueryInput startStream={startStream} />
          <StreamOutput />
        </section>

        <aside className="space-y-6 lg:col-span-3">
          <div className="rounded-lg border border-gray-800 bg-gray-900 p-4">
            <h2 className="mb-3 text-sm font-semibold text-gray-200">Graph Execution</h2>
            <GraphVisualizer />
          </div>

          <div className="rounded-lg border border-gray-800 bg-gray-900 p-4">
            <h2 className="mb-3 text-sm font-semibold text-gray-200">Session History</h2>
            <SessionHistory />
          </div>
        </aside>
      </main>

      <ApprovalModal resumeStream={resumeStream} />
    </div>
  )
}

export default App
