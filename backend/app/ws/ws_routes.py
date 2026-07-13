from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.game.engine import PhaseError, advance_phase
from app.game.state import game_state
from app.ws.connection_manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()


async def broadcast_state() -> None:
    await manager.broadcast(game_state.public_state())


@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str) -> None:
    player = game_state.get_player(token)
    if player is None:
        await websocket.accept()
        await websocket.close(code=4004)
        return

    await manager.connect(token, websocket)
    player.connected = True
    await broadcast_state()

    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "advance_phase":
                try:
                    advance_phase(game_state, token)
                except PhaseError:
                    continue
                await broadcast_state()
    except WebSocketDisconnect:
        manager.disconnect(token)
        player.connected = False
        await broadcast_state()
