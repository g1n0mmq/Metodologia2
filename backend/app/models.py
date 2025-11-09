from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from datetime import datetime

# `Base` es la clase declarativa de SQLAlchemy de la que heredarán todos nuestros modelos.
Base = declarative_base()

class Cliente(Base):
    __tablename__ = 'clientes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    dni = Column(Integer, unique=True, nullable=False)
    nombre = Column(String(45), nullable=False)
    apellido = Column(String(45), nullable=False)
    direccion = Column(String(60))
    telefono = Column(String(20))
    
    # Relación: Un cliente puede tener muchas facturas
    facturas = relationship('Factura', back_populates='cliente', cascade="all, delete-orphan")

class Producto(Base):
    __tablename__ = 'productos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(60), nullable=False, unique=True)
    descripcion = Column(String(100), nullable=False)
    stock = Column(Integer, nullable=False)
    precio_compra = Column(Numeric(11, 2), nullable=False)
    precio_venta = Column(Numeric(11, 2), nullable=False)
    
    # Relación: Un producto puede estar en muchos detalles
    detalles = relationship('Detalle', back_populates='producto', cascade="all, delete-orphan")
class Factura(Base):
    __tablename__ = 'factura'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    fecha = Column(DateTime, nullable=False)
    # --- 3. NUEVA COLUMNA DE "PROPIETARIO" ---
    # --- CORRECCIÓN AQUÍ ---
    creado_por_usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    
    # Relación: Una factura pertenece a un cliente
    cliente = relationship('Cliente', back_populates='facturas')
    # Relación: Una factura puede tener múltiples ítems (detalles).
    detalle = relationship('Detalle', back_populates='factura', cascade="all, delete-orphan")
    
    # --- 4. NUEVA RELACIÓN ---
    # Una factura fue creada por un usuario
    creador = relationship('Usuario', back_populates='facturas_creadas')

class Detalle(Base):
    __tablename__ = 'detalle'
    
    # Clave primaria compuesta (como en tu script SQL)
    factura_id = Column(Integer, ForeignKey('factura.id'), primary_key=True)
    producto_id = Column(Integer, ForeignKey('productos.id'), primary_key=True)
    
    cantidad = Column(Integer, nullable=False)
    precio = Column(Numeric(11, 2), nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relación: Cada detalle está asociado a una factura.
    factura = relationship('Factura', back_populates='detalle')
    # Relación: Cada detalle se refiere a un producto específico.
    producto = relationship('Producto', back_populates='detalles')

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(45), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # --- 1. NUEVA COLUMNA DE ROL ---
    rol = Column(String(10), nullable=False, default='usuario') # 'usuario' o 'admin'
    # --- 2. NUEVA RELACIÓN ---
    # Un usuario puede crear muchas facturas
    facturas_creadas = relationship('Factura', back_populates='creador')