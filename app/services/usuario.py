# services/usuario_service.py

import uuid
from datetime import datetime
from passlib.context import CryptContext    # sale sale libreria para hash
from schemas.usuario import UsuarioOut
import redis.asyncio as redis

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # hash 
r = redis.Redis()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

async def crear_usuario(data):
    async for key in r.scan_iter(match="usuario:*"):
        email = await r.hget(key, "email")
        if email and email.decode() == data.email:
            raise Exception("Correo ya registrado")

    usuario_id = str(uuid.uuid4())
    fecha = datetime.utcnow().isoformat()
    hashed = hash_password(data.password)

    await r.hset(f"usuario:{usuario_id}", mapping={
        "nombre": data.nombre,
        "surname": data.surname,
        "username": data.username,
        "email": data.email,
        "password_hash": hashed,
        "fecha_registro": fecha
    })

    return {
        "id": usuario_id,
        "nombre": data.nombre,
        "email": data.email,
        "fecha_registro": fecha
    }

    


async def logiar_usuario(data):  # data tiene: username, password
    async for key in r.scan_iter(match="usuario:*"):
        tipo = await r.type(key)
        
        if tipo != b"hash":
            continue  

        username = await r.hget(key, "username")
        if username and username.decode() == data.username:
            password_hash = await r.hget(key, "password_hash")
            if password_hash and pwd_context.verify(data.password, password_hash.decode()):
                datos = await r.hgetall(key)
                usuario_dict = {k.decode(): v.decode() for k, v in datos.items()}

                usuario_out_data = {
                    "id": key.decode().split(":")[1],
                    "nombre": usuario_dict.get("nombre"),
                    "surname": usuario_dict.get("surname"),
                    "username": usuario_dict.get("username"),
                    "email": usuario_dict.get("email"),
                    "fecha_registro": usuario_dict.get("fecha_registro"),
                }

                return UsuarioOut(**usuario_out_data)

    raise Exception("Usuario o contraseña incorrectos")
