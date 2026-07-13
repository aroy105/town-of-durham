export type JoinedPlayer = {
  token: string
  player_id: string
  display_name: string
}

export type Player = {
  player_id: string
  display_name: string
  connected: boolean
}

export type Phase = 'lobby' | 'night' | 'day'

export type StateMessage = {
  type: 'state'
  phase: Phase
  day_number: number
  host_player_id: string | null
  players: Player[]
}
