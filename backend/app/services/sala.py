# services/sala_service.py

import uuid
from datetime import datetime
from passlib.context import CryptContext
import redis.asyncio as redis

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
r = redis.Redis()

#  Agregar un id de sala a el set de salas del usuario 
async def safe_add_sala_usuario(redis, usuario_id, sala_key): 
    key = f"usuario:{usuario_id}:salas"             # Set deciado para las salas del usuario    
    tipo = await redis.type(key)                    # Obtenemos el tipo actual de la clave en redis 
    if tipo != b"none" and tipo != b"set":          #  Verificamos, si es none o otro tipo que no sea set mandamos un esception
        raise Exception(f"Conflicto de tipo en {key}. Esperado SET, encontrado {tipo}")
    print(f"[DEBUG] Añadiendo sala {sala_key} al set {key}")
    await redis.sadd(key, sala_key)                 # si esta todo correcto agregamos la clave al set de salas 

# Agregar un id de usuario a el set de usuarios de la sala 
async def safe_add_usuario_sala(redis, sala_id,usuario_key):
    key = f"sala:{sala_id}:usuarios"                     # definimos nuestro set de usuarios 
    tipo = await redis.type(key)                        # Obtenemos el tipo actual de la clave 
    if tipo != b"none" and tipo != b"set":              # Si es diferente de none o de un tipo que sea no set mandamos el exc  
        raise Exception(f"Conflicto de tipo en {key}. Esperado SET, encontrado {tipo}")
    print(f"[DEBUG] Añadiendo usuario {usuario_key} al set {key}")
    await redis.sadd(key, usuario_key)

async def safe_srem(redis, key: str, member: str):
    # Verificar si el miembro existe en el conjunto antes de removerlo
    existe = await redis.sismember(key, member)
    if existe:
        await redis.srem(key, member)
    else:
        print(f"Advertencia: {member} no existe en {key}, no se puede eliminar de Redis.")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Crear sala blindado
async def crear_sala(data, creador_id: str):
    # 🆔 Generamos un ID único para la sala
    sala_id = str(uuid.uuid4())
    fecha = datetime.utcnow().isoformat()
    password_hash = hash_password(data.password) if data.password else ""

    sala_hash_key = f"sala:{sala_id}"
    sala_usuarios_key = f"sala:{sala_id}:usuarios"
    usuario_salas_key = f"usuario:{creador_id}:salas"
    usuario_key = f"usuario:{creador_id}"

    print(f"[DEBUG] Iniciando creación de sala {sala_id}")
    print(f"[DEBUG] -> HSET en {sala_hash_key}")
    print(f"[DEBUG] -> SET de usuarios en {sala_usuarios_key}")
    print(f"[DEBUG] -> SET de salas del usuario en {usuario_salas_key}")

    # ✅ Validar que no exista otra clave con tipo incompatible
    tipo_sala = await r.type(sala_hash_key)
    if tipo_sala != b"none" and tipo_sala != b"hash":
        raise Exception(f"Conflicto de tipo: {sala_hash_key} ya existe como {tipo_sala}")

    # 📝 Crear sala como HASH
    await r.hset(sala_hash_key, mapping={
        "nombre": data.nombre,
        "creador_id": creador_id,
        "es_publica": int(data.es_publica),
        "password_hash": password_hash,
        "fecha_creacion": fecha,
        "tiempo_vida": data.tiempo_vida or 0
    })

    # ✅ Agregar la sala al set del usuario (relación inversa)
    tipo_user_salas = await r.type(usuario_salas_key)
    if tipo_user_salas != b"none" and tipo_user_salas != b"set":
        raise Exception(f"Conflicto de tipo en {usuario_salas_key}: tipo {tipo_user_salas}")
    await r.sadd(usuario_salas_key, sala_hash_key)
    print(f"[DEBUG] Añadida sala a {usuario_salas_key} → {sala_hash_key}")

    # ✅ Agregar el usuario al set de usuarios de la sala
    tipo_sala_usuarios = await r.type(sala_usuarios_key)
    if tipo_sala_usuarios != b"none" and tipo_sala_usuarios != b"set":
        raise Exception(f"Conflicto de tipo en {sala_usuarios_key}: tipo {tipo_sala_usuarios}")
    await r.sadd(sala_usuarios_key, usuario_key)
    print(f"[DEBUG] Añadido usuario a {sala_usuarios_key} → {usuario_key}")

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

    # Verificación para salas privadas (con contraseña)
    if sala_dict["es_publica"] == "0":
        if not data.password:
            raise Exception("Se requiere contraseña")
        if not pwd_context.verify(data.password, sala_dict["password_hash"]):
            raise Exception("Contraseña incorrecta")

    # Verificación si el usuario ya está en la sala
    ya_esta = await r.sismember(f"sala:{data.sala_id}:usuarios", f"usuario:{user_id}")
    if ya_esta:
        return {"mensaje": "Ya estás en la sala"}

    # Agregar la sala al set de salas del usuario y el usuario al set de usuarios de la sala
    await safe_add_sala_usuario(r, user_id, f"sala:{data.sala_id}")
    await safe_add_usuario_sala(r, data.sala_id, f"usuario:{user_id}")

    return {"mensaje": "Te uniste a la sala", "sala_id": data.sala_id}


