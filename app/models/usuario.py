from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid

class Usuario(BaseModel):
    id: str
    nombre: str
    surname: str
    username: str
    email: EmailStr
    password_hash: str
    fecha_registro: datetime
    
    class Config:
        orm_mode = True


