# mongo_transacciones.py

from db.mongodb import client as mongo_client, usuarios_collection, salas_collection
from datetime import datetime
from pymongo.errors import PyMongoError
from passlib.context import CryptContext
import uuid
from schemas.usuario import UsuarioCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def crear_usuario_y_sala_mongo(data: UsuarioCreate):
    usuario_id = str(uuid.uuid4())
    sala_id = str(uuid.uuid4())
    fecha_actual = datetime.utcnow()  # ❗ MANTENEMOS como datetime

    usuario_documento = {
        "_id": usuario_id,
        "username": data.username,
        "nombre": data.nombre,
        "surname": data.surname,
        "email": data.email,
        "password_hash": pwd_context.hash(data.password),
        "fecha_registro": fecha_actual,
    }

    sala_documento = {
        "_id": sala_id,
        "nombre": f"Sala de {data.username}",
        "descripcion": "Sala personal creada automáticamente",
        "creador_id": usuario_id,
        "es_publica": True,
        "password_hash": None,
        "fecha_creacion": fecha_actual,
        "miembros": [usuario_id],
    }

    try:
        async with await mongo_client.start_session() as session:
            async with session.start_transaction():
                await usuarios_collection.insert_one(usuario_documento, session=session)
                await salas_collection.insert_one(sala_documento, session=session)

        return {
            "ok": True,
            "usuario_id": usuario_id,
            "sala_id": sala_id,
            "fecha": fecha_actual,
            "password_hash": usuario_documento["password_hash"]
        }

    except PyMongoError as e:
        return {"ok": False, "error": str(e)}
