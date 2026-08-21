// WHAT DOES THIS FILE DO: Defines the global Zustand store holding the active research session's shared state.
//
// No persist middleware here, deliberately — session data should reset on browser refresh
// rather than resurrect a stale, possibly-completed research run.

import { create } from "zustand"
import { ResearchStatus } from "../types"
import type { CheckpointItem, SessionState, StreamEvent, StructuredReport } from "../types"

interface ResearchStoreState {
  query: string
  sessionId: string | null
  status: ResearchStatus
  report: StructuredReport | null
  streamEvents: StreamEvent[]
  isLoading: boolean
  awaitingApproval: boolean
  error: string | null
  sessionState: SessionState | null
  checkpoints: CheckpointItem[]

  setQuery: (query: string) => void
  setSessionId: (id: string) => void
  addStreamEvent: (event: StreamEvent) => void
  setReport: (report: StructuredReport) => void
  setStatus: (status: ResearchStatus) => void
  setIsLoading: (isLoading: boolean) => void
  setAwaitingApproval: (val: boolean) => void
  setError: (error: string | null) => void
  setSessionState: (sessionState: SessionState) => void
  setCheckpoints: (checkpoints: CheckpointItem[]) => void
  handleStreamEvent: (event: StreamEvent) => void
  reset: () => void
}

// USE: Fields reset() restores — kept separate so reset() can never drift from the initial state
const initialState = {
  query: "",
  sessionId: null,
  status: ResearchStatus.PENDING,
  report: null,
  streamEvents: [],
  isLoading: false,
  awaitingApproval: false,
  error: null,
  sessionState: null,
  checkpoints: [],
} satisfies Partial<ResearchStoreState>

export const useResearchStore = create<ResearchStoreState>()((set, get) => ({
  ...initialState,

  setQuery: (query) => set({ query }),
  setSessionId: (id) => set({ sessionId: id }),
  addStreamEvent: (event) => set({ streamEvents: [...get().streamEvents, event] }),
  setReport: (report) => set({ report }),
  setStatus: (status) => set({ status }),
  setIsLoading: (isLoading) => set({ isLoading }),
  setAwaitingApproval: (val) => set({ awaitingApproval: val }),
  setError: (error) => set({ error }),
  setSessionState: (sessionState) => set({ sessionState }),
  setCheckpoints: (checkpoints) => set({ checkpoints }),

  // FLOW-1: Route each incoming SSE event to the state update it implies
  handleStreamEvent: (event) => {
    get().addStreamEvent(event)

    switch (event.event_type) {
      case "status":
        if (typeof event.data.status === "string") {
          get().setStatus(event.data.status as ResearchStatus)
        }
        if (typeof event.data.session_id === "string") {
          get().setSessionId(event.data.session_id)
        }
        break

      case "awaiting_approval":
        get().setAwaitingApproval(true)
        get().setStatus(ResearchStatus.AWAITING_APPROVAL)
        if (typeof event.data.session_id === "string") {
          get().setSessionId(event.data.session_id)
        }
        break

      case "report":
        get().setReport(event.data as unknown as StructuredReport)
        get().setStatus(ResearchStatus.COMPLETED)
        get().setIsLoading(false)
        break

      case "cache_hit":
        if (event.data.report) {
          get().setReport(event.data.report as unknown as StructuredReport)
        }
        get().setStatus(ResearchStatus.COMPLETED)
        get().setIsLoading(false)
        break

      case "error": {
        const message = typeof event.data.message === "string" ? event.data.message : "Something went wrong"
        get().setError(message)
        get().setStatus(ResearchStatus.FAILED)
        get().setIsLoading(false)
        break
      }
    }
  },

  reset: () => set({ ...initialState }),
}))
