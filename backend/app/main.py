from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importa los routers que crearemos luego
from app.routers import clientes, productos #facturas
from app import models
from app.db import engine

# (Opcional) Esto le dice a SQLAlchemy que cree las tablas
# basándose en los modelos cuando la app se inicia.
# No es necesario si ya creaste las tablas manualmente con SQL.
# models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TP Final – API",
    version="1.0.0"
)

# --- Configuración de CORS ---
# Esto es VITAL para que tu frontend (React) pueda conectarse a la API
origins = [
    "http://localhost:5173",  # La dirección de tu app de React (Vite)
    "http://localhost:3000",  # Dirección común si usaras create-react-app
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Permite estas direcciones
    allow_credentials=True,    # Permite credenciales
    allow_methods=["*"],         # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],         # Permite todos los headers
)

# --- Rutas de la API ---
# Incluye los routers de los otros archivos
app.include_router(clientes.router)
app.include_router(productos.router)
#app.include_router(facturas.router)

# Ruta raíz de bienvenida
@app.get("/")
def root():
    return {"mensaje": "Bienvenido a la API del TP Final"}