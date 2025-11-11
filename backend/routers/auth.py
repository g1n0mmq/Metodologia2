from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import schemas.auth as schemas_auth
from services import auth_service

router = APIRouter(
    tags=["Autenticación"]
)

@router.post("/token", response_model=schemas_auth.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = await auth_service.get_user(form_data.username)
    if not user or not auth_service.verify_password(form_data.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.create_access_token(data={"sub": user['username']})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/usuarios", response_model=schemas_auth.UsuarioOut, status_code=status.HTTP_201_CREATED)
async def registrar_usuario(
    usuario_data: schemas_auth.UsuarioCreate
):
    return await auth_service.register_new_user(usuario_data)