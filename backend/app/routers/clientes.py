from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

from ..db import get_session
from .. import models, schemas

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)

# 2. RUTA: Crear un nuevo cliente (CREATE)
# --- ¡CORREGIDA! ---
@router.post("/", response_model=schemas.ClienteOut, status_code=201)
async def crear_cliente(
    data: schemas.ClienteCreate, 
    db: AsyncSession = Depends(get_session)
):
    # 1. Crea un objeto del modelo Cliente con los datos
    nuevo_cliente = models.Cliente(**data.model_dump())
    
    # 2. Añade el objeto a la sesión de la BD
    db.add(nuevo_cliente)
    
    # 3. Guarda los cambios en la BD
    await db.commit()
    
    # 4. Refresca el objeto (esto trae el nuevo 'id' desde la BD)
    await db.refresh(nuevo_cliente)
    
    return nuevo_cliente

# 3. RUTA: Listar todos los clientes (READ)
# --- (Esta ya estaba bien) ---
@router.get("/", response_model=list[schemas.ClienteOut])
async def listar_clientes(db: AsyncSession = Depends(get_session)):
    stmt = select(models.Cliente)
    result = await db.execute(stmt)
    clientes = result.scalars().all() 
    return [cliente for cliente in clientes]

# 4. RUTA: Actualizar un cliente (UPDATE)
# --- ¡CORREGIDA! ---
@router.put("/{cliente_id}", response_model=schemas.ClienteOut)
async def actualizar_cliente(
    cliente_id: int,
    data: schemas.ClienteCreate,
    db: AsyncSession = Depends(get_session)
):
    # 1. Primero, busca el cliente
    stmt_select = select(models.Cliente).where(models.Cliente.id == cliente_id)
    result = await db.execute(stmt_select)
    cliente_db = result.scalars().first() # .first() obtiene un solo objeto o None
    
    # 2. Si no existe, lanza un error 404
    if not cliente_db:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
    # 3. Actualiza el objeto cliente_db con los datos nuevos
    for key, value in data.model_dump().items():
        setattr(cliente_db, key, value) # Esto es como: cliente_db.nombre = data.nombre

    # 4. Guarda (commit) los cambios
    await db.commit()
    
    # 5. Refresca para asegurarte de que los datos están actualizados
    await db.refresh(cliente_db)
    
    return cliente_db

# 5. RUTA: Eliminar un cliente (DELETE)
# --- (Esta ya estaba bien, no usa .returning) ---
@router.delete("/{cliente_id}", status_code=204)
async def eliminar_cliente(
    cliente_id: int, 
    db: AsyncSession = Depends(get_session)
):
    stmt = delete(models.Cliente).where(models.Cliente.id == cliente_id)
    result = await db.execute(stmt)
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
    await db.commit()
    return