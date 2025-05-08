from fastapi import APIRouter, HTTPException
from schemas.usuario import UsuarioCreate, UsuarioLogin
from services.usuario import crear_usuario, logiar_usuario
from utils.auth import crear_token
router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/login")
async def loginchafa():
    return {"message": "Inicio de sesión exitoso"}

@router.get("/registerchafa")
async def register():
    return {"message": "Registro exitoso"}

# routers/auth.py

@router.post("/register")
async def register(usuario: UsuarioCreate):
    try:
        nuevo_usuario = await crear_usuario(usuario)
        return {"mensaje": "Usuario registrado", "usuario": nuevo_usuario}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        

@router.post("/loginchafa")
async def loginchafa(usuario: UsuarioLogin):
    try:
        return await logiar_usuario(usuario)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(data: UsuarioLogin):
    usuario = await logiar_usuario(data)
    token = crear_token({"user_id": usuario.id})
    return {"access_token": token, "token_type": "bearer"}


