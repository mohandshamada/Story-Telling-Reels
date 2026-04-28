import { useEffect, useRef, useState, useCallback } from 'react'

interface WsMessage {
  type: 'status' | 'scene' | 'error' | 'complete'
  status?: string
  stage?: string
  percent?: number
  scene_id?: string
  kind?: 'image' | 'audio'
  sequence?: number
  url?: string
  download_url?: string
  message?: string
}

export function useJobProgress(jobId: string | null | undefined) {
  const [wsData, setWsData] = useState<WsMessage | null>(null)
  const [connected, setConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  const connect = useCallback(() => {
    if (!jobId) return
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const ws = new WebSocket(`${protocol}//${host}/api/v1/ws/jobs/${jobId}`)

    ws.onopen = () => setConnected(true)
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as WsMessage
        setWsData(data)
      } catch {
        // ignore parse errors
      }
    }
    ws.onclose = () => setConnected(false)
    ws.onerror = () => setConnected(false)

    wsRef.current = ws
  }, [jobId])

  const disconnect = useCallback(() => {
    wsRef.current?.close()
    wsRef.current = null
    setConnected(false)
  }, [])

  useEffect(() => {
    connect()
    return () => disconnect()
  }, [connect, disconnect])

  return { wsData, connected, reconnect: connect }
}
