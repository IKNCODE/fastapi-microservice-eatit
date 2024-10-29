from itertools import product
from typing import List
import logging
import logging.config
import pythonjsonlogger
from config import LOG_DICT
from fastapi import FastAPI, Depends, HTTPException, APIRouter, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_users import jwt
import jwt
from jwt import PyJWTError
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, delete, func, update
from starlette import status

from models import get_async_session, Products, Units, Warehouse, Category
from schemas import (Unit, Warehouses, WarehouseResponse, UnitResponse, ProductsResponse, ProductsCreate, Categories,
                     CategoriesResponse)

from faststream import FastStream, Logger
from faststream.kafka import KafkaBroker



app = FastAPI()

SECRET_KEY = "d3432h54iu3fh894utf83jfidc9238ry8923djfc92"
ALGORITHM = "HS256"

security = HTTPBearer()

logging.config.dictConfig(LOG_DICT)

logging.error('ddddd')
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

store_router = APIRouter(prefix="/store", tags=["Store"])
unit_router = APIRouter(prefix="/unit", tags=["Unit"])
warehouse_router = APIRouter(prefix="/warehouse", tags=["Warehouse"])
category_router = APIRouter(prefix="/category", tags=["Category"])


@store_router.get("/protected-endpoint")
async def protected_endpoint(payload: dict = Depends(verify_token)):
    return {"message": "This is a protected endpoint", "payload": payload}

''' Find product by Id '''
@store_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=List[ProductsResponse])
async def get_product_by_id(id: int, session: Session = Depends(get_async_session)):
    try:
        logging.info("run get_product_by_id router")
        query = select(Products).where(Products.product_id == id)
        result = await session.execute(query)
        logging.info("router get_product_by_id router sucessful")
        return result.mappings().all()
    except Exception as e:
        logging.error(f"error in database with input {id}", exc_info=e)


''' Select all products '''
@store_router.get("/p/all", status_code=status.HTTP_200_OK, response_model=List[ProductsResponse])
async def get_all_product(session: Session = Depends(get_async_session)):
    try:
        logging.info("run get_all_product router")
        query = select(Products).order_by(Products.name.asc())
        logging.info("run query for selecting all products")
        result = await session.execute(query)
        return result
    except Exception as e:
        logging.error(f"error in database", exc_info=e)

''' Add product '''
@store_router.post("/add", status_code=status.HTTP_200_OK)
async def add_product(product: ProductsCreate, session: Session = Depends(get_async_session)):
    try:
        logging.info("run add_product router")
        query = insert(Products).values(**product.dict())
        logging.info("run query for inserting product into database")
        result = await session.execute(query)
        await session.commit()
        logging.info("product inserted successfully")
        return {"status" : "ok"}
    except Exception as ex:
        logging.error(f"error in database", exc_info=ex)
        return {"error" : str(ex)}

''' Update product '''
@store_router.put("/update/{id}", status_code=status.HTTP_200_OK)
async def update_product(product: ProductsCreate, id: int, session: Session = Depends(get_async_session)):
    try:
        logging.info("run update_product router")
        query = update(Products).where(Products.product_id == id).values(**product.dict())
        logging.info("run query for updating product into database")
        result = await session.execute(query)
        await session.commit()
        logging.info("product updated successfully")
        return {"result" : "ok"}
    except Exception as ex:
        logging.error(f"error in database while update products with id: {id} and new data: {product}", exc_info=ex)
        return {"error" : str(ex)}

''' Delete product '''
@store_router.delete("/delete/{id}", status_code=status.HTTP_200_OK)
async def delete_product(id: int, session: Session = Depends(get_async_session)):
    try:
        logging.info("run delete_product router")
        query = delete(Products).where(Products.product_id == id)
        logging.info("run query for deleting product into database")
        result = await session.execute(query)
        await session.commit()
        logging.info("product deleted successfully")
        return {"result" : "ok"}
    except Exception as ex:
        logging.error(f"error in database", exc_info=ex)
        return {"error" : str(ex)}

