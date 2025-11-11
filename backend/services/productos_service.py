from typing import List
from fastapi import HTTPException
from config.database import db
import schemas.producto as schemas_producto

async def get_productos(db_instance=db) -> List[schemas_producto.ProductoOut]:
    query = "SELECT * FROM productos"
    return await db_instance.fetch_all(query=query)

async def create_producto(data: schemas_producto.ProductoCreate, db_instance=db) -> schemas_producto.ProductoOut:
    query = "INSERT INTO productos (nombre, descripcion, stock, precio_compra, precio_venta) VALUES (:nombre, :descripcion, :stock, :precio_compra, :precio_venta)"
    last_record_id = await db_instance.execute(query=query, values=data.model_dump())
    return {**data.model_dump(), "id": last_record_id}
    
async def get_producto(producto_id: int, db_instance=db) -> schemas_producto.ProductoOut:
    query = "SELECT * FROM productos WHERE id = :id"
    producto = await db_instance.fetch_one(query=query, values={"id": producto_id})
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

async def update_producto(producto_id: int, data: schemas_producto.ProductoCreate, db_instance=db) -> schemas_producto.ProductoOut:
    await get_producto(producto_id, db_instance) # Verifica si existe
    query = "UPDATE productos SET nombre = :nombre, descripcion = :descripcion, stock = :stock, precio_compra = :precio_compra, precio_venta = :precio_venta WHERE id = :id"
    values = {**data.model_dump(), "id": producto_id}
    await db_instance.execute(query=query, values=values)
    return {**data.model_dump(), "id": producto_id}

async def delete_producto(producto_id: int, db_instance=db):
    await get_producto(producto_id, db_instance) # Verifica si existe
    query = "DELETE FROM productos WHERE id = :id"
    try:
        await db_instance.execute(query=query, values={"id": producto_id})
    except Exception as e:
        if "1451" in str(e): # Error de Foreign Key
             raise HTTPException(status_code=400, detail="No se puede eliminar el producto porque está asociado a una factura existente.")
        raise HTTPException(status_code=500, detail=f"Error al eliminar: {e}")
    return