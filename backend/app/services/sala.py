# services/sala_service.py

import uuid
from datetime import datetime
from passlib.context import CryptContext
import redis.asyncio as redis

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
r = redis.Redis()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

async def crear_sala(data, creador_id: str):
    sala_id = str(uuid.uuid4())
    fecha = datetime.utcnow().isoformat()
    password_hash = hash_password(data.password) if data.password else ""

    # Proteger antes de usar HSET
    tipo_sala = await r.type(f"sala:{sala_id}")
    if tipo_sala != b"none" and tipo_sala != b"hash":
        raise Exception("Conflicto de tipo: la clave sala:{id} ya existe como otro tipo")

    await r.hset(f"sala:{sala_id}", mapping={
        "nombre": data.nombre,
        "creador_id": creador_id,
        "es_publica": int(data.es_publica),
        "password_hash": password_hash,
        "fecha_creacion": fecha,
        "tiempo_vida": data.tiempo_vida or 0
    })

    # Relación: agregar sala al usuario
    tipo_usuario = await r.type(f"usuario:{creador_id}:salas")
    if tipo_usuario != b"none" and tipo_usuario != b"set":
        raise Exception("Conflicto de tipo: la clave usuario:{id}:salas ya existe como otro tipo")
    
    await r.sadd(f"usuario:{creador_id}:salas", f"sala:{sala_id}")
    
    # Relación: agregar usuario a la sala
    tipo_sala_usuarios = await r.type(f"sala:{sala_id}:usuarios")
    if tipo_sala_usuarios != b"none" and tipo_sala_usuarios != b"set":
        raise Exception("Conflicto de tipo: la clave sala:{id}:usuarios ya existe como otro tipo")
    
    await r.sadd(f"sala:{sala_id}:usuarios", f"usuario:{creador_id}")

    return {
        "id": sala_id,
        "nombre": data.nombre,
        "creador_id": creador_id,
        "fecha_creacion": fecha,
        "es_publica": data.es_publica
    }

async def unirse_a_sala(data, user_id: str):
    sala_key = f"sala:{data.sala_id}"

    if not await r.exists(sala_key):
        raise Exception("La sala no existe")

    sala_data = await r.hgetall(sala_key)
    sala_dict = {k.decode(): v.decode() for k, v in sala_data.items()}

    if sala_dict["es_publica"] == "0":
        if not data.password:
            raise Exception("Se requiere contraseña")
        if not pwd_context.verify(data.password, sala_dict["password_hash"]):
            raise Exception("Contraseña incorrecta")

    ya_esta = await r.sismember(f"sala:{data.sala_id}:usuarios", f"usuario:{user_id}")
    if ya_esta:
        return {"mensaje": "Ya estás en la sala"}

    await r.sadd(f"sala:{data.sala_id}:usuarios", f"usuario:{user_id}")
    await r.sadd(f"usuario:{user_id}:salas", f"sala:{data.sala_id}")

    return {"mensaje": "Te uniste a la sala", "sala_id": data.sala_id}


async def mostrar_salas_propias(user_id: str):
    claves = await r.smembers(f"usuario:{user_id}:salas")
    salas = []
    for c in claves:
        sala_id = c.decode().split(":")[1] # Sale sale le vamos a quitar la palabbra sala: al identificador de la sala
        datos = await r.hgetall(f"sala:{sala_id}") # guardamos los datos de la sala en un dic
        if datos:
            sala = {k.decode(): v.decode() for k, v in datos.items()} # recorremos el dic item por item para "decodificarlo "
            sala["id"] = sala_id                                        #  Agregamos la clave valor del id: sale_id 
            salas.append(sala)                                        # Agregamos a la lista de discionarios ( cada dic es una  sala)

    return {"salas":salas}


async def mostrar_salas_random(user_id: str):
    salas = []
    async for k in r.scan_iter(match="sala:*"):
        if b":" in k and b"usuarios" not in k and b"mensajes" not in k:
            datos = await r.hgetall(k)
            if datos: 
                sala = {k.decode(): v.decode() for k, v in datos.items()}
                if sala.get("es_publica") == "1":
                    sala["id"] = k.decode().split(":")[1]
                    salas.append(sala)
    salas.sort(key = lambda x: x.get("fecha_creacion",""), reverse=True)
    return {"salas": salas[:5]}


async def expulsar_usuario(sala_id: str, usuario_a_expulsar: str, solicitante_id: str):
    datos = await r.hgetall(f"sala:{sala_id}")
    if not datos:
        raise Exception("La sala no existe")

    sala = {k.decode(): v.decode() for k, v in datos.items()}

    if sala["creador_id"] != solicitante_id:
        raise Exception("Solo el creador puede expulsar usuarios")

    await r.srem(f"sala:{sala_id}:usuarios", f"usuario:{usuario_a_expulsar}")
    await r.srem(f"usuario:{usuario_a_expulsar}:salas", f"sala:{sala_id}")

    return {"mensaje": f"Usuario expulsado de la sala {sala_id}"}
