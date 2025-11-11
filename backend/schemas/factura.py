from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class FacturaCreate(BaseModel):
    cliente_id: int

class FacturaIdOut(BaseModel):
    factura_id: int

class FacturaOut(BaseModel):
    id: int
    cliente_id: int
    fecha: datetime
    creado_por_usuario_id: Optional[int] = None

class DetalleCreate(BaseModel):
    producto_id: int
    cantidad: int

class DetalleOut(BaseModel):
    factura_id: int
    producto_id: int
    cantidad: int
    precio: Decimal
    created: datetime

class DetalleFacturaItemOut(BaseModel):
    producto_id: int
    nombre: str
    cantidad: int
    precio: Decimal
    importe: Decimal

class ReporteVentasClienteOut(BaseModel):
    cliente_id: int
    nombre: str
    apellido: str
    total_comprado: Decimal

class FacturaConNombresOut(BaseModel):
    id: int
    fecha: datetime
    cliente_nombre: Optional[str] = None
    cliente_apellido: Optional[str] = None
    creador_username: Optional[str] = None