''' Select all units '''
@unit_router.get("/u/all", status_code=status.HTTP_200_OK, response_model=List[UnitResponse])
async def get_all_units(session: Session = Depends(get_async_session)):
    try:
        logging.info("run get_all_units router")
        query = select(Units).order_by(Units.unit_name)
        logging.info("selecting units from db")
        result = await session.execute(query)
        logging.info("query was execute sucessfully")
        return result
    except Exception as e:
        logging.error("error while selecting data from db", exc_info=e)
        return {"error" : str(e)}

''' Find unit by Id '''
@unit_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=List[UnitResponse])
async def get_unit_by_id(id: int, session: Session = Depends(get_async_session)):
    try:
        logging.info("run get_unit_by_id")
        logging.info("selecting units from db")
        query = select(Units).where(Units.unit_id == id)
        result = await session.execute(query)
        return result.mappings().all()
    except Exception as e:
        logging.error(f"error while selecting unit by {id} id", exc_info=e)
        return {"error" : str(e)}


''' Add unit '''
@unit_router.post("/add", status_code=status.HTTP_200_OK)
async def add_unit(unit: Unit, session: Session = Depends(get_async_session)):
    try:
        logging.info("inserting unit into db")
        query = insert(Units).values(**unit.dict())
        result = await session.execute(query)
        logging.info("commit data")
        await session.commit()
        return {"status" : "ok"}
    except Exception as ex:
        logging.error(f"error while add unit with {unit} data", exc_info=ex)
        return {"error" : str(ex)}

''' Update unit '''
@unit_router.put("/update/{id}", status_code=status.HTTP_200_OK)
async def update_unit(unit: Unit, id: int, session: Session = Depends(get_async_session)):
    try:
        logging.info("updating unit in db")
        query = update(Units).where(Units.unit_id == id).values(**unit.dict())
        result = await session.execute(query)
        logging.info("commit execute")
        await session.commit()
        return {"result" : "ok"}
    except Exception as ex:
        logging.error(f"error while update unit with id: {id} and new data: {unit}", exc_info=ex)
        return {"error" : str(ex)}

''' Delete unit '''
@unit_router.delete("/delete/{id}", status_code=status.HTTP_200_OK)
async def delete_unit(id: int, session: Session = Depends(get_async_session)):
    try:
        logging.info("deleting unit from db")
        query = delete(Units).where(Units.unit_id == id)
        result = await session.execute(query)
        logging.info("commit execute")
        await session.commit()
        return {"result" : "ok"}
    except Exception as ex:
        logging.error(f"error while deleting unit with {id} id", exc_info=ex)
        return {"error" : str(ex)}

''' Select all warehouses '''
@warehouse_router.get("/w/all", status_code=status.HTTP_200_OK, response_model=List[WarehouseResponse])
async def get_all_units(session: Session = Depends(get_async_session)):
    try:
        logging.info("selecting warehouses from db")
        query = select(Warehouse).order_by(Warehouse.warehouse_id)
        result = await session.execute(query)
        logging.info("query was execute sucessfully")
        return result
    except Exception as e:
        logging.error(f"error while selecting data from db", exc_info=e)
        return {"error" : str(e)}

''' Find warehouse by Id '''
@warehouse_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=List[WarehouseResponse])
async def get_unit_by_id(id: int, session: Session = Depends(get_async_session)):
    try:
        logging.info("selecting warehouses from db by id")
        query = select(Warehouse).where(Warehouse.warehouse_id == id)
        result = await session.execute(query)
        logging.info("query was execute sucessfully")
        return result.mappings().all()
    except Exception as e:
        logging.error(f"error while selecting unit by {id} id", exc_info=e)
        return {"error" : str(e)}


''' Add warehouse '''
@warehouse_router.post("/add", status_code=status.HTTP_200_OK)
async def add_unit(warehouse: Warehouses, session: Session = Depends(get_async_session)):
    try:
        logging.info("inserting warehouse into db")
        query = insert(Warehouse).values(**warehouse.dict())
        result = await session.execute(query)
        logging.info("commit data")
        await session.commit()
        return {"status" : "ok"}
    except Exception as ex:
        logging.error(f"error while inserting warehouse with {warehouse} data", exc_info=ex)
        return {"error" : str(ex)}

