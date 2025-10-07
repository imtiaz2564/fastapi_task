from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.db import models, schemas, database

router = APIRouter(prefix="/materials", tags=["materials"])


# CREATE Material
@router.post("/", response_model=schemas.MaterialRead)
async def create_material(material: schemas.MaterialCreate, db: AsyncSession = Depends(database.get_db)):
    db_material = models.Material(name=material.name, description=material.description)
    db.add(db_material)
    try:
        await db.commit()
        await db.refresh(db_material)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Material with this name already exists")
    return db_material


# READ all Materials
@router.get("/", response_model=list[schemas.MaterialRead])
async def get_materials(db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.Material))
    return result.scalars().all()


# READ single Material by ID
@router.get("/{material_id}", response_model=schemas.MaterialRead)
async def get_material(material_id: int, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.Material).where(models.Material.id == material_id))
    material = result.scalars().first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return material


# UPDATE Material
@router.put("/{material_id}", response_model=schemas.MaterialRead)
async def update_material(material_id: int, material: schemas.MaterialCreate,
                          db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.Material).where(models.Material.id == material_id))
    db_material = result.scalars().first()
    if not db_material:
        raise HTTPException(status_code=404, detail="Material not found")

    db_material.name = material.name
    db_material.description = material.description

    try:
        await db.commit()
        await db.refresh(db_material)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Material with this name already exists")

    return db_material


# DELETE Material
@router.delete("/{material_id}")
async def delete_material(material_id: int, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.Material).where(models.Material.id == material_id))
    db_material = result.scalars().first()
    if not db_material:
        raise HTTPException(status_code=404, detail="Material not found")

    await db.delete(db_material)
    await db.commit()
    return {"detail": "Material deleted"}
