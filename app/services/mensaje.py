# services/mensaje_service.py

import redis.asyncio as redis
import json
import uuid
from datetime import datetime
from schemas.mensaje import MensajeOut

r = redis.Redis()

async def guardar_mensaje(data, usuario_id: str) -> MensajeOut:
    mensaje_id = str(uuid.uuid4())
    fecha = datetime.utcnow().isoformat()

    mensaje = {
        "id": mensaje_id,
        "usuario_id": f"usuario:{usuario_id}",
        "sala_id": data.sala_id,
        "contenido": data.contenido,
        "fecha": fecha
    }

    await r.hset(f"sala:{data.sala_id}:mensajes", mensaje_id, json.dumps(mensaje))

    return MensajeOut(**mensaje)

async def obtener_mensajes(sala_id: str) -> list[MensajeOut]:
    mensajes_raw = await r.hgetall(f"sala:{sala_id}:mensajes")
    mensajes = []

    for id_mensaje, datos in mensajes_raw.items():
        mensaje = json.loads(datos.decode())
        mensajes.append(MensajeOut(**mensaje))

    # Ordenar los mensajes por fecha
    mensajes.sort(key=lambda x: x.fecha)
    return mensajes

async def editar_mensaje(sala_id: str, mensaje_id: str, nuevo_contenido: str, usuario_id: str):
    mensaje_raw = await r.hget(f"sala:{sala_id}:mensajes", mensaje_id)
    if not mensaje_raw:
        raise Exception("Mensaje no encontrado")

    mensaje = json.loads(mensaje_raw.decode())
    if mensaje["usuario_id"] != f"usuario:{usuario_id}":
        raise Exception("No puedes editar este mensaje")

    mensaje["contenido"] = nuevo_contenido

    await r.hset(f"sala:{sala_id}:mensajes", mensaje_id, json.dumps(mensaje))
    return {"mensaje": "Mensaje editado"}

async def eliminar_mensaje(sala_id: str, mensaje_id: str, usuario_id: str):
    mensaje_raw = await r.hget(f"sala:{sala_id}:mensajes", mensaje_id)
    if not mensaje_raw:
        raise Exception("Mensaje no encontrado")

    mensaje = json.loads(mensaje_raw.decode())
    if mensaje["usuario_id"] != f"usuario:{usuario_id}":
        raise Exception("No puedes eliminar este mensaje")

    await r.hdel(f"sala:{sala_id}:mensajes", mensaje_id)
    return {"mensaje": "Mensaje eliminado"}


