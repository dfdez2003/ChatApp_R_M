# services/sala_service.py

import uuid
from datetime import datetime
from passlib.context import CryptContext
import redis.asyncio as redis
from fastapi import HTTPException
from db.mongodb import salas_collection, mensajes_collection
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
    sala_id = str(uuid.uuid4())
    fecha = datetime.utcnow().isoformat()
    password_hash = hash_password(data.password) if data.password else ""
    es_publica = "0" if password_hash else "1"

    sala_hash_key = f"sala:{sala_id}"
    sala_usuarios_key = f"sala:{sala_id}:usuarios"
    usuario_salas_key = f"usuario:{creador_id}:salas"
    usuario_key = f"usuario:{creador_id}"

    print(f"[DEBUG] Iniciando creación de sala {sala_id}")

    # === Inserción MongoDB ===
    mongo_data = {
        "_id": sala_id,
        "nombre": data.nombre,
        "descripcion": data.descripcion or "",
        "tiempo_vida": int(data.tiempo_vida) if data.tiempo_vida else 2,
        "creador_id": creador_id,
        "es_publica": es_publica == "1",
        "password_hash": password_hash,
        "fecha_creacion": datetime.utcnow()
    }

    try:
        await salas_collection.insert_one(mongo_data)
        print(f"[DEBUG] Sala insertada en MongoDB: {sala_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al insertar en MongoDB: {str(e)}")

    # === Validación e Inserción Redis ===
    tipo_sala = await r.type(sala_hash_key)
    if tipo_sala != b"none" and tipo_sala != b"hash":
        raise Exception(f"Conflicto de tipo: {sala_hash_key} ya existe como {tipo_sala}")

    await r.hset(sala_hash_key, mapping={
        "nombre": data.nombre,
        "descripcion": data.descripcion or "",
        "tiempo_vida": str(data.tiempo_vida) if data.tiempo_vida else "0",
        "creador_id": creador_id,
        "es_publica": es_publica,
        "password_hash": password_hash,
        "fecha_creacion": fecha,
    })

    await safe_add_sala_usuario(r, creador_id, sala_hash_key)
    await safe_add_usuario_sala(r, sala_id, usuario_key)

    try:
        segundos = int(data.tiempo_vida or 2) * 3600
        await r.expire(sala_hash_key, segundos)
        await r.expire(sala_usuarios_key, segundos)
        await r.expire(f"sala:{sala_id}:mensajes", segundos)
        print(f"[DEBUG] TTL de sala establecido a {segundos} segundos")
    except Exception as e:
        print(f"[ERROR] No se pudo establecer TTL: {str(e)}")

    return {
        "id": sala_id,
        "nombre": data.nombre,
        "creador_id": creador_id,
        "fecha_creacion": fecha,
        "es_publica": es_publica == "1"
    }


async def unirse_a_sala(data, user_id: str):
    sala_key = f"sala:{data.sala_id}"

    if not await r.exists(sala_key):
        raise HTTPException(status_code=404, detail="La sala no existe")

    sala_data = await r.hgetall(sala_key)
    sala_dict = {k.decode(): v.decode() for k, v in sala_data.items()}

    if sala_dict.get("es_publica") == "0":
        if not data.password:
            raise HTTPException(status_code=403, detail="Se requiere contraseña")
        if not pwd_context.verify(data.password, sala_dict.get("password_hash", "")):
            raise HTTPException(status_code=403, detail="Contraseña incorrecta")

    ya_esta = await r.sismember(f"sala:{data.sala_id}:usuarios", f"usuario:{user_id}")
    if ya_esta:
        return {"mensaje": "Ya estás en la sala"}

    await safe_add_sala_usuario(r, user_id, f"sala:{data.sala_id}")
    await safe_add_usuario_sala(r, data.sala_id, f"usuario:{user_id}")

    # Añadir usuario a la sala
    await salas_collection.update_one(
        {"_id": data.sala_id},
        {"$addToSet": {"usuarios": user_id}}
    )

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
            #Obtener TTL en segundos
            ttl = await r.ttl(f"sala:{sala_id}")
            sala["tiempo_restante"] = ttl if ttl > 0 else None  # Si no tiene TTL, se asume permanente
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
                # if sala.get("es_publica") == "1":
                sala_id = k.decode().split(":")[1]
                sala["id"] = sala_id
                # Obtener TTL en segundos
                ttl = await r.ttl(f"sala:{sala_id}")
                sala["tiempo_restante"] = ttl if ttl > 0 else None

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


