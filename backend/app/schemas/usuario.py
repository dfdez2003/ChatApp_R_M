from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Esquema para crear un nuevo usuario
class UsuarioCreate(BaseModel):
    nombre: str
    surname: str
    username: str
    email: EmailStr
    password: str

# Esquema para actualizar los datos del usuario
class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    surname: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    class Config:
        from_attributes = True

# Esquema para logiarse 
class UsuarioLogin(BaseModel):
    username: str
    password: str
    class Config:
        from_attributes = True

# Esquema para la respuesta que enviarás al cliente cuando creas un usuario / la que ira atravez de la red 
class UsuarioOut(BaseModel):
    id: str
    username: str
    nombre: str
    surname: str
    email: str
    fecha_registro: str
    class Config:
        from_attributes = True


