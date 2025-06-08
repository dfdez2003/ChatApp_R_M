from pydantic import BaseModel
from datetime import datetime

class UsuarioEnSala(BaseModel):
    usuario_id: str
    sala_id: str
    fecha_union: datetime = datetime.now()

    class Config:
        from_attributes = True

