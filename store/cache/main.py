import redis
from redis import asyncio

from cache.config import r, TTL, LONG_TTL

async def check_connection():
    try:
        if r.ping():
            return True
        else:
            return False
    except redis.exceptions.ConnectionError:
        return False

async def set_data(key, value):
    try:
        await r.setex(key, TTL, value)
        return True
    except Exception:
        return False
async def set_data_long(key, value):
    try:
        await r.setex(key, LONG_TTL, value)
        return True
    except Exception:
        return False


async def get_data(key):
    try:
        a = r.get(key)
        return a
    except Exception as e:
        return e