''' Update warehouse '''
@warehouse_router.put("/update/{id}", status_code=status.HTTP_200_OK)
async def update_unit(warehouse: Warehouses, id: int, session: Session = Depends(get_async_session)):
    try:
        logging.info("updating warehouse")
        query = update(Warehouse).where(Warehouse.warehouse_id == id).values(**warehouse.dict())
        result = await session.execute(query)
        logging.info("commit data")
        await session.commit()
        return {"result" : "ok"}
    except Exception as ex:
        logging.error(f"error while updating warehouse with {id} id and new data: {warehouse}", exc_info=ex)
        return {"error" : str(ex)}

''' Delete warehouse '''
@warehouse_router.delete("/delete/{id}", status_code=status.HTTP_200_OK)
async def delete_ware(id: int, session: Session = Depends(get_async_session)):
    try:
        logging.info("deleting warehouse")
        query = delete(Warehouse).where(Warehouse.warehouse_id == id)
        result = await session.execute(query)
        logging.info("commit execute")
        await session.commit()
        return {"result" : "ok"}
    except Exception as ex:
        logging.error(f"error while deleting warehouse by {id} id", exc_info=ex)
        return {"error" : str(ex)}


''' Select all categories '''
@category_router.get("/c/all", status_code=status.HTTP_200_OK, response_model=List[CategoriesResponse])
async def get_all_categories(session: Session = Depends(get_async_session)):
    try:
        logging.info("selecting categories from db")
        query = select(Category).order_by(Category.category_id)
        result = await session.execute(query)
        logging.info("query was execute sucessfully")
        return result
    except Exception as e:
        logging.error(f"error while selecting data from db", exc_info=e)
        return {"error" : str(e)}

''' Find category by Id '''
@category_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=List[CategoriesResponse])
async def get_category_by_id(id: int, session: Session = Depends(get_async_session)):
    try:
        logging.info("selecting categories from db by id")
        query = select(Category).where(Category.category_id == id)
        result = await session.execute(query)
        logging.info("query was execute sucessfully")
        return result.mappings().all()
    except Exception as e:
        logging.error(f"error while selecting data from db by {id} id", exc_info=e)


''' Add category '''
@category_router.post("/add", status_code=status.HTTP_200_OK)
async def add_category(category: Categories, session: Session = Depends(get_async_session)):
    try:
        logging.info("inserting category")
        query = insert(Category).values(**category.dict())
        result = await session.execute(query)
        logging.info("commit data")
        await session.commit()
        return {"status" : "ok"}
    except Exception as ex:
        logging.error(f"error while inserting category with {category} data", exc_info=ex)
        return {"error" : str(ex)}

''' Update category '''
@category_router.put("/update/{id}", status_code=status.HTTP_200_OK)
async def update_category(category: Categories, id: int, session: Session = Depends(get_async_session)):
    try:
        logging.info("updating category")
        query = update(Category).where(Category.category_id == id).values(**category.dict())
        result = await session.execute(query)
        logging.info("commit data")
        await session.commit()
        return {"result" : "ok"}
    except Exception as ex:
        logging.error(f"error while updating category with {id} id and {category} data", exc_info=ex)
        return {"error" : str(ex)}

''' Delete category '''
@category_router.delete("/delete/{id}", status_code=status.HTTP_200_OK)
async def delete_category(id: int, session: Session = Depends(get_async_session)):
    try:
        logging.info("deleting category")
        query = delete(Category).where(Category.category_id == id)
        result = await session.execute(query)
        logging.info("commit data")
        await session.commit()
        return {"result" : "ok"}
    except Exception as ex:
        logging.error(f"error while deleting category with {id} id", exc_info=ex)
        return {"error" : str(ex)}

app.include_router(store_router)
app.include_router(unit_router)
app.include_router(warehouse_router)
app.include_router(category_router)