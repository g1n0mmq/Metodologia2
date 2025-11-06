from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importa los routers que crearemos luego
from .routers import clientes, productos, facturas
from app import models
from app.db import engine

# Esta línea (comentada) se usa para que SQLAlchemy cree las tablas
# en la base de datos basándose en los modelos definidos en `models.py`
# al iniciar la aplicación. Es útil para desarrollo inicial.
# models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TP Final – API",
    version="1.0.0"
)
# Configuración de CORS (Cross-Origin Resource Sharing)
# Permite que el frontend (ej. una aplicación React en localhost:5173)
# pueda hacer solicitudes a esta API.
origins = [
    "http://localhost:5173",  # La dirección de tu app de React (Vite)
    "http://localhost:3000",  # Dirección común si usaras create-react-app
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Lista de orígenes permitidos
    allow_credentials=True,    # Permite el envío de cookies y cabeceras de autenticación
    allow_methods=["*"],         # Permite todos los métodos HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],         # Permite todos los encabezados HTTP
)

# Incluye los routers definidos en otros módulos para organizar las rutas de la API.
app.include_router(clientes.router)
app.include_router(productos.router)
app.include_router(facturas.router)
    
# Ruta raíz de bienvenida
@app.get("/")
def root():
    return {"mensaje": "Bienvenido a la API del TP Final"}