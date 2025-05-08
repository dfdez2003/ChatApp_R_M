from fastapi import APIRouter

router = APIRouter(prefix="/archivos", tags=["archivos"])


@router.get("/")
async def login():
    return {"message": "En archivos:)"}

