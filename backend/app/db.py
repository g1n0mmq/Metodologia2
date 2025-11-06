import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Carga las variables de entorno del archivo .env
load_dotenv()

# Lee las variables de entorno
DB_USER = os.getenv("MYSQL_USER")
DB_PASS = os.getenv("MYSQL_PASSWORD")
DB_HOST = os.getenv("MYSQL_HOST")
DB_PORT = os.getenv("MYSQL_PORT")
DB_NAME = os.getenv("MYSQL_DB")

# Crea la URL de conexión para MySQL asíncrono (aiomysql)
DB_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Crea el motor (engine) asíncrono
engine = create_async_engine(DB_URL, echo=True, pool_pre_ping=True)

# Crea una fábrica de sesiones (Session factory)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependencia de FastAPI: obtiene una sesión de BD por cada petición
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session