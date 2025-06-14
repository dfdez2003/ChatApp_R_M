# mongo_transacciones.py

from db.mongodb import client_Maestro as mongo_client_maestro, usuarios_collection_maestro, salas_collection_maestro, mensajes_collection_maestro
from datetime import datetime
from services.historial import guardar_historial_sala

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
    }

    try:
        async with await mongo_client_maestro.start_session() as session:
            async with session.start_transaction():
                await usuarios_collection_maestro.insert_one(usuario_documento, session=session)
                await salas_collection_maestro.insert_one(sala_documento, session=session)

        return {
            "ok": True,
            "usuario_id": usuario_id,
            "sala_id": sala_id,
            "fecha": fecha_actual,
            "password_hash": usuario_documento["password_hash"]
        }

    except PyMongoError as e:
        return {"ok": False, "error": str(e)}



async def migrar_sala_a_historial(sala_id: str):
    try:
        async with await mongo_client_maestro.start_session() as session:
            async with session.start_transaction():
                sala = await salas_collection_maestro.find_one({"_id": sala_id}, session=session)
                if not sala:
                    raise Exception(f"Sala {sala_id} no encontrada")

                mensajes_cursor = mensajes_collection_maestro.find({"sala_id": sala_id}, session=session)
                mensajes = await mensajes_cursor.to_list(length=None)

                # Guardar en historial (fuera del bloque atomic si no queremos rollback)
                await guardar_historial_sala(sala, mensajes)

                # Eliminar sala y mensajes originales
                await salas_collection_maestro.delete_one({"_id": sala_id}, session=session)
                await mensajes_collection_maestro.delete_many({"sala_id": sala_id}, session=session)

    except PyMongoError as e:
        raise Exception(f"Error en transacción MongoDB: {str(e)}")
