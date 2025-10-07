from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import auth, materials, product_types, items 
from app.db import database, models


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ✅ Startup logic
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    print("✅ Database tables created")

    yield  # App runs here

    # ✅ Shutdown logic
    await database.engine.dispose()
    print("🧹 Database engine disposed")


# ✅ Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# ✅ Include routers
app.include_router(auth.router)
app.include_router(materials.router)
app.include_router(product_types.router)
app.include_router(items.router)
