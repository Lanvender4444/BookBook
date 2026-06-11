import { useEffect, useState } from "react"

const BACKEND_PORT = typeof __BACKEND_PORT__ !== 'undefined' ? __BACKEND_PORT__ : 18140

export function useBackendReady() {
  const [ready, setReady] = useState(false)

  useEffect(() => {
    const isTauri = typeof window !== 'undefined' && !!(window.__TAURI_INTERNALS__)
    if (!isTauri) {
      setReady(true)
      return
    }

    let cancelled = false
    const check = async () => {
      for (let i = 0; i < 40; i++) {
        if (cancelled) return
        try {
          await fetch(`http://localhost:${BACKEND_PORT}/api/identity`)
          if (!cancelled) setReady(true)
          return
        } catch {
          await new Promise(r => setTimeout(r, 500))
        }
      }
    }
    check()
    return () => { cancelled = true }
  }, [])

  return ready
}