from pydantic import BaseModel, Field
from models import Warehouses

class Warehouse(BaseModel):
    warehouse_id: int
    name: str
    longitude: float
    latitude: float

class WarehouseResponse(BaseModel):
    Warehouses: Warehouse = Field()
class WarehouseCreateResponse(BaseModel):
    name: str
    longitude: float
    latitude: float
