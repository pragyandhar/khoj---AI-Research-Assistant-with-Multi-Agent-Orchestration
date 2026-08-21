// WHAT DOES THIS FILE DO: Configures the shared Axios client — base URL, auth header, and request/response interceptors.

import axios from "axios"

// USE: Single source of truth for the backend base URL and API key, shared by every API call
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
  headers: {
    Authorization: import.meta.env.VITE_API_KEY,
  },
})

// FLOW-1: Tag every outgoing request with a correlation ID, matching the backend's own
// correlation ID middleware so a request can be traced end to end.
apiClient.interceptors.request.use((config) => {
  config.headers.set("X-Request-ID", crypto.randomUUID())
  return config
})

// FLOW-2: Centralize error logging for common failure statuses, so components don't each
// need their own 401/429 handling.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error("Unauthorized")
    } else if (error.response?.status === 429) {
      console.warn("Rate limited, retry after 60s")
    }

    return Promise.reject(error)
  }
)
