from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query,Depends
from fastapi.encoders import jsonable_encoder
from services.websocket_manager import manager
from services.mensaje import guardar_mensaje
from schemas.mensaje import MensajeIn
from utils.auth import verificar_token
import json
from datetime import datetime 
from schemas.usuario import UsuarioOut
from utils.auth import get_current_user_ws
router = APIRouter()

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, usuario: UsuarioOut = Depends(get_current_user_ws)):
    await manager.connect(websocket, room_id)  
    try:
        while True:
            data = await websocket.receive_text()
            mensaje = MensajeIn(**json.loads(data))
            result = await guardar_mensaje(mensaje, usuario.id)
            await manager.broadcast(room_id, json.dumps(jsonable_encoder(result)))
    except WebSocketDisconnect:
        print("connection closed")
        await manager.disconnect(room_id, websocket)
