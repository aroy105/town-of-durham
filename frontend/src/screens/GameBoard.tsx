import type { JoinedPlayer, StateMessage } from '../types/messages'

type GameBoardProps = {
  me: JoinedPlayer
  state: StateMessage | null
  isHost: boolean
  onAdvancePhase: () => void
}

function phaseLabel(state: StateMessage | null): string {
  if (state === null) return '...'
  if (state.phase === 'night') return `Night ${state.day_number}`
  return `Day ${state.day_number}`
}

export function GameBoard({ me, state, isHost, onAdvancePhase }: GameBoardProps) {
  const players = state?.players ?? []

  return (
    <div style={{ textAlign: 'left', padding: '0 24px' }}>
      <h1>{phaseLabel(state)}</h1>
      <p>You are: {me.display_name}</p>
      <div
        style={{
          border: '1px solid var(--border)',
          borderRadius: 8,
          padding: '12px 16px',
          width: 200,
          marginTop: 12,
        }}
      >
        {players.map((p) => (
          <div key={p.player_id} style={{ padding: '4px 0' }}>
            {p.display_name}
            {p.player_id === state?.host_player_id ? ' [Host]' : ''}
          </div>
        ))}
      </div>
      {isHost && (
        <button style={{ marginTop: 12 }} onClick={onAdvancePhase}>
          Advance Phase
        </button>
      )}
    </div>
  )
}
