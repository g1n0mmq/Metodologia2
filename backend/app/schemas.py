from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

# Schemas Pydantic para la validación de datos de Clientes.
class ClienteBase(BaseModel):
    # Campos base para un cliente, usados tanto para entrada como para salida.
    nombre: str
    apellido: str
    dni: int
    direccion: Optional[str] = None # Campo opcional.
    telefono: Optional[str] = None

class ClienteCreate(ClienteBase):
    # Schema para la creación de un cliente. Hereda de ClienteBase.
    pass

class ClienteOut(ClienteBase):
    # Schema para la respuesta de un cliente, incluyendo su ID.
    id: int

    class Config:
        from_attributes = True # Permite a Pydantic leer desde el modelo de SQLAlchemy

# --- Schemas para Productos ---

# Schemas Pydantic para la validación de datos de Productos.
class ProductoBase(BaseModel):
    nombre: str
    descripcion: str
    stock: int
    precio_compra: Decimal
    precio_venta: Decimal
class ProductoCreate(ProductoBase):
    # Schema para la creación de un producto.
    pass

class ProductoOut(ProductoBase):
    # Schema para la respuesta de un producto, incluyendo su ID.
    id: int

    class Config:
        from_attributes = True

# --- Schemas para Facturas ---
# Schemas Pydantic para la validación de datos de Facturas.
class FacturaCreate(BaseModel):
    # Schema para crear una factura, solo requiere el ID del cliente.
    cliente_id: int
class FacturaIdOut(BaseModel):
    # Schema para devolver el ID de una factura creada.
    factura_id: int

# --- Schemas para Detalle de Factura ---
# Schemas Pydantic para la validación de datos de Detalles de Factura.
class DetalleCreate(BaseModel):
    # Schema para agregar un ítem a una factura, requiere producto_id y cantidad.
    producto_id: int
    cantidad: int

# Schema para la respuesta de un detalle de factura.
class DetalleOut(BaseModel):
    factura_id: int
    producto_id: int
    cantidad: int
    precio: Decimal
    created: datetime

    class Config:
        from_attributes = True

class DetalleFacturaItemOut(BaseModel):
    producto_id: int
    nombre: str
    cantidad: int
    precio: Decimal
    importe: Decimal

    class Config:
        from_attributes = True # Permite leer datos desde objetos

# --- ¡CLASE FALTANTE CORREGIDA! ---
# Esta clase faltaba y causaba el error en facturas.py
class ReporteVentasClienteOut(BaseModel):
    cliente_id: int
    nombre: str
    apellido: str
    total_comprado: Decimal

    class Config:
        from_attributes = True