from pydantic import BaseModel
from decimal import Decimal

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