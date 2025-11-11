from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.database import db 

# Importa los routers
from routers import clientes, productos, facturas, auth

app = FastAPI(
    title="TP Final – API",
    version="1.0.0"
)

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CICLO DE VIDA DE LA CONEXIÓN (Requerido por 'databases') ---
@app.on_event("startup")
async def startup():
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()
# -------------------------------------------------------------

# Incluye los routers
app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(productos.router)
app.include_router(facturas.router)
    
@app.get("/")
def root():
    return {"mensaje": "Bienvenido a la API del TP Final"}