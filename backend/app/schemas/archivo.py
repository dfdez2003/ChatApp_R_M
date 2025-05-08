from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ArchivoCreate(BaseModel):
    nombre_archivo: str
    ruta: str
    tipo_mime: Optional[str]
    tamaño: Optional[int]

class ArchivoOut(BaseModel):
    id: str
    sala_id: str
    usuario_id: str
    nombre_archivo: str
    ruta: str
    tipo_mime: Optional[str]
    tamaño: Optional[int]
    fecha: datetime

    class Config:
        orm_mode = True
