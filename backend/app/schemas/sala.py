from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SalaCreate(BaseModel):
    nombre: str
    es_publica: bool = True
    password: Optional[str] = None
    tiempo_vida: Optional[int] = None

class SalaUpdate(BaseModel):
    nombre: Optional[str] = None
    es_publica: Optional[bool] = None
    password: Optional[str] = None
    tiempo_vida: Optional[int] = None

class SalaOut(BaseModel):
    id: str
    nombre: str
    creador_id: str
    es_publica: bool
    fecha_creacion: datetime
    tiempo_vida: Optional[int]

    class Config:
        orm_mode = True

class UnirseSala(BaseModel):
    sala_id: str
    password: Optional[str] = None


class ExpulsionData(BaseModel):
    sala_id: str
    usuario_id: str