from typing import List

from fastapi import FastAPI, Depends, HTTPException, APIRouter, Response
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, delete, func
from starlette import status

from models import get_async_session, Products, Units, Warehouse
from schemas import Products, Unit, Warehouse, UnitResponse


app = FastAPI()

store_router = APIRouter(prefix="/store", tags=["store"])

@store_router.get("/unit/all", status_code=status.HTTP_200_OK, response_model=List[UnitResponse])
async def get_all_units(session: Session = Depends(get_async_session)):
    query = select(Units).order_by(Units.unit_name)
    result = await session.execute(query)
    return result.mappings().all()



app.include_router(store_router)