from pydantic import BaseModel
from datetime import datetime
import uuid

class Mensaje(BaseModel):
    id: str
    usuario_id: str
    sala_id: str
    contenido: str
    fecha: datetime
    
    class Config:
        orm_mode = True
