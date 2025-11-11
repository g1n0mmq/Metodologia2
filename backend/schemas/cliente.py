from pydantic import BaseModel
from typing import Optional

class ClienteBase(BaseModel):
    nombre: str
    apellido: str
    dni: int
    direccion: Optional[str] = None
    telefono: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteOut(ClienteBase):
    id: int