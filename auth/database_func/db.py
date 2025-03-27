import datetime

import jwt
from fastapi import Depends, Request, HTTPException
from jose import JWTError

from models import get_async_session
from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER, ALGORITHM, SECRET_KEY
from typing import AsyncGenerator

from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from passlib.context import CryptContext

from models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # Используем библиотеку passlib для проверки и
                                                                   # получения пароля используя различные алгоритмы

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
async def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def check_jwt_cookie(request: Request):
    acc_tkn = request.cookies.get("Authorization")
    if acc_tkn is None:
        raise HTTPException(status_code=401, detail="Access token is missing")
    return acc_tkn



async def get_current_user(token: str = Depends(check_jwt_cookie), session: AsyncSession = Depends(get_async_session)):
    try:
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=401, detail="Token is invalid")
        expired = decoded_token.get("exp")
        expire_time = datetime.datetime.fromtimestamp(int(expired), tz=datetime.timezone.utc)
        if expire_time < datetime.datetime.now(datetime.timezone.utc):
            raise HTTPException(status_code=401, detail="Token is expired")
        user_login = decoded_token.get("sub")
        if not user_login:
            raise HTTPException(status_code=401, detail="Token is invalid")
        user = select(User).where(User.login == str(user_login))
        user = await session.execute(user)
        if not user:
            raise HTTPException(status_code=401, detail="User does not exist")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

async def verify_login(login: str, session: AsyncSession = Depends(get_async_session)) -> bool:
    user = select(User).where(User.login == str(login))
    user = await session.execute(user)
    if not user.scalars().all():
        return False
    return True

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def create_jwt_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=30)
    to_encode.update({'exp': expire})
    encoded = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded




