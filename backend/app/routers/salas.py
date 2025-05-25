# routers/salas.py

from fastapi import APIRouter, Depends, HTTPException
from schemas.sala import SalaCreate, ExpulsionData
from fastapi.responses import HTMLResponse, FileResponse
from services.sala import crear_sala, unirse_a_sala, mostrar_salas_propias, mostrar_salas_random, expulsar_usuario
from utils.auth import get_current_user  # esta función saca el user del token

from schemas.sala import UnirseSala

router = APIRouter(prefix="/salas", tags=["salas"])

@router.get("/", response_class=FileResponse)
async def get_salas_page():
    return "static/salas.html"



@router.post("/create")
async def crear_sala_endpoint(
    sala: SalaCreate,
    user = Depends(get_current_user)
):
    return await crear_sala(sala, user["id"])


# routers/salas.py
@router.post("/unirse")
async def unirse_sala(data: UnirseSala, user = Depends(get_current_user)):
    try:
        return await unirse_a_sala(data, user["id"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/mias")
async def salas_usuario(user = Depends(get_current_user)):
    try:
        return await mostrar_salas_propias(user["id"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    


@router.get("/salasrandom")
async def salas_random(user = Depends(get_current_user)):
    try:
        return await mostrar_salas_random(user["id"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/expulsar")
async def expulsar(data: ExpulsionData, user = Depends(get_current_user)):
    try:
        return await expulsar_usuario(data.sala_id, data.usuario_id, user["id"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
