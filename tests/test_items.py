import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from PIL import Image
from reportlab.pdfgen import canvas
# from . import models, schemas, database
from app import models, schemas, database

router = APIRouter(prefix="/items", tags=["items"])

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_IMAGE_PATH = os.path.join(BASE_DIR, "static", "base_image.jpg")
PDF_DIR = os.path.join(BASE_DIR, "generated_pdfs")
os.makedirs(PDF_DIR, exist_ok=True)


async def generate_pdf(item_id: int, width: float, height: float) -> str:
    """Helper to crop image and generate PDF, returning relative path."""
    try:
        with Image.open(BASE_IMAGE_PATH) as img:
            crop_box = (0, 0, int(width), int(height))
            cropped_img = img.crop(crop_box)
            temp_path = os.path.join(PDF_DIR, f"temp_{item_id}.jpg")
            cropped_img.save(temp_path)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"item_{item_id}_{timestamp}.pdf"
            pdf_path = os.path.join(PDF_DIR, pdf_filename)

            c = canvas.Canvas(pdf_path)
            c.drawImage(temp_path, 50, 400, width=width, height=height)
            c.drawString(50, 380, f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            c.save()

            os.remove(temp_path)
            return f"app/generated_pdfs/{pdf_filename}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")


# CREATE
@router.post("/", response_model=schemas.ItemRead)
async def create_item(item: schemas.ItemCreate, db: AsyncSession = Depends(database.get_db)):
    # Validate Material
    result = await db.execute(select(models.Material).where(models.Material.id == item.material_id))
    material = result.scalars().first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    # Validate Product Type
    result = await db.execute(select(models.ProductType).where(models.ProductType.id == item.product_type_id))
    pt = result.scalars().first()
    if not pt:
        raise HTTPException(status_code=404, detail="Product type not found")

    # Create DB record
    db_item = models.Item(
        material_id=item.material_id,
        product_type_id=item.product_type_id,
        width=item.width,
        height=item.height,
        pdf_path=None
    )
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)

    # Generate PDF
    db_item.pdf_path = await generate_pdf(db_item.id, item.width, item.height)
    await db.commit()
    await db.refresh(db_item)

    return db_item


# READ ALL
@router.get("/", response_model=list[schemas.ItemRead])
async def read_items(db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.Item))
    return result.scalars().all()


# READ ONE
@router.get("/{item_id}", response_model=schemas.ItemRead)
async def read_item(item_id: int, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.Item).where(models.Item.id == item_id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


# UPDATE
@router.put("/{item_id}", response_model=schemas.ItemRead)
async def update_item(item_id: int, item: schemas.ItemCreate, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.Item).where(models.Item.id == item_id))
    db_item = result.scalars().first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Update fields
    db_item.material_id = item.material_id
    db_item.product_type_id = item.product_type_id
    db_item.width = item.width
    db_item.height = item.height

    # Regenerate PDF
    db_item.pdf_path = await generate_pdf(db_item.id, item.width, item.height)

    await db.commit()
    await db.refresh(db_item)
    return db_item


# DELETE
@router.delete("/{item_id}")
async def delete_item(item_id: int, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.Item).where(models.Item.id == item_id))
    db_item = result.scalars().first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Delete PDF if exists
    if db_item.pdf_path:
        pdf_full_path = os.path.join(BASE_DIR, os.path.relpath(db_item.pdf_path, "app"))
        if os.path.exists(pdf_full_path):
            os.remove(pdf_full_path)

    await db.delete(db_item)
    await db.commit()
    return {"detail": "Item deleted"}
