from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

# --- Schemas para Clientes ---

class ClienteBase(BaseModel):
    # Campos que se piden para crear Y para mostrar
    nombre: str
    apellido: str
    dni: int
    direccion: Optional[str] = None # Opcional, puede ser None
    telefono: Optional[str] = None

class ClienteCreate(ClienteBase):
    # No necesita campos extra para crear
    pass

class ClienteOut(ClienteBase):
    # Campos que se devuelven al cliente
    id: int

    class Config:
        from_attributes = True # Permite a Pydantic leer desde el modelo de SQLAlchemy

# --- Schemas para Productos ---

class ProductoBase(BaseModel):
    nombre: str
    descripcion: str
    stock: int
    precio_compra: Decimal
    precio_venta: Decimal

class ProductoCreate(ProductoBase):
    pass

class ProductoOut(ProductoBase):
    id: int

    class Config:
        from_attributes = True

# --- Schemas para Facturas ---

class FacturaCreate(BaseModel):
    # Para crear una factura, solo necesitamos el ID del cliente
    cliente_id: int

# --- Schemas para Detalle de Factura ---

class DetalleCreate(BaseModel):
    # Para agregar un item, necesitamos el producto y la cantidad
    producto_id: int
    cantidad: int

class DetalleOut(BaseModel):
    # Lo que devolvemos al frontend
    factura_id: int
    producto_id: int
    cantidad: int
    precio: Decimal
    created: datetime

    class Config:
        from_attributes = True