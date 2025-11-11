import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import schemas.auth as schemas_auth
from config.database import db

SECRET_KEY = os.getenv("SECRET_KEY", "unallavesecretamuysegura_pordefecto")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ph = PasswordHasher()

def verify_password(plain_password, hashed_password):
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False
    except Exception:
        return False

def get_password_hash(password):
    return ph.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user(username: str):
    query = "SELECT * FROM usuarios WHERE username = :username"
    user = await db.fetch_one(query=query, values={"username": username})
    return user

async def register_new_user(usuario_data: schemas_auth.UsuarioCreate):
    hashed_password = get_password_hash(usuario_data.password)
    query = "INSERT INTO usuarios (username, hashed_password, rol) VALUES (:username, :hashed_password, 'usuario')"
    values = {"username": usuario_data.username, "hashed_password": hashed_password}
    try:
        user_id = await db.execute(query=query, values=values)
        user_data_out = usuario_data.model_dump(exclude={"password"})
        return {**user_data_out, "id": user_id, "rol": "usuario"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe.")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas_auth.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user