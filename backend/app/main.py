from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, salas, mensajes, archivos, websockets
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.responses import RedirectResponse
import asyncio

from utils.limpieza_salas import tarea_limpieza_salas

# 👉 Importaciones para replicación
from db.mongodb import colecciones  # asegúrate de que mongo.py esté correctamente importado
from db.replication import replicar_coleccion  # script con tu lógica de Change Streams

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.get("/login")
async def redirect_login():
    return RedirectResponse(url="/auth/login")

@app.get("/")
async def redirect_register():
    return RedirectResponse(url="/auth/register")

@app.get("/register")
async def redirect_login():
    return RedirectResponse(url="/auth/register")

@app.on_event("startup")
async def iniciar_tareas_background():
    # 🧼 Tarea de limpieza de salas
    asyncio.create_task(tarea_limpieza_salas())

    # 🔁 Tareas de replicación para cada colección
    for src, dst in colecciones.values():
        asyncio.create_task(replicar_coleccion(src, dst))

# Rutas de la API
app.include_router(auth.router)
app.include_router(salas.router)
app.include_router(mensajes.router)
app.include_router(archivos.router)
app.include_router(websockets.router)
