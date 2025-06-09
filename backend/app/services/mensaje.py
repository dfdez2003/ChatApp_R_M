import redis.asyncio as redis
import json
import uuid
from datetime import datetime
from schemas.mensaje import MensajeOut, MensajeIn
from services.usuario import obtener_usuario_por_id  # importante
from db.mongodb import mensajes_collection_maestro, usuarios_collection_maestro
r = redis.Redis()

MAX_MENSAJES = 50

async def guardar_mensaje(data: MensajeIn, usuario_id: str) -> MensajeOut:
    fecha = datetime.utcnow()
    mensaje_id = str(uuid.uuid4())

    # Obtener username desde Mongo
    usuario = await usuarios_collection_maestro.find_one({"_id": usuario_id})
    if not usuario:
        raise Exception("Usuario no encontrado")

    mensaje_doc = {
        "_id": mensaje_id,
        "usuario_id": usuario_id,
        "sala_id": data.sala_id,
        "contenido": data.contenido,
        "fecha": fecha
    }

    await mensajes_collection_maestro.insert_one(mensaje_doc)

    return MensajeOut(
        id=mensaje_id,
        usuario_id=usuario_id,
        sala_id=data.sala_id,
        contenido=data.contenido,
        fecha=fecha.isoformat(),
        username=usuario["username"]
    )

async def obtener_mensajes(sala_id: str, limite: int = 50) -> list[MensajeOut]:
    cursor = mensajes_collection_maestro.find(
        {"sala_id": sala_id}
    ).sort("fecha", -1).limit(limite)

    mensajes = []
    async for doc in cursor:
        usuario = await usuarios_collection_maestro.find_one({"_id": doc["usuario_id"]})
        mensajes.append(MensajeOut(
            id=doc["_id"],
            usuario_id=doc["usuario_id"],
            sala_id=doc["sala_id"],
            contenido=doc["contenido"],
            fecha=doc["fecha"].isoformat(),
            username=usuario["username"] if usuario else "Desconocido"
        ))

    return list(reversed(mensajes))  # del más viejo al más nuevo


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

