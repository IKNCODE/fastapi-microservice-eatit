from pydantic import BaseModel, Field
from models import Units, Products

class Unit(BaseModel):
    unit_name: str


class Warehouses(BaseModel):
    location: str

class WarehouseResponse(BaseModel):
    Warehouse: Warehouses = Field()

class UnitResponse(BaseModel):
    Units: Unit = Field()

class ProductsCreate(BaseModel):
    name: str
    unit: int
    warehouse_id: int
    count: int
    price: int

class ProductsResponse(BaseModel):
    Products: ProductsCreate = Field()

