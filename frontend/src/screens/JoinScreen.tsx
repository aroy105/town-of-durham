import { useState } from 'react'
import type { JoinedPlayer } from '../types/messages'

type JoinScreenProps = {
  onJoined: (player: JoinedPlayer) => void
}

export function JoinScreen({ onJoined }: JoinScreenProps) {
  const [displayName, setDisplayName] = useState('')
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)

    try {
      const res = await fetch('http://127.0.0.1:8000/join', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ display_name: displayName }),
      })
      if (!res.ok) {
        throw new Error(`join failed: ${res.status}`)
      }
      const player: JoinedPlayer = await res.json()
      localStorage.setItem('player', JSON.stringify(player))
      onJoined(player)
    } catch {
      setError('Could not join — is the backend running?')
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h1>Town of Durham</h1>
      <input
        value={displayName}
        onChange={(e) => setDisplayName(e.target.value)}
        placeholder="Your name"
        required
      />
      <button type="submit">Join</button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </form>
  )
}
