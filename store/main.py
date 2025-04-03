import json
from typing import List
import logging
import logging.config
from config import LOG_DICT
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, APIRouter, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_users import jwt
import jwt
import pika
from config import connection, channel, connection_params
from cache.main import get_data, set_data, set_data_long, check_connection
from jwt import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete, update, literal_column, values
from starlette import status
from models import get_async_session, Products, Units, Category
from schemas import (Unit, Warehouses, WarehouseResponse, ProductsCreate, ProductsResponse, Categories,
                     CategoriesResponse, UnitCreateResponse, UnitCreate, WarehouseCreateResponse, WarehousesCreate,
                     CategoriesCreateResponse, CategoriesCreate, ProductsSelect)

app = FastAPI()

SECRET_KEY = "d3432h54iu3fh894utf83jfidc9238ry8923djfc92"
ALGORITHM = "HS256"

queue_name = 'hello'

security = HTTPBearer()

logging.config.dictConfig(LOG_DICT)

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

async def get_entity_by_id(id : int, entity, session: AsyncSession):
    try:
        model_id = entity.__table__.primary_key.columns.values()[0].name
        query = select(entity).where(getattr(entity, model_id) == id)
        result = await session.execute(query)
        return result.mappings().all()
    except Exception as e:
        return {"message": str(e)}

async def get_all_from_cache(key: str, entity, order, session: AsyncSession = Depends(get_async_session())):
    cache_data = await get_data(key)
    if not cache_data:
        query = select(entity).order_by(order)
        result = await session.execute(query)
        data = [obj.__dict__ for obj in result.scalars().all()]
        for item in data:
            item.pop("_sa_instance_state", None)
        data = json.dumps(data, default=str)
        await set_data_long(key, data)
        return json.loads(data)
    return json.loads(cache_data)

