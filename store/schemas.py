from typing import Annotated, Optional

from pydantic import BaseModel, Field, validator
from models import Units, Products, Category

class Unit(BaseModel):
    unit_id : int
    unit_name: str

class UnitCreate(BaseModel):
    unit_name : str

class UnitCreateResponse(BaseModel):
    Unit: UnitCreate = Field()

class UnitResponse(BaseModel):
    Units: Unit = Field()

class Categories(BaseModel):
    category_id : int
    name: str
    description: str

class CategoriesCreate(BaseModel):
    name: str
    description: str

class CategoriesResponse(BaseModel):
    Category: Categories = Field()

class CategoriesCreateResponse(BaseModel):
    Category: CategoriesCreate = Field()

class ProductsCreate(BaseModel):
    name: str
    unit: int
    article: str
    count: int
    price: int
    description: str
    carb: int
    protein: int
    fats: int
    calories: int
    composition: str
    store_condition: str
    category_id: int

class ProductsSelect(BaseModel):
    name: str
    unit_name: str
    article: Optional[str] = ""
    count: int
    price: int
    description: str
    carb: int
    protein: int
    fats: int
    calories: int
    composition: str
    store_condition: str
    category: str

    @validator("article")
    def validate_notes(cls, article):
        return article if article is not None else ""




class ProductsResponse(BaseModel):
    Products: ProductsCreate = Field()

