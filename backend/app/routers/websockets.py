from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.websocket_manager import manager

router = APIRouter()

@router.websocket("/ws/{room_id}")                                  # Sale con el /ws/{room_id}
async def websocket_endpoint(websocket: WebSocket, room_id: str):   # Vamos a pasar el websocket y el id de la sala           
    print(f"🔌 Nueva conexión a sala {room_id}")
    await manager.connect(websocket, room_id)                       # Realizamos la conexión con el manager 
    try:                                                            # Creamos un bucle infinito en el que estaremos recibiendo datos ( no conexiónes por que ya esta abierta)
        while True: 
            data = await websocket.receive_text()                   # Recibimos texto 
            print(f"📥 Mensaje recibido en sala {room_id}: {data}") # Imprimimos el id room y el texto
            await manager.broadcast(room_id, data)                  # Lanzamos el mensaje a todos los websockets de esa sala    
    except WebSocketDisconnect:                                     # si una conexión se cierra imprimimos
        print(f"❌ Desconexión de sala {room_id}")
        await manager.disconnect(websocket, room_id)                # y desconectamos



