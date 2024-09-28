from pydantic import BaseModel, Field
from models import Units, Products
class Unit(BaseModel):
    unit_name: str

class UnitResponse(BaseModel):
    Units: Unit = Field()

class Warehouse(BaseModel):
    location: str
class ProductsCreate(BaseModel):
    name: str
    unit: Unit
    warehouse: Warehouse
    quantity: int
    price: int

class ProductsResponse(BaseModel):
    Products: ProductsCreate = Field()

