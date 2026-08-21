// WHAT DOES THIS FILE DO: Shows which LangGraph node is currently active as a simple box-and-arrow diagram.

import { useResearchStore } from "../../store/researchStore"

// USE: Matches the real edge order in backend app/graph/main_graph.py — router -> human_approval
// -> research -> summary -> citation_check -> output. The doc's original list had citation_check
// before summary, which doesn't match how the graph is actually wired.
const GRAPH_NODES = ["router", "human_approval", "research", "summary", "citation_check", "output"]

const AGENT_LABELS: Record<string, string> = {
  science: "Science Agent",
  technology: "Technology Agent",
  general: "General Agent",
}

export function GraphVisualizer() {
  const sessionState = useResearchStore((state) => state.sessionState)

  if (!sessionState) {
    return <p className="text-sm text-gray-500">Start a research query to see graph execution</p>
  }

  const agentLabel = sessionState.selected_agent ? AGENT_LABELS[sessionState.selected_agent] : undefined

  return (
    <div className="flex flex-wrap items-center gap-1">
      {GRAPH_NODES.map((nodeName, index) => {
        const isActive = sessionState.current_node === nodeName

        return (
          <div key={nodeName} className="flex items-center gap-1">
            <div className="flex flex-col items-center">
              <div
                className={
                  isActive
                    ? "rounded-md border-2 border-blue-400 bg-blue-950 px-3 py-2 text-xs font-medium text-blue-200"
                    : "rounded-md border border-gray-700 bg-gray-900 px-3 py-2 text-xs text-gray-400"
                }
              >
                {nodeName}
              </div>

              {nodeName === "research" && agentLabel && (
                <span className="mt-1 text-[10px] text-gray-500">{agentLabel}</span>
              )}
            </div>

            {index < GRAPH_NODES.length - 1 && <span className="text-gray-600">&rarr;</span>}
          </div>
        )
      })}
    </div>
  )
}
