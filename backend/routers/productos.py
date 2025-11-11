from typing import List
from fastapi import APIRouter, Depends
import schemas.producto as schemas_producto
import schemas.auth as schemas_auth
from services import productos_service, auth_service

router = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)

@router.get("/", response_model=List[schemas_producto.ProductoOut])
async def listar_productos(user: schemas_auth.UsuarioOut = Depends(auth_service.get_current_user)):
    return await productos_service.get_productos()

@router.post("/", response_model=schemas_producto.ProductoOut, status_code=201)
async def crear_producto(
    data: schemas_producto.ProductoCreate,
    user: schemas_auth.UsuarioOut = Depends(auth_service.get_current_user)
):
    return await productos_service.create_producto(data)

@router.get("/{producto_id}", response_model=schemas_producto.ProductoOut)
async def obtener_producto(
    producto_id: int,
    user: schemas_auth.UsuarioOut = Depends(auth_service.get_current_user)
):
    return await productos_service.get_producto(producto_id)

@router.put("/{producto_id}", response_model=schemas_producto.ProductoOut)
async def actualizar_producto(
    producto_id: int,
    data: schemas_producto.ProductoCreate,
    user: schemas_auth.UsuarioOut = Depends(auth_service.get_current_user)
):
    return await productos_service.update_producto(producto_id, data)

@router.delete("/{producto_id}", status_code=204)
async def eliminar_producto(
    producto_id: int, 
    user: schemas_auth.UsuarioOut = Depends(auth_service.get_current_user)
):
    await productos_service.delete_producto(producto_id)
    return