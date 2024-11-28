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
from models import get_async_session, Warehouses
from schemas import WarehouseResponse, WarehouseCreateResponse, Warehouse

app = FastAPI()

warehouse_router = APIRouter(tags=["warehouse"], prefix="/warehouse")

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(warehouse_router)
