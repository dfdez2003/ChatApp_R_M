import redis.asyncio as redis
import json
import uuid
from datetime import datetime
from schemas.mensaje import MensajeOut, MensajeIn
from services.usuario import obtener_usuario_por_id  # importante

r = redis.Redis()

MAX_MENSAJES = 50

# ✅ Guardar nuevo mensaje (usa lista para mantener orden y limitar tamaño)
async def guardar_mensaje(data: MensajeIn, usuario_id: str) -> MensajeOut:
    mensaje_id = str(uuid.uuid4())
    fecha = datetime.utcnow().isoformat()

    usuario = await obtener_usuario_por_id(usuario_id)

    mensaje = {
        "id": mensaje_id,
        "usuario_id": usuario_id,
        "sala_id": data.sala_id,
        "contenido": data.contenido,
        "fecha": fecha,
        "username": usuario.username
    }

    clave = f"sala:{data.sala_id}:mensajes"

    # Verifica tipo para evitar corrupción si antes era hash
    tipo = await r.type(clave)
    if tipo not in [b"none", b"list"]:
        raise Exception("Tipo de clave inválido para mensajes")

    await r.lpush(clave, json.dumps(mensaje))
    await r.ltrim(clave, 0, MAX_MENSAJES - 1)

    return MensajeOut(**mensaje)

# ✅ Obtener últimos mensajes de la sala (máx 50)
async def obtener_mensajes(sala_id: str, limite: int = 50) -> list[MensajeOut]:
    clave = f"sala:{sala_id}:mensajes"
    tipo = await r.type(clave)
    if tipo == b"none":
        return []

    if tipo != b"list":
        raise Exception("Tipo de clave inválido para mensajes")

    mensajes_raw = await r.lrange(clave, 0, limite - 1)
    mensajes = []
    for m in mensajes:
        print(f'mesajes chat debug: {m}')
    for raw in reversed(mensajes_raw):  # del más viejo al más nuevo
        try:
            data = json.loads(raw)
            mensajes.append(MensajeOut(**data))
        except (json.JSONDecodeError, TypeError, KeyError):
            continue

    return mensajes


## ------------------- Funciones no adaptadas aun para list


async def editar_mensaje(sala_id: str, mensaje_id: str, nuevo_contenido: str, usuario_id: str):
    clave = f"sala:{sala_id}:mensajes"
    tipo = await r.type(clave)
    if tipo != b"hash":
        raise Exception("La clave de mensajes no es de tipo hash")

    mensaje_raw = await r.hget(clave, mensaje_id)
    if not mensaje_raw:
        raise Exception("Mensaje no encontrado")

    mensaje = json.loads(mensaje_raw.decode())
    if mensaje["usuario_id"] != f"usuario:{usuario_id}":
        raise Exception("No puedes editar este mensaje")

    mensaje["contenido"] = nuevo_contenido
    await r.hset(clave, mensaje_id, json.dumps(mensaje))
    return {"mensaje": "Mensaje editado"}

async def eliminar_mensaje(sala_id: str, mensaje_id: str, usuario_id: str):
    clave = f"sala:{sala_id}:mensajes"
    tipo = await r.type(clave)
    if tipo != b"hash":
        raise Exception("La clave de mensajes no es de tipo hash")

    mensaje_raw = await r.hget(clave, mensaje_id)
    if not mensaje_raw:
        raise Exception("Mensaje no encontrado")

    mensaje = json.loads(mensaje_raw.decode())
    if mensaje["usuario_id"] != f"usuario:{usuario_id}":
        raise Exception("No puedes eliminar este mensaje")

    await r.hdel(clave, mensaje_id)
    return {"mensaje": "Mensaje eliminado"}

