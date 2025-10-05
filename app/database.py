from app.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# ✅ Create the base class for all models
Base = declarative_base()

# ✅ Create async engine using DATABASE_URL from .env
engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)

# ✅ Create session factory
async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# ✅ Dependency for FastAPI routes
async def get_db():
    async with async_session_maker() as session:
        yield session