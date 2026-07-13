import { useState } from 'react'
import { JoinScreen } from './screens/JoinScreen'
import { LobbyScreen } from './screens/LobbyScreen'

type JoinedPlayer = {
  token: string
  player_id: string
  display_name: string
}

function loadStoredPlayer(): JoinedPlayer | null {
  const raw = localStorage.getItem('player')
  return raw ? JSON.parse(raw) : null
}

function App() {
  const [player, setPlayer] = useState<JoinedPlayer | null>(loadStoredPlayer)

  if (!player) {
    return <JoinScreen onJoined={setPlayer} />
  }

  return <LobbyScreen me={player} />
}

export default App
