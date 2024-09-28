from pydantic import BaseModel, Field
from models import Units
class Unit(BaseModel):
    unit_name: str

class UnitResponse(BaseModel):
    Units: Unit = Field()

class Warehouse(BaseModel):
    location: str
class Products(BaseModel):
    name: str
    unit: Unit
    warehouse: Warehouse
    quantity: int
    price: int

