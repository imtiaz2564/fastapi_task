from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .database import async_session_maker
from . import models, schemas, utils

router = APIRouter(prefix="/auth", tags=["auth"])

async def get_db():
    async with async_session_maker() as session:
        yield session

@router.post("/register", response_model=schemas.UserOut)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).filter(models.User.username == user.username))
    if result.scalar():
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_pw = utils.hash_password(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.TokenOut)
async def login(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).filter(models.User.username == user.username))
    db_user = result.scalar()
    if not db_user or not utils.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = utils.create_access_token({"sub": str(db_user.id)})
    new_session = models.TokenSession(user_id=db_user.id, token=token)
    db.add(new_session)
    await db.commit()
    return {"access_token": token, "token_type": "bearer"}

@router.post("/logout")
async def logout(token: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.TokenSession).filter(models.TokenSession.token == token))
    session = result.scalar()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    await db.delete(session)
    await db.commit()
    return {"message": "Logged out successfully"}

