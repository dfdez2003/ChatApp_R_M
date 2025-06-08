from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SalaCreate(BaseModel):
    nombre: str
    es_publica: bool = True
    password: Optional[str] = None
    tiempo_vida: int = Field(ge=1, le=72, default=2)
    descripcion: Optional[str] = None
    class Config:
        from_attributes = True

class SalaUpdate(BaseModel):
    nombre: Optional[str] = None
    es_publica: Optional[bool] = None
    password: Optional[str] = None
    tiempo_vida: Optional[int] = None
    descripcion: Optional[str] = None
    class Config:
        from_attributes = True

class SalaOut(BaseModel):
    id: str
    nombre: str
    creador_id: str
    es_publica: bool
    fecha_creacion: datetime
    tiempo_vida: Optional[int]
    descripcion: Optional[str] = None
    class Config:
        from_attributes = True


class UnirseSala(BaseModel):
    sala_id: str
    password: Optional[str] = None
    class Config:
        from_attributes = True


class ExpulsionData(BaseModel):
    sala_id: str
    usuario_id: str
    class Config:
        from_attributes = True
