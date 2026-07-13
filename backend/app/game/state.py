import uuid
from dataclasses import dataclass

from app.game.phases import Phase

@dataclass
class Player:
    token: str
    player_id: str
    display_name: str
    connected: bool = False

class GameState:
    def __init__(self) -> None:
        self.players: dict[str, Player] = {}
        self.host_token: str | None = None
        self.phase: Phase = Phase.LOBBY
        self.day_number: int = 0

    def add_player(self, display_name: str) -> Player:
        token = str(uuid.uuid4())
        player = Player(token=token, player_id=token[:8], display_name=display_name)
        self.players[token] = player
        if self.host_token is None:
            self.host_token = token
        return player

    def get_player(self, token: str) -> Player | None:
        return self.players.get(token)

    @property
    def host_player_id(self) -> str | None:
        if self.host_token is None:
            return None
        return self.players[self.host_token].player_id

    def public_player_list(self) -> list[dict]:
        return [
            {"player_id": p.player_id, "display_name": p.display_name, "connected": p.connected}
            for p in self.players.values()
        ]

    def public_state(self) -> dict:
        return {
            "type": "state",
            "phase": self.phase.value,
            "day_number": self.day_number,
            "host_player_id": self.host_player_id,
            "players": self.public_player_list(),
        }

game_state = GameState()