from pydantic import BaseModel
from datetime import datetime
import uuid
from typing import Optional

class Archivo(BaseModel):
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
