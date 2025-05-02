# schemas/mensaje.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MensajeIn(BaseModel):
    sala_id: str
    contenido: str

class MensajeOut(BaseModel):
    id: str
    usuario_id: str
    sala_id: str
    contenido: str
    fecha: datetime

    class Config:
        from_attributes = True

class MensajeEdit(BaseModel):
    sala_id: str
    mensaje_id: str
    nuevo_contenido: str

class MensajeDelete(BaseModel):
    sala_id: str
    mensaje_id: str
