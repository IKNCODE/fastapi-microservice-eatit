from fastapi import Request

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, APIRouter, Response, status
from fastapi.openapi.docs import get_swagger_ui_html
from sqlalchemy.orm import Session

from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, insert, delete, func

from models import get_async_session, User
from schemas import UserSchema, UserCreate
from database_func.db import get_password_hash, verify_password, create_jwt_token, get_current_user, verify_login
import json
from faststream import FastStream
from faststream.kafka import KafkaBroker
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
        if not await verify_login(user_dict['login'], session):
            response.status_code = status.HTTP_401_UNAUTHORIZED
            raise HTTPException(status_code=401, detail="Incorrect username or password")

        if await verify_password(user_dict['password'], result.scalars().first().hashed_password) == True:
            access_token = await create_jwt_token({"sub": str(user_dict.get("login"))})
            response.set_cookie("Authorization", access_token, httponly=True)
            return {"Authorization": access_token, "status": "ok"}
        else:
            return {"error": "Wrong credentials"}
    except Exception as e:
        return {"error" : str(e)}

@auth_router.post("/logout")
async def logout(response: Response, session: Session = Depends(get_async_session)):
    try:
        response.delete_cookie("Authorization")
        return {"status": "ok"}
    except Exception as e:
        return {"error" : str(e)}


@app.get(app.root_path + "/openapi.json")
async def custom_swagger_ui_html():
    return app.openapi()

origins = [
    "http://localhost:8082",
    "http://127.0.0.1:8082"
]



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


