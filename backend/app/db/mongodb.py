# database/mongo.py

from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://ChatApp:chatapp123@cluster0.1qmak.mongodb.net/")
mongo_client = AsyncIOMotorClient(MONGO_URI)

db = mongo_client["ChatApp"]

# Exporta las colecciones para importarlas fácilmente
usuarios_collection = db["usuarios"]
salas_collection = db["salas"]
mensajes_collection = db["mensajes"]
historial_collection = db["historial"]
client = mongo_client  # Exporta el cliente por si necesitas start_session()
