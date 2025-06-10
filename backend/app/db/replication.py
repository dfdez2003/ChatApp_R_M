import asyncio
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import PyMongoError

async def replicar_coleccion(coleccion_src: AsyncIOMotorCollection, coleccion_dst: AsyncIOMotorCollection):
    while True:
        
        try:
            
            async with coleccion_src.watch(full_document="updateLookup") as stream:
                async for cambio in stream:
                    op = cambio["operationType"]
                    doc = cambio.get("fullDocument")
                    id_ = cambio["documentKey"]["_id"]

                    if op == "insert":
                        await coleccion_dst.insert_one(doc)
                    elif op in ("update", "replace"):
                        await coleccion_dst.replace_one({"_id": id_}, doc, upsert=True)
                    elif op == "delete":
                        await coleccion_dst.delete_one({"_id": id_})

                    print(f"🔄 [{coleccion_src.name}] Replicado {op.upper()} -> {id_}")
        except PyMongoError as e:
            print(f"❌ Error replicando {coleccion_src.name}: {e}")
            await asyncio.sleep(5)  # espera antes de intentar de nuevo
