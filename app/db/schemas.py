from pydantic import BaseModel, ConfigDict, constr
from typing import Optional


# Users
class UserOut(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)

class TokenOut(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)

# Materials
class MaterialCreate(BaseModel):
    name: constr(min_length=1)
    description: str | None = None

class MaterialRead(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)

# Product Types
class ProductTypeCreate(BaseModel):
    name: str
    description: str | None = None

class ProductTypeRead(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)

# Items
class ItemCreate(BaseModel):
    material_id: int
    product_type_id: int
    width: float
    height: float

class ItemRead(BaseModel):
    id: int
    material_id: int
    product_type_id: int
    width: float
    height: float
    pdf_path: str | None

    model_config = ConfigDict(from_attributes=True)
