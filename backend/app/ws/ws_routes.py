from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.game.state import game_state
from app.ws.connection_manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()


async def broadcast_player_list() -> None:
    await manager.broadcast({"type": "player_list", "players": game_state.public_player_list()})


@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str) -> None:
    player = game_state.get_player(token)
    if player is None:
        await websocket.accept()
        await websocket.close(code=4004)
        return

    await manager.connect(token, websocket)
    player.connected = True
    await broadcast_player_list()

    try:
        while True:
            await websocket.receive_json()
    except WebSocketDisconnect:
        manager.disconnect(token)
        player.connected = False
        await broadcast_player_list()