async def eliminar_sala_completa(sala_id: str, solicitante_id: str):
    """
    Elimina una sala completamente y todas sus referencias si el solicitante es el creador.
    Se elimina de Redis (tiempo real) y MongoDB (persistencia).
    """
    sala_key = f"sala:{sala_id}"
    datos_sala = await r.hgetall(sala_key)
    
    if not datos_sala:
        raise Exception("La sala no existe")

    sala = {k.decode(): v.decode() for k, v in datos_sala.items()}
    
    if sala["creador_id"] != solicitante_id:
        raise Exception("Solo el creador puede eliminar la sala")

    try:
        # 1. Redis: eliminar referencias cruzadas
        sala_usuarios_key = f"sala:{sala_id}:usuarios"
        usuarios = await r.smembers(sala_usuarios_key)

        for usuario_bytes in usuarios:
            usuario_id = usuario_bytes.decode().split(":")[1]
            usuario_salas_key = f"usuario:{usuario_id}:salas"
            await safe_srem(r, usuario_salas_key, sala_key)
            print(f"✅ Eliminada referencia de sala en usuario {usuario_id}")

        await r.delete(sala_usuarios_key)
        await r.delete(f"sala:{sala_id}:mensajes")
        await r.delete(sala_key)
        print(f"✅ Sala {sala_id} eliminada completamente de Redis")

        # 2. MongoDB: eliminar documento de la sala
        resultado = await salas_collection.delete_one({"_id": sala_id})
        if resultado.deleted_count:
            print(f"✅ Documento de sala eliminado en MongoDB: {sala_id}")
        else:
            print(f"⚠️ Sala no encontrada en MongoDB con _id: {sala_id}")

        # 3. MongoDB: eliminar mensajes relacionados con esa sala (si aplicas esa colección)
        result_msg = await mensajes_collection.delete_many({"sala_id": sala_id})
        print(f"✅ Eliminados {result_msg.deleted_count} mensajes en MongoDB")

        return {
            "mensaje": "Sala eliminada completamente",
            "sala_id": sala_id,
            "usuarios_afectados": len(usuarios)
        }

    except Exception as e:
        print(f"❌ Error eliminando sala: {str(e)}")
        raise Exception(f"Error al eliminar la sala: {str(e)}")


async def obtener_detalles_sala(sala_id: str):
    """
    Obtiene todos los detalles de una sala específica.
    
    Args:
        sala_id (str): ID de la sala a consultar
        
    Returns:
        dict: Datos completos de la sala
    Raises:
        Exception: Si la sala no existe
    """
    sala_key = f"sala:{sala_id}"
    
    # Verificar que la sala existe
    datos = await r.hgetall(sala_key)
    if not datos:
        raise Exception("La sala no existe")
    
    # Convertir los datos de bytes a un diccionario
    sala = {k.decode(): v.decode() for k, v in datos.items()}
    
    # Añadir el ID de la sala al resultado
    sala["id"] = sala_id
    
    # Convertir valores booleanos y numéricos
    sala["es_publica"] = sala["es_publica"] == "1"
    if "tiempo_vida" in sala:
        sala["tiempo_vida"] = int(sala["tiempo_vida"]) if sala["tiempo_vida"] else None
    
    # Eliminar datos sensibles
    if "password_hash" in sala:
        del sala["password_hash"]
        # Obtener TTL restante en segundos
    ttl = await r.ttl(sala_key)

    if ttl >= 0:
        sala["tiempo_restante"] = ttl
    else:
        sala["tiempo_restante"] = None  # No tiene expiración activa


    return sala


async def crear_sala_redis(
    sala_id: str,
    nombre: str,
    descripcion: str,
    creador_id: str,
    es_publica: bool,
    password_hash: str,
    tiempo_vida_segundos: int,
    fecha_creacion: datetime,
    usuarios: list
):
    sala_key = f"sala:{sala_id}"
    sala_usuarios_key = f"sala:{sala_id}:usuarios"
    creador_salas_key = f"usuario:{creador_id}:salas"

    # Hash principal
    await r.hset(sala_key, mapping={
        "nombre": nombre,
        "descripcion": descripcion,
        "tiempo_vida": str(tiempo_vida_segundos),
        "creador_id": creador_id,
        "es_publica": "1" if es_publica else "0",
        "password_hash": password_hash,
        "fecha_creacion": fecha_creacion.isoformat()
    })

    # Agregar usuarios al set de la sala
    for uid in usuarios:
        await r.sadd(sala_usuarios_key, f"usuario:{uid}")
        await r.sadd(f"usuario:{uid}:salas", sala_key)

    # Establecer expiración
    await r.expire(sala_key, tiempo_vida_segundos)
    await r.expire(sala_usuarios_key, tiempo_vida_segundos)
    await r.expire(f"sala:{sala_id}:mensajes", tiempo_vida_segundos)

    return {"mensaje": "Sala creada en Redis", "sala_id": sala_id}
