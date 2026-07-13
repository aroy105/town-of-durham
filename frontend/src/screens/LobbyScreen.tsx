import { useGameSocket } from '../ws/useGameSocket'

type JoinedPlayer = {
  token: string
  player_id: string
  display_name: string
}

type Player = {
  player_id: string
  display_name: string
  connected: boolean
}

type PlayerListMessage = {
  type: 'player_list'
  players: Player[]
}

type LobbyScreenProps = {
  me: JoinedPlayer
}

export function LobbyScreen({ me }: LobbyScreenProps) {
  const { lastMessage } = useGameSocket(me.token)

  const players =
    lastMessage && (lastMessage as PlayerListMessage).type === 'player_list'
      ? (lastMessage as PlayerListMessage).players
      : []

  return (
    <div style={{ textAlign: 'left', padding: '0 24px' }}>
      <h1>Lobby</h1>
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
          </div>
        ))}
      </div>
    </div>
  )
}
