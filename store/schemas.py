from pydantic import BaseModel, Field
from models import Units, Products, Category

class Unit(BaseModel):
    unit_name: str


class Warehouses(BaseModel):
    longitude: float
    latitude: float

class WarehouseResponse(BaseModel):
    Warehouse: Warehouses = Field()

class UnitResponse(BaseModel):
    Units: Unit = Field()

class Categories(BaseModel):
    name: str
    descr: str

class CategoriesResponse(BaseModel):
    Category: Categories = Field()

class CategoryResponse(BaseModel):
    CategoryResponse: Categories = Field()

class ProductsCreate(BaseModel):
    name: str
    unit: int
    warehouse_id: int
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

class ProductsResponse(BaseModel):
    Products: ProductsCreate = Field()

