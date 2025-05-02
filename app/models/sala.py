from pydantic import BaseModel
from datetime import datetime
import uuid
from typing import Optional

class Sala(BaseModel):
    id: str
    nombre: str
    creador_id: str
    es_publica: bool
    password_hash: Optional[str]
    fecha_creacion: datetime
    tiempo_vida: Optional[int]

    class Config:
        orm_mode = True

