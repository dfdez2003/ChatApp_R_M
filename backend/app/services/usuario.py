# services/usuario_service.py

import uuid
from datetime import datetime
from passlib.context import CryptContext
from schemas.usuario import UsuarioOut, UsuarioCreate, UsuarioLogin
import redis.asyncio as redis
import logging
from fastapi import HTTPException
from db.mongodb import usuarios_collection_maestro
from services.transaccion import crear_usuario_y_sala_mongo
from  services.sala import crear_sala_redis

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
r = redis.Redis()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

async def crear_usuario(data):
    data_obj = UsuarioCreate(**data.dict()) if hasattr(data, "dict") else UsuarioCreate(**data)

    # Verificar correo duplicado
    existing = await usuarios_collection_maestro.find_one({"email": data_obj.email})
    if existing:
        raise Exception("Correo ya registrado")

    # Ejecutar transacción MongoDB
    resultado = await crear_usuario_y_sala_mongo(data_obj)
    if not resultado["ok"]:
        raise Exception("Error al crear usuario en MongoDB")

    usuario_id = resultado["usuario_id"]
    sala_id = resultado["sala_id"]
    fecha = resultado["fecha"]
    hashed = resultado["password_hash"]

    # Redis: Crear usuario
    usuario_hash_key = f"usuario:{usuario_id}"
    tipo = await r.type(usuario_hash_key)
    if tipo != b"none" and tipo != b"hash":
        raise Exception(f"Conflicto de tipo en {usuario_hash_key}. Ya existe como {tipo.decode()}")

    await r.hset(usuario_hash_key, mapping={
        "nombre": data_obj.nombre,
        "surname": data_obj.surname,
        "username": data_obj.username,
        "email": data_obj.email,
        "password_hash": hashed,
        "fecha_registro": fecha.isoformat()  # ✅ Aquí sí lo convertimos
    })

    # Redis: Crear sala
    await crear_sala_redis(
        sala_id=sala_id,
        nombre="Sala personal",
        descripcion=f"Sala de {data_obj.username}",
        creador_id=usuario_id,
        es_publica=True,
        password_hash="",
        tiempo_vida_segundos=7200,
        fecha_creacion=fecha,  # ✅ Pasa como datetime
        usuarios=[usuario_id]
    )

    logger.info(f"[DEBUG] Usuario y sala creados en Redis y Mongo: {usuario_id} | Sala: {sala_id}")

    return {
        "id": usuario_id,
        "nombre": data_obj.nombre,
        "email": data_obj.email,
        "fecha_registro": fecha.isoformat()
    }

async def logiar_usuario(data: UsuarioLogin):
    usuario = await usuarios_collection_maestro.find_one({"username": data.username})
    if not usuario:
        raise Exception("Usuario o contraseña incorrectos")

    if not pwd_context.verify(data.password, usuario["password_hash"]):
        raise Exception("Usuario o contraseña incorrectos")

    usuario_out_data = {
        "id": usuario["_id"],
        "nombre": usuario["nombre"],
        "surname": usuario["surname"],
        "username": usuario["username"],
        "email": usuario["email"],
        "fecha_registro": usuario["fecha_registro"].isoformat()
            if isinstance(usuario["fecha_registro"], datetime)
            else usuario["fecha_registro"]
    }

    logger.debug(f"[DEBUG] Usuario autenticado: {usuario_out_data}")
    return UsuarioOut(**usuario_out_data)


async def obtener_usuario_por_id(usuario_id: str) -> UsuarioOut:
    try:
        usuario = await usuarios_collection_maestro.find_one({"_id": usuario_id})
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        usuario_out_data = {
            "id": usuario["_id"],
            "nombre": usuario["nombre"],
            "surname": usuario["surname"],
            "username": usuario["username"],
            "email": usuario["email"],
            "fecha_registro": usuario["fecha_registro"].isoformat() if isinstance(usuario["fecha_registro"], datetime) else usuario["fecha_registro"]
        }

        return UsuarioOut(**usuario_out_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuario: {str(e)}")
