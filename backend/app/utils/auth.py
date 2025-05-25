from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from db.redis import get_redis_connection
SECRET_KEY = "tu_clave_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # <- esto es importante

# Modelo para los datos dentro del token
class TokenData(BaseModel):
    username: str | None = None
    id: str | None = None


def crear_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    cred_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return {"id": user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")



# Función manual para WebSocket u otros usos
async def verificar_token_ws(token: str):
    cred_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o no autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise cred_error

        # Si quieres cargar datos del usuario desde Redis (opcional)
        r = await get_redis_connection()
        datos = await r.hgetall(f"usuario:{user_id}")
        if not datos:
            return {"id": user_id, "username": "Usuario"}  # fallback

        datos_decodificados = {k.decode(): v.decode() for k, v in datos.items()}
        return {"id": user_id, **datos_decodificados}

    except JWTError:
        raise cred_error