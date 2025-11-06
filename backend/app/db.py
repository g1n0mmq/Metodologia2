import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Carga las variables de entorno desde el archivo `.env` en el directorio raíz.
load_dotenv()

# Obtiene las credenciales de la base de datos de las variables de entorno.
DB_USER = os.getenv("MYSQL_USER")
DB_PASS = os.getenv("MYSQL_PASSWORD")
DB_HOST = os.getenv("MYSQL_HOST")
DB_PORT = os.getenv("MYSQL_PORT")
DB_NAME = os.getenv("MYSQL_DB")

# Crea la URL de conexión para MySQL asíncrono (aiomysql)
DB_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}" # type: ignore

# Inicializa el motor de la base de datos asíncrono. `echo=True` habilita el log de SQL.
engine = create_async_engine(DB_URL, echo=True, pool_pre_ping=True)

# Configura una fábrica de sesiones asíncronas para interactuar con la base de datos.
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Función de dependencia de FastAPI que proporciona una sesión de base de datos por cada solicitud.
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session