''' Find product by Id '''
@store_router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_product_by_id(id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        logging.info("run get_product_by_id router")
        result = await get_entity_by_id(id, Products, session)
        logging.info("router get_product_by_id router sucessful")
        return result
    except Exception as e:
        logging.error(f"error in database with input {id}", exc_info=e)

''' Add product to Basket'''
@store_router.get("/basket_add/{id}", status_code=status.HTTP_200_OK)
async def basket_add(uuid: str, id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        logging.info("run basket_add router")
        query = select(Products.name, Products.product_id, Products.price, Units.unit_name, Products.count,
                       Category.name.label("category")).join(Units, Products.unit == Units.unit_id).join(
            Category, Products.category_id == Category.category_id).where(Products.product_id == id)
        logging.info("run query for find product by id")
        result = await session.execute(query)
        channel = connection.channel()
        channel.queue_declare(queue=queue_name)
        dic = dict(result.mappings().all()[0])
        dic.update({"uuid" : uuid})
        message = str(dic)
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=message
        )
        channel.close()
        logging.info(f"Sent: '{message}'")
        await session.commit()
    except Exception as e:
        logging.error(f"error in database", exc_info=e)
        return {"error" : str(e)}

''' Select all products '''
@store_router.get("/p/all", status_code=status.HTTP_200_OK)
async def get_all_product(session: AsyncSession = Depends(get_async_session)):
    try:
        logging.info("run get_all_product router")
        query = select(Products.name, Units.unit_name, Products.count,
                       Products.price, Products.description, Products.carb, Products.protein,
                       Products.fats, Products.calories, Products.composition,
                       Products.store_condition, Category.name.label("category")).join(Units, Products.unit == Units.unit_id).join(
            Category, Products.category_id == Category.category_id).order_by(Products.name.asc())
        logging.info("run query for selecting all products")
        result = await session.execute(query)
        return result.mappings().all()
    except Exception as e:
        logging.error(f"error in database", exc_info=e)


''' Add product '''
@store_router.post("/add", status_code=status.HTTP_200_OK)
async def add_product(product: ProductsCreate, session: AsyncSession = Depends(get_async_session),
                      payload: dict = Depends(verify_token)):
    try:
        logging.info("run add_product router")
        query = insert(Products).values(**product.dict()).returning(literal_column('*'))
        logging.info("run query for inserting product into database")
        result = await session.execute(query)
        await session.commit()
        logging.info(f"product inserted successfully, Product: {result}")
        return {"status" : f"{result.mappings().all()[0]['product_id']}"}
    except Exception as ex:
        logging.error(f"error in database", exc_info=ex)
        return {"error" : str(ex)}


''' Update product '''
@store_router.put("/update/{id}", status_code=status.HTTP_200_OK)
async def update_product(product: ProductsCreate, id: int, session: AsyncSession = Depends(get_async_session)
                         , payload: dict = Depends(verify_token)):
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
async def delete_product(id: int, session: AsyncSession = Depends(get_async_session),
                         payload: dict = Depends(verify_token)):
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
@unit_router.get("/u/all", status_code=status.HTTP_200_OK , response_model=List[Unit])
async def get_all_units(session: AsyncSession = Depends(get_async_session)):
    try:
        logging.info("run get_all_units router")
        if not await check_connection():
            query = select(Units).order_by(Units.unit_name)
            logging.info("selecting units from db")
            result = await session.execute(query)
            logging.info("query was execute sucessfully")
            return result.mappings().all()
        cache_data = await get_all_from_cache('unit_all', Units, Units.unit_name, session)
        return cache_data
    except Exception as e:
        logging.error("error while selecting data from db", exc_info=e)
        return {"error" : str(e)}

''' Find unit by Id '''
@unit_router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_unit_by_id(id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        logging.info("run get_unit_by_id")
        logging.info("selecting units from cache")
        if not await check_connection():
            result = await get_entity_by_id(id, Units, session)
            return result
        try:
            cache_data = await get_all_from_cache('unit_all', Units, Units.unit_name, session)
            result = "unit does not exist"
            for i in cache_data:
                if i['Units']['unit_id'] == id:
                    result = i
            return result
        except KeyError:
            return "ID doesn't exist"
    except Exception as e:
        logging.error(f"error while selecting unit by {id} id", exc_info=e)
        return {"error" : str(e)}


''' Add unit '''
@unit_router.post("/add", status_code=status.HTTP_200_OK)
async def add_unit(unit: UnitCreate, session: AsyncSession = Depends(get_async_session),
                   payload: dict = Depends(verify_token)):
    try:
        logging.info("inserting unit into db")
        query = insert(Units).values(**unit.dict())
        result = await session.execute(query)
        logging.info("commit data")
        await session.commit()
        await get_all_from_cache('unit_all', Units, Units.unit_name, session)
        return {"status" : "Sucessfully added"}
    except Exception as ex:
        logging.error(f"error while add unit with {unit} data", exc_info=ex)
        return {"error" : str(ex)}

''' Update unit '''
@unit_router.put("/update/{id}", status_code=status.HTTP_200_OK)
async def update_unit(unit: UnitCreate, id: int, session: AsyncSession = Depends(get_async_session),
                      payload: dict = Depends(verify_token)):
    try:
        logging.info("updating unit in db")
        query = update(Units).where(Units.unit_id == id).values(**unit.dict())
        result = await session.execute(query)
        logging.info("commit execute")
        await session.commit()
        await get_all_from_cache('unit_all', Units, Units.unit_name, session)
        return {"result" : "ok"}
    except Exception as ex:
        logging.error(f"error while update unit with id: {id} and new data: {unit}", exc_info=ex)
        return {"error" : str(ex)}

''' Delete unit '''
@unit_router.delete("/delete/{id}", status_code=status.HTTP_200_OK)
async def delete_unit(id: int, session: AsyncSession = Depends(get_async_session),
                      payload: dict = Depends(verify_token)):
    try:
        logging.info("deleting unit from db")
        query = delete(Units).where(Units.unit_id == id)
        result = await session.execute(query)
        logging.info("commit execute")
        await session.commit()
        await get_all_from_cache('unit_all', Units, Units.unit_name, session)
        return {"result" : "ok"}
    except Exception as ex:
        logging.error(f"error while deleting unit with {id} id", exc_info=ex)
        return {"error" : str(ex)}

''' Select all categories '''
@category_router.get("/c/all", status_code=status.HTTP_200_OK, response_model=List[Categories])
async def get_all_categories(session: AsyncSession = Depends(get_async_session)):
    try:
        result = await get_all_from_cache('category_all', Category, Category.name, session)
        return result
    except Exception as e:
        logging.error(f"error while selecting data from db", exc_info=e)
        return {"error" : str(e)}

''' Find category by Id '''
@category_router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_category_by_id(id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        logging.info("selecting category from cache by id")
        if not await check_connection():
            result = await get_entity_by_id(id, Category, session)
            return result
        try:
            cache_data = await get_data('category_all')
            cache_data = json.loads(cache_data)
            result = "category does not exist"
            for i in cache_data:
                if i['Category']['category_id'] == id:
                    result = i
            return result
        except KeyError:
            return "ID doesn't exist"
    except Exception as e:
        logging.error(f"error while selecting data from db by {id} id", exc_info=e)


''' Add category '''
@category_router.post("/add", status_code=status.HTTP_200_OK)
async def add_category(category: CategoriesCreate, session: AsyncSession = Depends(get_async_session)):
    try:
        logging.info("inserting category")
        query = insert(Category).values(**category.dict())
        result = await session.execute(query)
        logging.info("commit data")
        await session.commit()
        await get_all_from_cache("category_all", Category, Category.name, session)
        return {"status" : "ok"}
    except Exception as ex:
        logging.error(f"error while inserting category with {category} data", exc_info=ex)
        return {"error" : str(ex)}

''' Update category '''
@category_router.put("/update/{id}", status_code=status.HTTP_200_OK)
async def update_category(category: CategoriesCreate, id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        logging.info("updating category")
        query = update(Category).where(Category.category_id == id).values(**category.dict())
        result = await session.execute(query)
        logging.info("commit data")
        await session.commit()
        await get_all_from_cache("category_all", Category, Category.name, session)
        return {"result" : "ok"}
    except Exception as ex:
        logging.error(f"error while updating category with {id} id and {category} data", exc_info=ex)
        return {"error" : str(ex)}

''' Delete category '''
@category_router.delete("/delete/{id}", status_code=status.HTTP_200_OK)
async def delete_category(id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        logging.info("deleting category")
        query = delete(Category).where(Category.category_id == id)
        result = await session.execute(query)
        logging.info("commit data")
        await session.commit()
        await get_all_from_cache("category_all", Category, Category.name, session)
        return {"result" : "ok"}
    except Exception as ex:
        logging.error(f"error while deleting category with {id} id", exc_info=ex)
        return {"error" : str(ex)}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(store_router)
app.include_router(unit_router)
app.include_router(warehouse_router)
app.include_router(category_router)