from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

from ..db import get_session
from .. import models, schemas

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)

# Endpoint para crear un nuevo cliente.
@router.post("/", response_model=schemas.ClienteOut, status_code=201)
async def crear_cliente(
    data: schemas.ClienteCreate, 
    db: AsyncSession = Depends(get_session)
):
    # 1. Crea un objeto del modelo Cliente con los datos
    nuevo_cliente = models.Cliente(**data.model_dump())
    
    # 2. Agrega el nuevo cliente a la sesión de la base de datos.
    db.add(nuevo_cliente)
    
    # 3. Confirma la transacción para guardar los cambios en la base de datos.
    await db.commit()
    
    # 4. Actualiza el objeto `nuevo_cliente` con los datos generados por la base de datos (ej. el ID).
    await db.refresh(nuevo_cliente)
    
    return nuevo_cliente

# Endpoint para obtener una lista de todos los clientes.
@router.get("/", response_model=list[schemas.ClienteOut])
async def listar_clientes(db: AsyncSession = Depends(get_session)):
    stmt = select(models.Cliente)
    result = await db.execute(stmt)
    clientes = result.scalars().all() 
    return clientes

# Endpoint para actualizar la información de un cliente existente.
@router.put("/{cliente_id}", response_model=schemas.ClienteOut)
async def actualizar_cliente(
    cliente_id: int,
    data: schemas.ClienteCreate,
    db: AsyncSession = Depends(get_session)
):
    # 1. Primero, busca el cliente
    result = await db.execute(select(models.Cliente).where(models.Cliente.id == cliente_id))
    cliente_db = result.scalars().first() # Obtiene el primer resultado o None si no existe.
    
    # 2. Si el cliente no se encuentra, devuelve un error 404.
    if not cliente_db:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
    # 3. Itera sobre los datos proporcionados y actualiza los atributos del cliente en la base de datos.
    for key, value in data.model_dump().items():
        setattr(cliente_db, key, value)

    # 4. Confirma la transacción para guardar los cambios.
    await db.commit()
    
    # 5. Actualiza el objeto `cliente_db` para reflejar los cambios persistidos.
    await db.refresh(cliente_db)
    
    return cliente_db

# Endpoint para eliminar un cliente por su ID.
@router.delete("/{cliente_id}", status_code=204)
async def eliminar_cliente(
    cliente_id: int, 
    db: AsyncSession = Depends(get_session)
):
    stmt = delete(models.Cliente).where(models.Cliente.id == cliente_id)
    result = await db.execute(stmt)
    # `rowcount` indica cuántas filas fueron afectadas por la operación DELETE.
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
    # Confirma la eliminación en la base de datos.
    await db.commit()
    return