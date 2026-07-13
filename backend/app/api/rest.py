from fastapi import APIRouter
from pydantic import BaseModel

from app.game.state import game_state

router = APIRouter()

class JoinRequest(BaseModel):
    display_name: str

class JoinResponse(BaseModel):
    token: str
    player_id: str
    display_name: str

@router.post("/join", response_model=JoinResponse)
def join(request: JoinRequest) -> JoinResponse:
    player = game_state.add_player(request.display_name)
    return JoinResponse(
        token=player.token,
        player_id=player.player_id,
        display_name=player.display_name,
    )

@router.get("/players")
def list_players() -> list[dict]:
    return game_state.public_player_list()