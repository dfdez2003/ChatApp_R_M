# database/mongo.py

from motor.motor_asyncio import AsyncIOMotorClient
import os

#MAESTRO BD
MONGO_URI_MAESTRO = os.getenv("MONGO_URI", "mongodb+srv://ChatApp:chatapp123@cluster0.1qmak.mongodb.net/")
mongo_client_maestro = AsyncIOMotorClient(MONGO_URI_MAESTRO)
db_Maestro = mongo_client_maestro["ChatApp"]

#ESCLAVO BD
MONGO_URI_ESCLAVO = os.getenv("MONGO_URI", "mongodb+srv://ChatAppR1:chatapp1234@cluster0.1qmak.mongodb.net/")
mongo_client_esclavo = AsyncIOMotorClient(MONGO_URI_MAESTRO)
db_Esclavo = mongo_client_esclavo["ChatAppR1"]


# Exporta las colecciones de maestro para importarlas fácilmente
usuarios_collection_maestro = db_Maestro["usuarios"]
salas_collection_maestro = db_Maestro["salas"]
mensajes_collection_maestro = db_Maestro["mensajes"]

# Exporta las colecciones de esclavo para importarlas fácilmente
usuarios_collection_esclavo = db_Esclavo["usuarios"]
salas_collection_esclavo = db_Esclavo["salas"]
mensajes_collection_esclavo = db_Esclavo["mensajes"]

client_Maestro = mongo_client_maestro  # Exporta el cliente por si necesitas start_session()
client_Esclavo = mongo_client_esclavo
