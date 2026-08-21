// WHAT DOES THIS FILE DO: Encapsulates the SSE streaming lifecycle so components just call startStream()/resumeStream().
//
// Adapted from the doc's EventSource-based design (see api/research.ts's module docstring for
// why): there's no persistent EventSource object to hold in a ref here, so an AbortController
// fills the same role — stopStream() aborts the in-flight fetch instead of closing a socket.

import { useCallback, useEffect, useRef } from "react"
import { approveResearch, submitQuery } from "../api/research"
import { useResearchStore } from "../store/researchStore"

export function useStream() {
  const abortControllerRef = useRef<AbortController | null>(null)
  const handleStreamEvent = useResearchStore((state) => state.handleStreamEvent)
  const setError = useResearchStore((state) => state.setError)

  // FLOW-1: Abort whatever stream is currently in flight, if any
  const stopStream = useCallback(() => {
    abortControllerRef.current?.abort()
    abortControllerRef.current = null
  }, [])

  // FLOW-2: Report a stream failure, but only if it wasn't just us aborting it on purpose
  const reportStreamError = useCallback(
    (controller: AbortController, error: unknown) => {
      if (controller.signal.aborted) return
      setError(error instanceof Error ? error.message : "Research stream failed")
    },
    [setError]
  )

  // FLOW-3: Start a brand new research query stream
  const startStream = useCallback(
    (query: string, userId?: string) => {
      stopStream()
      const controller = new AbortController()
      abortControllerRef.current = controller

      void submitQuery(
        query,
        handleStreamEvent,
        (error) => reportStreamError(controller, error),
        userId,
        controller.signal
      )
    },
    [handleStreamEvent, reportStreamError, stopStream]
  )

  // FLOW-4: Resume an existing session's stream after human approval
  const resumeStream = useCallback(
    (sessionId: string, modifiedQuery?: string) => {
      stopStream()
      const controller = new AbortController()
      abortControllerRef.current = controller

      void approveResearch(
        sessionId,
        handleStreamEvent,
        (error) => reportStreamError(controller, error),
        modifiedQuery,
        controller.signal
      )
    },
    [handleStreamEvent, reportStreamError, stopStream]
  )

  // FLOW-5: Abort any in-flight stream when the component using this hook unmounts
  useEffect(() => {
    return () => stopStream()
  }, [stopStream])

  return { startStream, resumeStream, stopStream }
}
