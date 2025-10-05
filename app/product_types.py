from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, schemas, database

router = APIRouter(prefix="/product-types", tags=["product-types"])

# Create ProductType
@router.post("/", response_model=schemas.ProductTypeRead)
async def create_product_type(pt: schemas.ProductTypeCreate, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.ProductType).where(models.ProductType.name == pt.name))
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Product type already exists")

    db_pt = models.ProductType(name=pt.name, description=pt.description)
    db.add(db_pt)
    await db.commit()
    await db.refresh(db_pt)
    return db_pt

# Read all ProductTypes
@router.get("/", response_model=list[schemas.ProductTypeRead])
async def read_product_types(db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.ProductType))
    return result.scalars().all()

# Read single ProductType
@router.get("/{pt_id}", response_model=schemas.ProductTypeRead)
async def read_product_type(pt_id: int, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.ProductType).where(models.ProductType.id == pt_id))
    pt = result.scalars().first()
    if not pt:
        raise HTTPException(status_code=404, detail="Product type not found")
    return pt

# Update ProductType
@router.put("/{pt_id}", response_model=schemas.ProductTypeRead)
async def update_product_type(pt_id: int, pt: schemas.ProductTypeCreate, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.ProductType).where(models.ProductType.id == pt_id))
    db_pt = result.scalars().first()
    if not db_pt:
        raise HTTPException(status_code=404, detail="Product type not found")

    db_pt.name = pt.name
    db_pt.description = pt.description
    await db.commit()
    await db.refresh(db_pt)
    return db_pt

# Delete ProductType
@router.delete("/{pt_id}")
async def delete_product_type(pt_id: int, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.ProductType).where(models.ProductType.id == pt_id))
    db_pt = result.scalars().first()
    if not db_pt:
        raise HTTPException(status_code=404, detail="Product type not found")

    await db.delete(db_pt)
    await db.commit()
    return {"detail": "Product type deleted"}
