# schemas/mensaje.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MensajeIn(BaseModel):
    sala_id: str
    contenido: str
    
    class Config:
        from_attributes = True


class MensajeOut(BaseModel):
    id: str
    usuario_id: str
    sala_id: str
    contenido: str
    fecha: str
    username: str

    class Config:
        from_attributes = True

class MensajeEdit(BaseModel):
    sala_id: str
    mensaje_id: str
    nuevo_contenido: str
    class Config:
        from_attributes = True


class MensajeDelete(BaseModel):
    sala_id: str
    mensaje_id: str
    class Config:
        from_attributes = True


class Mensaje(BaseModel):
    usuario_id: str
    username: str
    contenido: str
    timestamp: str  # ISO string

    def to_dict(self):
        return self.dict()

    def to_json(self):
        return self.model_dump_json()
    
    class Config:
        from_attributes = True
