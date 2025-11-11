from typing import List
from fastapi import APIRouter, Depends
import schemas.cliente as schemas_cliente
import schemas.auth as schemas_auth
from services import clientes_service, auth_service

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)

@router.get("/", response_model=List[schemas_cliente.ClienteOut])
async def listar_clientes(user: schemas_auth.UsuarioOut = Depends(auth_service.get_current_user)):
    return await clientes_service.get_clientes()

@router.post("/", response_model=schemas_cliente.ClienteOut, status_code=201)
async def crear_cliente(
    data: schemas_cliente.ClienteCreate, 
    user: schemas_auth.UsuarioOut = Depends(auth_service.get_current_user)
):
    return await clientes_service.create_cliente(data)

@router.put("/{cliente_id}", response_model=schemas_cliente.ClienteOut)
async def actualizar_cliente(
    cliente_id: int,
    data: schemas_cliente.ClienteCreate,
    user: schemas_auth.UsuarioOut = Depends(auth_service.get_current_user)
):
    return await clientes_service.update_cliente(cliente_id, data)

@router.delete("/{cliente_id}", status_code=204)
async def eliminar_cliente(
    cliente_id: int, 
    user: schemas_auth.UsuarioOut = Depends(auth_service.get_current_user)
):
    await clientes_service.delete_cliente(cliente_id)
    return