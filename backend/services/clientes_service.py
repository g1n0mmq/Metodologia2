from typing import List
from fastapi import HTTPException
from config.database import db
import schemas.cliente as schemas_cliente

async def get_clientes(db_instance=db) -> List[schemas_cliente.ClienteOut]:
    query = "SELECT * FROM clientes"
    return await db_instance.fetch_all(query=query)

async def create_cliente(data: schemas_cliente.ClienteCreate, db_instance=db) -> schemas_cliente.ClienteOut:
    query = "INSERT INTO clientes (dni, nombre, apellido, direccion, telefono) VALUES (:dni, :nombre, :apellido, :direccion, :telefono)"
    last_record_id = await db_instance.execute(query=query, values=data.model_dump())
    return {**data.model_dump(), "id": last_record_id}

async def update_cliente(cliente_id: int, data: schemas_cliente.ClienteCreate, db_instance=db) -> schemas_cliente.ClienteOut:
    await get_cliente_by_id(cliente_id, db_instance) # Verifica si existe
    query = "UPDATE clientes SET dni = :dni, nombre = :nombre, apellido = :apellido, direccion = :direccion, telefono = :telefono WHERE id = :id"
    values = {**data.model_dump(), "id": cliente_id}
    await db_instance.execute(query=query, values=values)
    return {**data.model_dump(), "id": cliente_id}

async def delete_cliente(cliente_id: int, db_instance=db):
    await get_cliente_by_id(cliente_id, db_instance) # Verifica si existe
    query = "DELETE FROM clientes WHERE id = :id"
    await db_instance.execute(query=query, values={"id": cliente_id})
    return

async def get_cliente_by_id(cliente_id: int, db_instance=db):
    query = "SELECT * FROM clientes WHERE id = :id"
    row = await db_instance.fetch_one(query=query, values={"id": cliente_id})
    if not row:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return row