from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

from ..db import get_session
from .. import models, schemas

router = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)

@router.post("/", response_model=schemas.ProductoOut, status_code=201)
async def crear_producto(
    data: schemas.ProductoCreate,
    db: AsyncSession = Depends(get_session)
):
    # 1. Crea un objeto del modelo Producto con los datos del schema
    nuevo_producto = models.Producto(**data.model_dump())
    # 2. Añade el objeto a la sesión de la BD
    db.add(nuevo_producto)
    # 3. Guarda los cambios en la BD
    await db.commit()
    # 4. Refresca el objeto para obtener el ID asignado por la BD
    await db.refresh(nuevo_producto)
    return nuevo_producto

@router.get("/", response_model=list[schemas.ProductoOut])
async def listar_productos(db: AsyncSession = Depends(get_session)):
    """
    Devuelve una lista de todos los productos.
    """
    stmt = select(models.Producto)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{producto_id}", response_model=schemas.ProductoOut)
async def obtener_producto(
    producto_id: int,
    db: AsyncSession = Depends(get_session)
):
    """
    Devuelve un producto específico por su ID.
    """
    stmt = select(models.Producto).where(models.Producto.id == producto_id)
    result = await db.execute(stmt)
    producto = result.scalar_one_or_none() # .scalar_one_or_none() es ideal para obtener un solo resultado o None

    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return producto

@router.put("/{producto_id}", response_model=schemas.ProductoOut)
async def actualizar_producto(
    producto_id: int,
    data: schemas.ProductoCreate,
    db: AsyncSession = Depends(get_session)
):
    # 1. Primero, busca el producto
    stmt = select(models.Producto).where(models.Producto.id == producto_id)
    result = await db.execute(stmt)
    producto_db = result.scalars().first()
    
    # 2. Si no existe, lanza un error 404
    if not producto_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # 3. Actualiza el objeto producto_db con los datos nuevos
    for key, value in data.model_dump().items():
        setattr(producto_db, key, value)

    # 4. Guarda (commit) los cambios
    await db.commit()
    # 5. Refresca para asegurarte de que los datos están actualizados
    await db.refresh(producto_db)
    return producto_db

@router.delete("/{producto_id}", status_code=204)
async def eliminar_producto(producto_id: int, db: AsyncSession = Depends(get_session)):
    stmt = delete(models.Producto).where(models.Producto.id == producto_id)
    result = await db.execute(stmt)

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    await db.commit()
