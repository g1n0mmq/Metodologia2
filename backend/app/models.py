from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from datetime import datetime

# Base para todos los modelos
Base = declarative_base()

class Cliente(Base):
    __tablename__ = 'clientes'
    
    id = Column(Integer, primary_key=True)
    dni = Column(Integer, unique=True, nullable=False)
    nombre = Column(String(45), nullable=False)
    apellido = Column(String(45), nullable=False)
    direccion = Column(String(60))
    telefono = Column(String(20))
    
    # Relación: Un cliente puede tener muchas facturas
    facturas = relationship('Factura', back_populates='cliente')

class Producto(Base):
    __tablename__ = 'productos'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(60), nullable=False)
    descripcion = Column(String(100), nullable=False)
    stock = Column(Integer, nullable=False)
    precio_compra = Column(Numeric(11, 2), nullable=False)
    precio_venta = Column(Numeric(11, 2), nullable=False)
    
    # Relación: Un producto puede estar en muchos detalles
    detalles = relationship('Detalle', back_populates='producto')

class Factura(Base):
    __tablename__ = 'factura'
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    fecha = Column(DateTime, nullable=False)
    
    # Relación: Una factura pertenece a un cliente
    cliente = relationship('Cliente', back_populates='facturas')
    # Relación: Una factura tiene muchos detalles
    detalle = relationship('Detalle', back_populates='factura')

class Detalle(Base):
    __tablename__ = 'detalle'
    
    # Clave primaria compuesta (como en tu script SQL)
    factura_id = Column(Integer, ForeignKey('factura.id'), primary_key=True)
    producto_id = Column(Integer, ForeignKey('productos.id'), primary_key=True)
    
    cantidad = Column(Integer, nullable=False)
    precio = Column(Numeric(11, 2), nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relación: Un detalle pertenece a una factura
    factura = relationship('Factura', back_populates='detalle')
    # Relación: Un detalle tiene un producto
    producto = relationship('Producto', back_populates='detalles')

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(45), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)