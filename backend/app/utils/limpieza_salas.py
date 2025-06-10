import redis.asyncio as redis
import asyncio
from services.transacciones import migrar_sala_a_historial
r = redis.Redis()

async def limpiar_sala_completa(sala_id: str):
    print(f"🧹 Limpiando datos de sala {sala_id}...")

    sala_key = f"sala:{sala_id}"
    mensajes_key = f"sala:{sala_id}:mensajes"
    usuarios_key = f"sala:{sala_id}:usuarios"

    # Eliminar claves principales
    await r.delete(sala_key)
    await r.delete(mensajes_key)
    await r.delete(usuarios_key)

    # Eliminar referencia en cada usuario
    async for usuario_salas_key in r.scan_iter("usuario:*:salas"):
        await r.srem(usuario_salas_key, sala_key)

    # Eliminar de salas:activas
    await r.srem("salas:activas", sala_key)

    print(f"✅ Sala {sala_id} completamente eliminada.")


async def tarea_limpieza_salas():
    while True:
        print("🔄 Ejecutando limpieza de salas expiradas...")

        try:
            ids_activas = await r.smembers("salas:activas")
            for key in ids_activas:
                key_str = key.decode()
                sala_id = key_str.split(":")[1]

                existe = await r.exists(f"sala:{sala_id}")
                if existe == 0:  # ya expiró

                    print(f"⚠️ Sala {sala_id} ya no existe en Redis. Procediendo con limpieza...")

                    # Limpiar claves relacionadas en Redis
                    await r.delete(f"sala:{sala_id}:mensajes")
                    await r.srem("salas:activas", f"sala:{sala_id}")

                    # Limpiar de usuarios
                    async for usuario_key in r.scan_iter("usuario:*:salas"):
                        await r.srem(usuario_key, f"sala:{sala_id}")

                    # Ejecutar transacción MongoDB
                    try:
                        await migrar_sala_a_historial(sala_id)
                        print(f"✅ Sala {sala_id} migrada a historial y eliminada de MongoDB.")
                    except Exception as e:
                        print(f"❌ Error al migrar a historial MongoDB: {e}")

        except Exception as e:
            print(f"❌ Error en limpieza periódica: {e}")

        await asyncio.sleep(60)

