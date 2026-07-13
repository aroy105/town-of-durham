from fastapi import WebSocket

class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, client_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str) -> None:
        self.active_connections.pop(client_id, None)
    
    async def send_to(self, client_id: str, message: dict) -> None:
        websocket = self.active_connections.get(client_id)
        if websocket is not None:
            await websocket.send_json(message)

    async def broadcast(self, message: dict) -> None:
        stale_ids = []
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception:
                stale_ids.append(client_id)
        for client_id in stale_ids:
            self.active_connections.pop(client_id, None)