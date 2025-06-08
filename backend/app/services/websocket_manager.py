# services/websocket_manager.py                     # vale todo bien, estamos gestionando las conexiones solametne
from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:                # Clase para las operaciones de websockets
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}                    # Clave: id_clave Websockets

    async def connect(self, websocket: WebSocket, room_id: str):                    # Pasamos el websocket y el id 
        await websocket.accept()                                                    # Aceptamos la conexión del websocket
        if room_id not in self.active_connections:                                  # Comprobamos si existe la sala en nuestro dic
            self.active_connections[room_id] = []                                   # si no existe la creamos 
        self.active_connections[room_id].append(websocket)                          # la agregamos a el dic de websockets

    async def disconnect(self, room_id: str, websocket: WebSocket):
        conexiones = self.active_connections.get(room_id)
        if conexiones and websocket in conexiones:
            conexiones.remove(websocket)
            if not conexiones:
                self.active_connections.pop(room_id, None)

    async def broadcast(self, room_id: str, message: str):
        if room_id not in self.active_connections:
            return
        disconnected = []
        for conn in self.active_connections[room_id]:
            try:
                await conn.send_text(message)
            except Exception as e:
                print(f"⚠️ Error enviando a un websocket: {e}")
                disconnected.append(conn)
        # Eliminar conexiones cerradas
        for conn in disconnected:
            await self.disconnect(room_id, conn)                                           # si no no tendra nada, iteraremos en la lista y enviaremos a cada websocket el mensaje

manager = ConnectionManager()
