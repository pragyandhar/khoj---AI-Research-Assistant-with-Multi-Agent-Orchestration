// WHAT DOES THIS FILE DO: Defines TypeScript types mirroring the backend's Pydantic models — the frontend/backend contract.

// Mirrors backend app/models/research.py ResearchStatus. The backend's own Python enum is
// missing AWAITING_APPROVAL even though it's a real status value the API emits (added when
// human-in-the-loop approval landed) — this type reflects what the backend actually sends.
// A const object (not `enum`) — this project's tsconfig enables erasableSyntaxOnly, which
// disallows TypeScript enums since they compile to more than a plain type erasure.
export const ResearchStatus = {
  PENDING: "pending",
  ROUTING: "routing",
  RESEARCHING: "researching",
  SUMMARIZING: "summarizing",
  CITING: "citing",
  COMPLETED: "completed",
  FAILED: "failed",
  AWAITING_APPROVAL: "awaiting_approval",
} as const

export type ResearchStatus = (typeof ResearchStatus)[keyof typeof ResearchStatus]

// Mirrors backend app/models/report.py Citation
export interface Citation {
  title: string
  url: string
  relevance_score: number
}

// Mirrors backend app/models/report.py ReportSection
export interface ReportSection {
  heading: string
  content: string
  citations: Citation[]
}

// Mirrors backend app/models/report.py StructuredReport
export interface StructuredReport {
  title: string
  summary: string
  sections: ReportSection[]
  topic: string
  confidence_score: number
  total_sources: number
  generated_at: string
}

// Mirrors backend app/models/research.py StreamEvent
export interface StreamEvent {
  event_type: string
  data: Record<string, unknown>
  timestamp: string
}

// Mirrors backend app/models/session.py SessionState
export interface SessionState {
  session_id: string
  current_node: string | null
  selected_agent: string | null
  status: string
  human_approved: boolean
  created_at: string
}

// Mirrors one entry returned by backend GET /research/sessions/{id}/checkpoints
// (SessionService.list_checkpoints in app/services/session_service.py). `node` is nullable —
// the very first ("input") checkpoint in a session has no producing node yet.
export interface CheckpointItem {
  checkpoint_id: string
  created_at: string
  node: string | null
}
