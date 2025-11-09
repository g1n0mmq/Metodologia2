import os
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

# --- 1. CAMBIO: Importamos argon2 directamente ---
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
# --- (Quitamos 'passlib.context') ---

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from . import models, schemas
from .db import get_session

# --- (Configuración de Seguridad - sin cambios) ---
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "unallavesecretamuysegura_pordefecto")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- 2. CAMBIO: Creamos una instancia de PasswordHasher ---
ph = PasswordHasher()

router = APIRouter(
    tags=["Autenticación"]
)

# --- 3. CAMBIO: Funciones de Utilidad (sin passlib) ---

def verify_password(plain_password, hashed_password):
    """Compara una contraseña en texto plano con una hasheada usando Argon2."""
    try:
        # ph.verify() no devuelve nada si tiene éxito.
        # Lanza una excepción si la verificación falla.
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        # Las contraseñas no coinciden
        return False
    except Exception as e:
        # Captura otros posibles errores (ej. hash inválido)
        return False

def get_password_hash(password):
    """Genera un hash de una contraseña usando Argon2."""
    global ph
    return ph.hash(password)

# --- (create_access_token - sin cambios) ---
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- (get_current_user - sin cambios, usa nuestro nuevo verify_password) ---
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_session)
):
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
    except JWTError:
        raise credentials_exception
    
    query = select(models.Usuario).where(models.Usuario.username == username)
    result = await db.execute(query)
    user = result.scalars().first()
    
    if user is None:
        raise credentials_exception
    
    return user

# --- (login_for_access_token - sin cambios, usa nuestro nuevo verify_password) ---
@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session)
):
    query = select(models.Usuario).where(models.Usuario.username == form_data.username)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# --- 5. NUEVO ENDPOINT: Registro de Usuario ---
@router.post("/usuarios", response_model=schemas.UsuarioOut, status_code=status.HTTP_201_CREATED, summary="Registrar un nuevo usuario")
async def registrar_usuario(
    usuario_data: schemas.UsuarioCreate,
    db: AsyncSession = Depends(get_session)
):
    """
    Crea un nuevo usuario en la base de datos.
    - **username**: Nombre de usuario único.
    - **password**: Contraseña del usuario.
    """
    # Hashea la contraseña antes de guardarla
    hashed_password = get_password_hash(usuario_data.password)
    
    # Crea el nuevo usuario
    nuevo_usuario = models.Usuario(
        username=usuario_data.username,
        hashed_password=hashed_password
        # El rol por defecto es 'usuario' según el modelo
    )
    db.add(nuevo_usuario)
    try:
        await db.commit()
        await db.refresh(nuevo_usuario)
        return nuevo_usuario
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe.")