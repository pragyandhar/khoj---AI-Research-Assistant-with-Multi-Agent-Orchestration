// WHAT DOES THIS FILE DO: Renders the live SSE event log plus the final structured report once it arrives.

import { useState } from "react"
import ReactMarkdown from "react-markdown"
import { useResearchStore } from "../../store/researchStore"
import type { ReportSection } from "../../types"

// =========== FUNCTION ===========
// ROLE: One collapsible report section — click the heading to expand its content and citations.
function ReportSectionAccordion({ section }: { section: ReportSection }) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="border-b border-gray-800 last:border-b-0">
      <button
        type="button"
        onClick={() => setIsOpen((open) => !open)}
        className="flex w-full items-center justify-between py-3 text-left text-gray-100"
      >
        <span className="font-medium">{section.heading}</span>
        <span className="text-gray-500">{isOpen ? "−" : "+"}</span>
      </button>

      {isOpen && (
        <div className="pb-4 text-sm text-gray-300">
          <ReactMarkdown>{section.content}</ReactMarkdown>

          {section.citations.length > 0 && (
            <ul className="mt-3 space-y-1 border-t border-gray-800 pt-2 text-xs text-gray-500">
              {section.citations.map((citation) => (
                <li key={citation.url}>
                  <a href={citation.url} target="_blank" rel="noreferrer" className="text-purple-400 hover:underline">
                    {citation.title}
                  </a>{" "}
                  &middot; relevance {citation.relevance_score.toFixed(2)}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}
// =========== FUNCTION ===========


export function StreamOutput() {
  const streamEvents = useResearchStore((state) => state.streamEvents)
  const isLoading = useResearchStore((state) => state.isLoading)
  const report = useResearchStore((state) => state.report)

  // FLOW-1: Latest event first
  const orderedEvents = [...streamEvents].reverse()

  if (orderedEvents.length === 0) {
    return <p className="text-sm text-gray-500">Submit a query to see live progress here.</p>
  }

  return (
    <div className="space-y-3">
      {orderedEvents.map((event, index) => {
        const key = `${event.timestamp}-${index}`

        // FLOW-2: Progress indicator, showing the reported status and topic/agent if present
        if (event.event_type === "status") {
          const topic = typeof event.data.topic === "string" ? event.data.topic : undefined
          const statusLabel = typeof event.data.status === "string" ? event.data.status : "working"

          return (
            <div
              key={key}
              className="flex items-center gap-2 rounded-md border border-gray-800 bg-gray-900 px-3 py-2 text-sm text-gray-300"
            >
              {isLoading && (
                <span className="h-3 w-3 animate-spin rounded-full border-2 border-gray-600 border-t-purple-500" />
              )}
              <span>
                {statusLabel}
                {topic ? ` — ${topic}` : ""}
              </span>
            </div>
          )
        }

        // FLOW-3: Warning banner while the human-approval gate is pending
        if (event.event_type === "awaiting_approval") {
          return (
            <div key={key} className="rounded-md border border-yellow-700 bg-yellow-950/40 px-3 py-2 text-sm text-yellow-300">
              Waiting for your approval to continue.
            </div>
          )
        }

        // FLOW-4: Error message
        if (event.event_type === "error") {
          const message = typeof event.data.message === "string" ? event.data.message : "Something went wrong"

          return (
            <div key={key} className="rounded-md border border-red-700 bg-red-950/40 px-3 py-2 text-sm text-red-300">
              {message}
            </div>
          )
        }

        // FLOW-5: Cache hit badge
        if (event.event_type === "cache_hit") {
          return (
            <span
              key={key}
              className="inline-block rounded-full border border-green-700 bg-green-950/40 px-3 py-1 text-xs text-green-300"
            >
              Loaded from cache
            </span>
          )
        }

        // FLOW-6: Full report — rendered from the store's typed report, not the raw event payload
        if (event.event_type === "report" && report) {
          return (
            <div key={key} className="rounded-lg border border-gray-800 bg-gray-900 p-4">
              <h2 className="text-lg font-semibold text-gray-100">{report.title}</h2>
              <div className="mt-2 text-sm text-gray-300">
                <ReactMarkdown>{report.summary}</ReactMarkdown>
              </div>
              <div className="mt-4">
                {report.sections.map((section) => (
                  <ReportSectionAccordion key={section.heading} section={section} />
                ))}
              </div>
            </div>
          )
        }

        return null
      })}
    </div>
  )
}
