import json
from typing import List
import logging
import logging.config
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, APIRouter, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_users import jwt
import jwt
import pika
from jwt import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete, update, literal_column, values
from starlette import status
from models import get_async_session, Warehouses, ProductsWarehouses, Products
from schemas import WarehouseResponse, WarehouseCreateResponse, Warehouse, ProductCreate

app = FastAPI()

warehouse_router = APIRouter(tags=["warehouse"], prefix="/warehouse")
inventory_router = APIRouter(tags=["inventory"], prefix="/inventory")

''' Get all warehouses Router '''
@warehouse_router.get('/w/all')
async def get_all_warehouses(session: AsyncSession = Depends(get_async_session)):
    try:
        logging.info(f"Getting all warehouses")
        query = select(Warehouses.warehouse_id, Warehouses.name, Warehouses.latitude,
                       Warehouses.longitude).order_by(Warehouses.warehouse_id)
        result = await session.execute(query)
        logging.error(f"Successfully fetched all warehouses")
        return result.mappings().all()
    except AttributeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logging.error("Error in get_all_warehouses: %s", e)
        return {"error" : e}

''' Get all products from warehouse Router '''
@warehouse_router.get("/all_products/{id}", status_code=status.HTTP_200_OK)
async def get_products_from_warehouse(id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        logging.info("run get_warehouse_by_id router")
        query = (select(ProductsWarehouses.products_warehouses_id, Products.product_id.label("product_id"),
                        Products.articles.label("article"), Products.count.label("count"))
                 .join(Products, Products.product_id == ProductsWarehouses.product_id)
                 .where(ProductsWarehouses.warehouse_id == id))
        result = await session.execute(query)
        logging.info("router get_warehouse_by_id router sucessful")
        return result.mappings().all()
    except Exception as e:
        logging.error(f"error in database with input {id}", exc_info=e)

''' Get warehouse by ID Router '''
@warehouse_router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_warehouse_by_id(id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        logging.info("run get_warehouse_by_id router")
        query = select(Warehouses.warehouse_id, Warehouses.name,
                       Warehouses.latitude, Warehouses.longitude).where(Warehouses.warehouse_id == id)
        result = await session.execute(query)
        logging.info("router get_warehouse_by_id router sucessful")
        return result.mappings().all()
    except Exception as e:
        logging.error(f"error in database with input {id}", exc_info=e)

''' Add warehouse Router '''
@warehouse_router.post('/add')
async def add_warehouse(warehouse: WarehouseCreateResponse, session: AsyncSession = Depends(get_async_session)):
    try:
        logging.info(f"Add into warehouses")
        query = insert(Warehouses).values(**warehouse.dict())
        result = await session.execute(query)
        await session.commit()
        logging.info(f"Successfully add into warehouse: {warehouse.dict()}")
        return {"result" : "ok"}
    except Exception as e:
        logging.error("Error in get_all_warehouses: %s", e)
        return {"error" : e}

''' Get all products from warehouses Router '''
@inventory_router.get('/all')
async def get_all_products(session: AsyncSession = Depends(get_async_session)):
    try:
        logging.info(f"Get all products")
        query = (select(Products.product_id, Products.articles, Products.count,
                       ProductsWarehouses.warehouse_id, Warehouses.name.label("warehouse_name"))
                       .join(ProductsWarehouses, Products.product_id == ProductsWarehouses.product_id)
                       .join(Warehouses, ProductsWarehouses.warehouse_id == Warehouses.warehouse_id))
        result = await session.execute(query)
        logging.info("router get_all_products router sucessful")
        return result.mappings().all()
    except AttributeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logging.error("Error in get_all_warehouses: %s", e)
        return {"error" : e}

''' Add product to warehouses Router '''
@inventory_router.post('/add')
async def get_all_products(product: ProductCreate, w_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        logging.info(f"Add product")
        query = insert(Products).values(**product.dict()).returning(literal_column('*'))
        result = await session.execute(query)
        await session.commit()
        new_prod = result.mappings().all()
        prodWareQuery = insert(ProductsWarehouses).values(warehouse_id=w_id, product_id=new_prod[0]['product_id'])
        await session.execute(prodWareQuery)
        await session.commit()
        logging.info("router get_all_products router sucessful")
        return new_prod
    except AttributeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logging.error("Error in get_all_warehouses: %s", e)
        return {"error" : e}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(warehouse_router)
app.include_router(inventory_router)
