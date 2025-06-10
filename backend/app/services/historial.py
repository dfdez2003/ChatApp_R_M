# services/historial_service.py

from db.mongodb import historial_collection
from datetime import datetime

async def guardar_historial_sala(sala: dict, mensajes: list[dict]):
    documento = {
        "sala_id": sala["_id"],
        "nombre": sala["nombre"],
        "descripcion": sala.get("descripcion"),
        "creador_id": sala["creador_id"],
        "es_publica": sala["es_publica"],
        "fecha_creacion": sala["fecha_creacion"],
        "fecha_expiracion": datetime.utcnow().isoformat(),
        "mensajes": mensajes  # lista de objetos mensaje anidados
    }
    await historial_collection.insert_one(documento)
