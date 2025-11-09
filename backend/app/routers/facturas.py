from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, insert, update
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

# Importaciones relativas
from ..db import get_session
from .. import models, schemas
# 1. IMPORTA EL ARCHIVO DE AUTH
from .. import auth

# Creamos el router para Facturas
router = APIRouter(
    prefix="/facturas",
    tags=["Facturas"]
)

# Endpoint para crear una nueva factura.
@router.post("/", response_model=schemas.FacturaIdOut)
async def crear_factura(
    data: schemas.FacturaCreate, # Requiere el ID del cliente.
    db: AsyncSession = Depends(get_session),
    # 2. USA LA FUNCIÓN REAL y DESCOMENTA la línea
    current_user: models.Usuario = Depends(auth.get_current_user) 
):
    """
    Crea una nueva factura en la base de datos.
    Este método ahora usa una inserción directa con SQLAlchemy para mayor
    claridad y un manejo de errores robusto.
    """
    try:
        # 1. Instancia un objeto `Factura` con los datos proporcionados.
        nueva_factura = models.Factura(
            cliente_id=data.cliente_id,
            fecha=datetime.utcnow(),
            creado_por_usuario_id=current_user.id 
        )
        # 2. Añade, guarda y refresca para obtener el ID.
        db.add(nueva_factura)
        await db.commit()
        await db.refresh(nueva_factura)
        
        return {"factura_id": nueva_factura.id}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear la factura: {e}")

# --- LÓGICA DE LISTAR FACTURAS (ADMIN vs USUARIO) ---
@router.get("/", response_model=list[schemas.FacturaConNombresOut]) # <-- 1. CAMBIO AQUÍ
async def listar_facturas(
    db: AsyncSession = Depends(get_session),
    # 4. USA LA FUNCIÓN REAL aquí también
    current_user: models.Usuario = Depends(auth.get_current_user)
):
    # 2. CAMBIO: Usamos SQL puro (text()) para hacer los JOINs
    query_sql = """
        SELECT 
            f.id, 
            f.fecha, 
            c.nombre as cliente_nombre, 
            c.apellido as cliente_apellido,
            u.username as creador_username
        FROM factura f
        LEFT JOIN clientes c ON f.cliente_id = c.id
        LEFT JOIN usuarios u ON f.creado_por_usuario_id = u.id
    """
    
    # 3. La lógica de roles (admin ve todo, usuario ve solo lo suyo)
    if current_user.rol == 'admin':
        query = text(query_sql + " ORDER BY f.fecha DESC")
        result = await db.execute(query)
    else:
        # Añadimos el WHERE para el usuario normal
        query_sql += " WHERE f.creado_por_usuario_id = :user_id ORDER BY f.fecha DESC"
        query = text(query_sql)
        result = await db.execute(query, {"user_id": current_user.id})
        
    facturas = result.mappings().all()
    
    return facturas


# Endpoint para agregar un ítem a una factura existente.
@router.post("/{factura_id}/items", status_code=201)
async def agregar_item_factura(
    factura_id: int,
    item: schemas.DetalleCreate, # Necesita producto_id y cantidad
    db: AsyncSession = Depends(get_session)
):
    # 1. Buscar el producto para obtener su precio y stock
    result = await db.execute(select(models.Producto).where(models.Producto.id == item.producto_id))
    producto = result.scalars().first()
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    # Verifica si hay suficiente stock del producto.
    if producto.stock < item.cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente")
        
    # 2. Prepara la sentencia para insertar el detalle de la factura.
    detalle_stmt = insert(models.Detalle).values(
        factura_id=factura_id,
        producto_id=item.producto_id,
        cantidad=item.cantidad,
        precio=producto.precio_venta, # Usamos el precio guardado del producto
        created=datetime.utcnow()
    )
    
    # 3. Prepara la sentencia para actualizar el stock del producto.
    stock_stmt = update(models.Producto).where(
        models.Producto.id == item.producto_id
    ).values(
        stock = models.Producto.stock - item.cantidad
    )
    
    # Ejecuta ambas operaciones (insertar detalle y actualizar stock) dentro de una transacción.
    try:
        await db.execute(detalle_stmt)
        await db.execute(stock_stmt)
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback() # Si ocurre un error, se revierte toda la transacción.
        raise HTTPException(status_code=500, detail=f"Error de base de datos al agregar item: {str(e)}")
    
    return {"mensaje": "Item agregado correctamente"}
# Endpoint para obtener el detalle de una factura específica, incluyendo información del producto.
@router.get("/{factura_id}/detalle")
async def detalle_factura(factura_id: int, db: AsyncSession = Depends(get_session)) -> list[schemas.DetalleFacturaItemOut]:
    query = text("""
        SELECT d.producto_id, p.nombre, d.cantidad, d.precio, (d.cantidad * d.precio) AS importe
        FROM detalle d
        INNER JOIN productos p ON p.id = d.producto_id
        WHERE d.factura_id = :f_id
    """)
    
    result = await db.execute(query, {"f_id": factura_id})
    items = result.mappings().all() # Mapea los resultados a diccionarios.
    
    if not items:
        raise HTTPException(status_code=404, detail="Factura no encontrada o sin items")
        
    return items

# Endpoint para generar un reporte de ventas agrupado por cliente.
@router.get("/reporte/ventas-por-cliente", response_model=list[schemas.ReporteVentasClienteOut])
async def reporte_ventas_cliente(db: AsyncSession = Depends(get_session)):
    query = text("""
        SELECT 
            c.id AS cliente_id,
            c.nombre,
            c.apellido,
            SUM(d.cantidad * d.precio) AS total_comprado
        FROM factura f
        INNER JOIN clientes c ON c.id = f.cliente_id
        INNER JOIN detalle d ON d.factura_id = f.id
        GROUP BY c.id, c.nombre, c.apellido
        ORDER BY total_comprado DESC
    """)
    
    result = await db.execute(query)
    reporte = result.mappings().all()
    
    return reporte