import { useEffect, useRef, useState } from 'react'

type ConnectionStatus = 'connecting' | 'open' | 'closed'

export function useGameSocket(clientId: string) {
  const [status, setStatus] = useState<ConnectionStatus>('connecting')
  const [lastMessage, setLastMessage] = useState<unknown>(null)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    let cancelled = false

    function connect() {
      const ws = new WebSocket(`ws://127.0.0.1:8000/ws/${clientId}`)
      wsRef.current = ws
      setStatus('connecting')

      ws.onopen = () => setStatus('open')
      ws.onmessage = (event) => setLastMessage(JSON.parse(event.data))
      ws.onclose = () => {
        setStatus('closed')
        if (!cancelled) {
          setTimeout(connect, 1000)
        }
      }
    }

    connect()

    return () => {
      cancelled = true
      wsRef.current?.close()
    }
  }, [clientId])

  function send(message: unknown) {
    wsRef.current?.send(JSON.stringify(message))
  }

  return { status, lastMessage, send }
}
