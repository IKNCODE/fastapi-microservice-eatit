from fastapi import FastAPI, Depends, HTTPException, APIRouter, Response
from sqlalchemy.orm import Session
from starlette import status
from sqlalchemy import select, insert, delete, func

from models import get_async_session, User
from schemas import UserSchema, UserCreate
from database_func.db import get_password_hash, verify_password, create_jwt_token, get_current_user

app = FastAPI()

auth_router = APIRouter(prefix="/auth", tags=["Auth"]) # Authorization routers



@app.get("/check")
async def root(user: User = Depends(get_current_user)):
    return {"Hello": "World"}

@auth_router.post("/register")
async def register(user_data: UserCreate, session: Session = Depends(get_async_session)):
    try:
        user_dict = dict(user_data)
        user_dict.pop('password')
        user_dict['hashed_password'] = await get_password_hash(user_data.password)
        print(user_dict)
        query = insert(User).values(**user_dict)
        await session.execute(query)
        await session.commit()
        return {"message" : "OK!"}
    except Exception as e:
        return {"error" : str(e)}

@auth_router.post("/login")
async def login(response: Response, user_data: UserSchema, session: Session = Depends(get_async_session)):
    try:
        user_dict = dict(user_data)
        query = select(User).where(User.login == user_dict['login'])
        result = await session.execute(query)
        if await verify_password(user_dict['password'], result.scalars().first().hashed_password) == True:
            access_token = await create_jwt_token({"sub": str(user_dict.get("login"))})
            response.set_cookie("access_token", access_token, httponly=True)
            return {"access_token": access_token, "status": "ok"}
    except Exception as e:
        return {"error" : str(e)}



app.include_router(auth_router)


