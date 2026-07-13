import { useState } from 'react'
import { JoinScreen } from './screens/JoinScreen'
import { LobbyScreen } from './screens/LobbyScreen'
import { GameBoard } from './screens/GameBoard'
import { useGameSocket } from './ws/useGameSocket'
import type { JoinedPlayer, StateMessage } from './types/messages'

function loadStoredPlayer(): JoinedPlayer | null {
  const raw = localStorage.getItem('player')
  return raw ? JSON.parse(raw) : null
}

function ConnectedGame({ me }: { me: JoinedPlayer }) {
  const { lastMessage, send } = useGameSocket(me.token)

  const state =
    lastMessage && (lastMessage as StateMessage).type === 'state'
      ? (lastMessage as StateMessage)
      : null

  const isHost = state !== null && state.host_player_id === me.player_id

  function handleAdvancePhase() {
    send({ type: 'advance_phase' })
  }

  if (state === null || state.phase === 'lobby') {
    return (
      <LobbyScreen me={me} state={state} isHost={isHost} onStartGame={handleAdvancePhase} />
    )
  }

  return <GameBoard me={me} state={state} isHost={isHost} onAdvancePhase={handleAdvancePhase} />
}

function App() {
  const [player, setPlayer] = useState<JoinedPlayer | null>(loadStoredPlayer)

  if (!player) {
    return <JoinScreen onJoined={setPlayer} />
  }

  return <ConnectedGame me={player} />
}

export default App