#  Expulsar usuario blindado
async def expulsar_usuario(sala_id: str, usuario_a_expulsar: str, solicitante_id: str):
    datos = await r.hgetall(f"sala:{sala_id}")
    if not datos:
        raise Exception("La sala no existe")

    sala = {k.decode(): v.decode() for k, v in datos.items()}

    if sala["creador_id"] != solicitante_id:
        raise Exception("Solo el creador puede expulsar usuarios")

    # Validación segura antes de remover
    await safe_srem(r, f"sala:{sala_id}:usuarios", f"usuario:{usuario_a_expulsar}")
    await safe_srem(r, f"usuario:{usuario_a_expulsar}:salas", f"sala:{sala_id}")

    return {"mensaje": f"Usuario expulsado de la sala {sala_id}"}

#  Mostrar salas propias (sin riesgo de corrupción)
async def mostrar_salas_propias(user_id: str):
    claves = await r.smembers(f"usuario:{user_id}:salas")
    salas = []
    for c in claves:
        sala_id = c.decode().split(":")[1]
        datos = await r.hgetall(f"sala:{sala_id}")
        if datos:
            sala = {k.decode(): v.decode() for k, v in datos.items()}
            sala["id"] = sala_id
            salas.append(sala)
    return {"salas": salas}

#  Mostrar salas públicas aleatorias (sin riesgo de corrupción)
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
    salas.sort(key=lambda x: x.get("fecha_creacion", ""), reverse=True)
    return {"salas": salas}

async def obtener_usuario(user_id: str):
    """
    Obtiene los datos de un usuario específico de manera segura.
    Solo accede a la clave usuario:id_user y valida el tipo de dato.
    
    Args:
        user_id (str): ID del usuario a obtener
        
    Returns:
        dict: Datos del usuario o None si no existe
    Raises:
        Exception: Si hay conflicto de tipos de datos
    """
    user_key = f"usuario:{user_id}"
    
    # Verificar el tipo de dato primero
    key_type = await r.type(user_key)
    
    # Solo permitimos hash o none (si no existe)
    if key_type != b"none" and key_type != b"hash":
        raise Exception(f"Conflicto de tipo en {user_key}. Esperado HASH, encontrado {key_type}")
    
    # Si no existe, retornar None
    if key_type == b"none":
        return None
    
    # Obtener todos los campos del hash
    user_data = await r.hgetall(user_key)
    
    # Convertir bytes a strings
    decoded_data = {k.decode(): v.decode() for k, v in user_data.items()}
    
    # Añadir el ID del usuario al resultado
    decoded_data["id"] = user_id
    
    return decoded_data