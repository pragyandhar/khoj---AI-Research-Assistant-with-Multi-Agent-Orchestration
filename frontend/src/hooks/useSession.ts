// WHAT DOES THIS FILE DO: Short-polls session state while approval is pending, stopping once the session finishes.

import { useCallback, useEffect, useRef } from "react"
import { getCheckpoints, getSessionState } from "../api/research"
import { useResearchStore } from "../store/researchStore"
import { ResearchStatus } from "../types"

const POLL_INTERVAL_MS = 2000

export function useSession() {
  // USE: setInterval returns `number` in a browser/DOM context, not Node's NodeJS.Timeout —
  // this project has no @types/node, and ReturnType<typeof setInterval> is the portable form.
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const status = useResearchStore((state) => state.status)
  const setSessionState = useResearchStore((state) => state.setSessionState)
  const setCheckpoints = useResearchStore((state) => state.setCheckpoints)

  // FLOW-1: Clear any active polling interval
  const stopPolling = useCallback(() => {
    if (intervalRef.current !== null) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }, [])

  // FLOW-2: Poll session state every 2s until stopPolling() is called
  const pollSessionState = useCallback(
    (sessionId: string) => {
      stopPolling()

      intervalRef.current = setInterval(() => {
        void getSessionState(sessionId)
          .then(setSessionState)
          .catch(() => {
            // USE: A transient poll failure shouldn't kill future polls — just skip this tick
          })
      }, POLL_INTERVAL_MS)
    },
    [setSessionState, stopPolling]
  )

  // FLOW-3: Fetch the checkpoint list for the time-travel UI
  const fetchCheckpoints = useCallback(
    (sessionId: string) => {
      void getCheckpoints(sessionId)
        .then(setCheckpoints)
        .catch(() => {
          // USE: Checkpoint listing is a secondary feature — a failure here shouldn't break the page
        })
    },
    [setCheckpoints]
  )

  // FLOW-4: Stop polling automatically once the session reaches a terminal status
  useEffect(() => {
    if (status === ResearchStatus.COMPLETED || status === ResearchStatus.FAILED) {
      stopPolling()
    }
  }, [status, stopPolling])

  // FLOW-5: Always stop polling when the component using this hook unmounts
  useEffect(() => {
    return () => stopPolling()
  }, [stopPolling])

  return { pollSessionState, stopPolling, fetchCheckpoints }
}
