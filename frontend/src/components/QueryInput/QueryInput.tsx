// WHAT DOES THIS FILE DO: The query entry point — a validated textarea that kicks off a new research stream.

import { useResearchStore } from "../../store/researchStore"

const MIN_QUERY_LENGTH = 10
const MAX_QUERY_LENGTH = 500

interface QueryInputProps {
  // USE: Owned by App (via useStream), not this component — see useStream.ts's module docstring
  // on why a single shared stream lifecycle matters.
  startStream: (query: string, userId?: string) => void
}

export function QueryInput({ startStream }: QueryInputProps) {
  const query = useResearchStore((state) => state.query)
  const setQuery = useResearchStore((state) => state.setQuery)
  const isLoading = useResearchStore((state) => state.isLoading)
  const setIsLoading = useResearchStore((state) => state.setIsLoading)
  const reset = useResearchStore((state) => state.reset)

  const isSubmitDisabled = query.length < MIN_QUERY_LENGTH || isLoading

  // FLOW-1: Capture the typed query before reset() clears the store back to its initial state
  const handleSubmit = () => {
    if (isSubmitDisabled) return

    const submittedQuery = query
    reset()
    setIsLoading(true)
    startStream(submittedQuery)
  }

  return (
    <div className="rounded-lg border border-gray-800 bg-gray-900 p-4">
      <textarea
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        disabled={isLoading}
        maxLength={MAX_QUERY_LENGTH}
        rows={4}
        placeholder="Ask a research question — e.g. 'What are the latest advances in battery technology?'"
        className="w-full resize-none rounded-md border border-gray-700 bg-gray-950 p-3 text-gray-100 placeholder-gray-500 outline-none focus:border-purple-500 disabled:opacity-50"
      />

      <div className="mt-2 flex items-center justify-between">
        <span className="text-sm text-gray-500">
          {query.length}/{MAX_QUERY_LENGTH}
        </span>

        <button
          type="button"
          onClick={handleSubmit}
          disabled={isSubmitDisabled}
          className="rounded-md bg-purple-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-purple-500 disabled:cursor-not-allowed disabled:bg-gray-700 disabled:text-gray-400"
        >
          {isLoading ? "Researching..." : "Start Research"}
        </button>
      </div>
    </div>
  )
}
