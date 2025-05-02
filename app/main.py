from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, salas, mensajes, archivos
from fastapi.staticfiles import StaticFiles

from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Configuración de CORS para permitir solicitudes desde otros orígenes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O puedes especificar un origen en particular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos (por si deseas permitir la subida de archivos, imágenes, etc.)
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Incluir las rutas
app.include_router(auth.router)  # Rutas para autenticación
app.include_router(salas.router)  # Rutas para gestionar salas
app.include_router(mensajes.router)  # Rutas para mensajes
app.include_router(archivos.router)  # Rutas para archivos

app.mount("/static",StaticFiles(directory="static"), name= "static")




# WebSockets: cuando un cliente se conecta, se gestiona en esta ruta
@app.websocket("/ws/chat/{room_name}")
async def websocket_endpoint(websocket: WebSocket, room_name: str):
    await websocket.accept()
    # Aquí gestionamos los mensajes entrantes y salientes de la sala
    try:
        while True:
            data = await websocket.receive_text()  # Recibe mensaje
            await websocket.send_text(f"Mensaje recibido: {data}")  # Envía respuesta
    except WebSocketDisconnect:
        print(f"Cliente desconectado de la sala {room_name}")




@app.get("/")
async def get():
    return {"Message":"Hi"}