// WHAT DOES THIS FILE DO: Wraps every /research API call — including SSE streaming — behind plain async functions.
//
// NOTE ON STREAMING: the doc this phase was built from assumed a `GET /research/stream/{sessionId}`
// endpoint consumable via the native `EventSource` API. The actual backend (built in Phases 3-5)
// doesn't have that route — it streams Server-Sent Events directly from the `POST /research/query`
// and `POST /research/sessions/{id}/approve` responses themselves, and session_id isn't known
// until the stream itself reports it. `EventSource` cannot POST or read a POST response body, so
// streaming here is done via `fetch()` + a ReadableStream reader instead, parsing `data: ...`
// lines by hand. Adding a separate GET-by-session-id stream route would need a pub/sub layer the
// backend doesn't have — out of scope for a frontend-only phase.

import { apiClient, BASE_URL, API_KEY } from "./client"
import type { CheckpointItem, SessionState, StreamEvent } from "../types"

// =========== FUNCTION ===========
// ROLE: Reads an SSE response body, invoking onEvent for each parsed event as it arrives.
async function streamSSE(
  response: Response,
  onEvent: (event: StreamEvent) => void,
  onError: (error: unknown) => void
): Promise<void> {
  if (!response.ok || !response.body) {
    onError(new Error(`Request failed with status ${response.status}`))
    return
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ""

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      // FLOW-1: SSE events are separated by a blank line; keep any trailing partial event buffered
      const chunks = buffer.split("\n\n")
      buffer = chunks.pop() ?? ""

      for (const chunk of chunks) {
        const dataLine = chunk.split("\n").find((line) => line.startsWith("data:"))
        if (!dataLine) continue

        try {
          onEvent(JSON.parse(dataLine.slice(5).trim()) as StreamEvent)
        } catch {
          // USE: Skip a malformed chunk rather than aborting the whole stream over one bad event
        }
      }
    }
  } catch (error) {
    onError(error)
  }
}
// =========== FUNCTION ===========


// =========== FUNCTION ===========
// ROLE: Starts a research query and streams every resulting event back via onEvent.
export async function submitQuery(
  query: string,
  onEvent: (event: StreamEvent) => void,
  onError: (error: unknown) => void,
  userId?: string,
  signal?: AbortSignal
): Promise<void> {
  // FLOW-1: fetch() itself rejects on network failure (backend unreachable, DNS, CORS block —
  // before there's even a Response) — that rejection has to be caught here and routed through
  // onError too, or it becomes an unhandled promise rejection with no user-facing feedback and
  // isLoading stuck true forever, since the caller only awaits this via `void submitQuery(...)`.
  try {
    const response = await fetch(`${BASE_URL}/research/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: API_KEY,
        "X-Request-ID": crypto.randomUUID(),
      },
      body: JSON.stringify({ query, user_id: userId ?? null }),
      signal,
    })

    await streamSSE(response, onEvent, onError)
  } catch (error) {
    onError(error)
  }
}
// =========== FUNCTION ===========


// =========== FUNCTION ===========
// ROLE: Approves the pending human-approval gate and streams the resumed graph execution.
export async function approveResearch(
  sessionId: string,
  onEvent: (event: StreamEvent) => void,
  onError: (error: unknown) => void,
  modifiedQuery?: string,
  signal?: AbortSignal
): Promise<void> {
  // FLOW-1: see submitQuery's matching comment — fetch() itself can reject before streamSSE
  // ever runs, and that needs to reach onError too.
  try {
    const response = await fetch(`${BASE_URL}/research/sessions/${sessionId}/approve`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: API_KEY,
        "X-Request-ID": crypto.randomUUID(),
      },
      body: JSON.stringify({ modified_query: modifiedQuery ?? null }),
      signal,
    })

    await streamSSE(response, onEvent, onError)
  } catch (error) {
    onError(error)
  }
}
// =========== FUNCTION ===========


// =========== FUNCTION ===========
// ROLE: Fetches the aggregated session state for the graph visualizer.
export async function getSessionState(sessionId: string): Promise<SessionState> {
  const response = await apiClient.get<SessionState>(`/research/sessions/${sessionId}/state`)
  return response.data
}
// =========== FUNCTION ===========


// =========== FUNCTION ===========
// ROLE: Fetches every checkpoint recorded for a session, for the time-travel UI.
export async function getCheckpoints(sessionId: string): Promise<CheckpointItem[]> {
  const response = await apiClient.get<CheckpointItem[]>(`/research/sessions/${sessionId}/checkpoints`)
  return response.data
}
// =========== FUNCTION ===========


// =========== FUNCTION ===========
// ROLE: Rolls a session's active state back to a prior checkpoint.
export async function rollbackToCheckpoint(sessionId: string, checkpointId: string): Promise<void> {
  await apiClient.post(`/research/sessions/${sessionId}/rollback`, { checkpoint_id: checkpointId })
}
// =========== FUNCTION ===========
