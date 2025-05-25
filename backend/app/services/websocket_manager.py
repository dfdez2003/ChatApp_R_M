# services/websocket_manager.py
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

    async def disconnect(self, websocket: WebSocket, room_id: str):                 # Pasamos el websocket y el id 
        self.active_connections[room_id].remove(websocket)                          # Vamos a remover el webosocket q tenga ese id
        if not self.active_connections[room_id]:                                    # Verifica si hay conexiones aun, si queda vacia borra el dic
            del self.active_connections[room_id]                                    

    async def broadcast(self, room_id: str, message: str):                          # Pasamos id y el mensaje
        for conn in self.active_connections.get(room_id, []):                       # optenemos la lista de websockets en la sala room_id, si existe retornara los [ws1,ws2]
            await conn.send_text(message)                                           # si no no tendra nada, iteraremos en la lista y enviaremos a cada websocket el mensaje

manager = ConnectionManager()
