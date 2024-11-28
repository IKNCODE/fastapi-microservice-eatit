from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from config import *
from typing import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, Float, String, ForeignKey, Boolean, TIMESTAMP, Text

engine = create_async_engine(DB_CONN)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

class BaseModel(DeclarativeBase):
    pass

class Products(BaseModel):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    articles = Column(Integer, nullable=False)
    count = Column(Integer, nullable=False)

class Warehouses(BaseModel):
    __tablename__ = "warehouses"

    warehouse_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)

class ProductsWarehouses(BaseModel):
    __tablename__ = "products_warehouses"

    products_warehouses_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.warehouse_id"), nullable=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session