import { useState, useCallback } from 'react'

const STORAGE_KEY = 'cockpit-focus-mode'

export function useFocusMode() {
  const [focusMode, setFocusMode] = useState(() => {
    return localStorage.getItem(STORAGE_KEY) === 'true'
  })

  const toggleFocusMode = useCallback(() => {
    setFocusMode((prev) => {
      const next = !prev
      localStorage.setItem(STORAGE_KEY, String(next))
      return next
    })
  }, [])

  return { focusMode, toggleFocusMode }
}
