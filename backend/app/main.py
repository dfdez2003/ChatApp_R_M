from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, salas, mensajes, archivos
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuración de CORS para permitir solicitudes desde otros orígenes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O puedes especificar un origen en particular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas
app.include_router(auth.router)  # Rutas para autenticación
app.include_router(salas.router)  # Rutas para gestionar salas
app.include_router(mensajes.router)  # Rutas para mensajes
app.include_router(archivos.router)  # Rutas para archivos



app.mount("/static", StaticFiles(directory="static"), name="static")
# Ruta para la página principal (index)


# Ruta para login
@app.get("/login")
async def read_login():
    return FileResponse("static/login.html")

# Ruta para registro
@app.get("/registro")
async def read_registro():
    return FileResponse("static/registro.html")


