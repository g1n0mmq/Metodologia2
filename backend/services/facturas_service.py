from fastapi import HTTPException, status
from datetime import datetime
from config.database import db
import schemas.factura as schemas_factura
import schemas.auth as schemas_auth
from utils import pdf_generator # Importa tu generador de PDF
import io
from decimal import Decimal
from fastapi.responses import StreamingResponse

# --- LÓGICA DE FACTURAS ---

async def create_factura(data: schemas_factura.FacturaCreate, current_user, db_instance=db):
    try:
        # 1. Intenta la inserción manual
        query = "INSERT INTO factura (cliente_id, fecha, creado_por_usuario_id) VALUES (:cliente_id, :fecha, :usuario_id)"
        values = {
            "cliente_id": data.cliente_id,
            "fecha": datetime.utcnow(),
            "usuario_id": current_user['id']
        }
        factura_id = await db_instance.execute(query=query, values=values)
        return {"factura_id": factura_id}
    except Exception as e:
        # 2. Fallback: Llama al Stored Procedure (si existe)
        try:
            sp_query = "CALL sp_agregar_factura(:cliente_id)"
            row = await db.fetch_one(sp_query, values={"cliente_id": data.cliente_id})
            if not row or "factura_id" not in row:
                 raise HTTPException(status_code=500, detail="El SP no devolvió un ID de factura.")
            return {"factura_id": row["factura_id"]}
        except Exception as sp_e:
             raise HTTPException(status_code=500, detail=f"Error al crear factura (ambos métodos fallaron): {e} | {sp_e}")

async def get_facturas(current_user, db_instance=db):
    query_sql = """
        SELECT f.id, f.fecha, c.nombre as cliente_nombre, 
               c.apellido as cliente_apellido, u.username as creador_username
        FROM factura f
        LEFT JOIN clientes c ON f.cliente_id = c.id
        LEFT JOIN usuarios u ON f.creado_por_usuario_id = u.id
    """
    
    if current_user['rol'] == 'admin':
        query_sql += " ORDER BY f.fecha DESC"
        return await db_instance.fetch_all(query=query_sql)
    else:
        query_sql += " WHERE f.creado_por_usuario_id = :user_id ORDER BY f.fecha DESC"
        return await db_instance.fetch_all(query=query_sql, values={"user_id": current_user['id']})

async def add_item_to_factura(factura_id: int, item: schemas_factura.DetalleCreate, db_instance=db):
    prod_query = "SELECT id, nombre, stock, precio_venta FROM productos WHERE id = :id"
    producto = await db_instance.fetch_one(query=prod_query, values={"id": item.producto_id})
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if producto['stock'] < item.cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente")

    try:
        async with db_instance.transaction():
            detalle_query = "INSERT INTO detalle (factura_id, producto_id, cantidad, precio, created) VALUES (:factura_id, :producto_id, :cantidad, :precio, :created)"
            await db_instance.execute(detalle_query, values={
                "factura_id": factura_id,
                "producto_id": item.producto_id,
                "cantidad": item.cantidad,
                "precio": producto['precio_venta'],
                "created": datetime.utcnow()
            })
            stock_query = "UPDATE productos SET stock = stock - :cantidad WHERE id = :id"
            await db_instance.execute(stock_query, values={"cantidad": item.cantidad, "id": item.producto_id})
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Error de base de datos al agregar item: {str(e)}")
    return {"mensaje": "Item agregado correctamente"}

async def get_detalle_factura(factura_id: int, db_instance=db):
    query = """
        SELECT d.producto_id, p.nombre, d.cantidad, d.precio, (d.cantidad * d.precio) AS importe
        FROM detalle d
        INNER JOIN productos p ON p.id = d.producto_id
        WHERE d.factura_id = :f_id
    """
    items = await db_instance.fetch_all(query=query, values={"f_id": factura_id})
    if not items:
        raise HTTPException(status_code=404, detail="Factura no encontrada o sin items")
    return items

async def get_reporte_ventas_cliente(db_instance=db):
    query = """
        SELECT c.id AS cliente_id, c.nombre, c.apellido,
               SUM(d.cantidad * d.precio) AS total_comprado
        FROM factura f
        INNER JOIN clientes c ON c.id = f.cliente_id
        INNER JOIN detalle d ON d.factura_id = f.id
        GROUP BY c.id, c.nombre, c.apellido
        ORDER BY total_comprado DESC
    """
    return await db_instance.fetch_all(query=query)

async def get_full_factura_data_for_pdf(factura_id: int, db_instance=db):
    query_factura = "SELECT f.id, f.fecha, c.nombre, c.apellido, c.dni, c.direccion, c.telefono, u.username FROM factura f LEFT JOIN clientes c ON f.cliente_id = c.id LEFT JOIN usuarios u ON f.creado_por_usuario_id = u.id WHERE f.id = :factura_id"
    factura = await db_instance.fetch_one(query=query_factura, values={"factura_id": factura_id})
    if not factura:
        return None
    query_items = "SELECT d.cantidad, d.precio, p.nombre FROM detalle d INNER JOIN productos p ON d.producto_id = p.id WHERE d.factura_id = :factura_id"
    items = await db_instance.fetch_all(query=query_items, values={"factura_id": factura_id})
    return {
        "id": factura['id'], "fecha": factura['fecha'], "creador": {"username": factura['username'] or "N/A"},
        "cliente": {"nombre": factura['nombre'], "apellido": factura['apellido'], "dni": factura['dni'], "direccion": factura['direccion'], "telefono": factura['telefono']},
        "detalle": items
    }

async def generate_factura_pdf(factura_id: int, current_user, db_instance=db):
    factura_data = await get_full_factura_data_for_pdf(factura_id, db_instance)
    if not factura_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada")
    if current_user['rol'] != 'admin' and factura_data['creador']['username'] != current_user['username']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para acceder a esta factura")
    pdf_buffer = pdf_generator.generate_invoice_pdf_buffer(factura_data)
    return StreamingResponse(pdf_buffer, media_type='application/pdf', headers={"Content-Disposition": f"inline; filename=factura_{factura_id}.pdf"})