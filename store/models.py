from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from config import *
from typing import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, Float, String, ForeignKey, Boolean, TIMESTAMP, Text

engine = create_async_engine(DB_CONN)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

class BaseModel(DeclarativeBase):
    pass
class Warehouse(BaseModel):
    __tablename__ = "warehouse"

    warehouse_id = Column(Integer, primary_key=True, autoincrement=True)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)

class Units(BaseModel):
    __tablename__ = "units"

    unit_id = Column(Integer, primary_key=True, autoincrement=True)
    unit_name = Column(String, nullable=False)

class Category(BaseModel):
    __tablename__ = "category"
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)

class Products(BaseModel):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    unit = Column(Integer, ForeignKey("units.unit_id"), nullable=False)
    count = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouse.warehouse_id"), nullable=False)
    description = Column(String, nullable=False)
    carb = Column(Integer, nullable=False)
    protein = Column(Integer, nullable=False)
    fats = Column(Integer, nullable=False)
    calories = Column(Integer, nullable=False)
    composition = Column(String, nullable=False)
    store_condition = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("category.category_id"), nullable=False)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


