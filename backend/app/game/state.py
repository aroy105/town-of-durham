import uuid
from dataclasses import dataclass

@dataclass
class Player:
    token: str
    player_id: str
    display_name: str
    connected: bool = False

class GameState:
    def __init__(self) -> None:
        self.players: dict[str, Player] = {}

    def add_player(self, display_name: str) -> Player:
        token = str(uuid.uuid4())
        player = Player(token=token, player_id=token[:8], display_name=display_name)
        self.players[token] = player
        return player

    def get_player(self, token: str) -> Player | None:
        return self.players.get(token)
    
    def public_player_list(self) -> list[dict]:
        return [
            {"player_id": p.player_id, "display_name": p.display_name, "connected": p.connected}
            for p in self.players.values()
        ]

game_state = GameState()