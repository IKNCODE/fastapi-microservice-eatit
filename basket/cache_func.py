from config import r, TTL, LONG_TTL

async def set_data(key, value):
    try:
        await r.setex(key, TTL, value)
        return True
    except Exception as e:
        return False
def set_data_long(key, value):
    try:
        r.setex(key, LONG_TTL, value)
        return True
    except Exception as e:
        return False


async def get_data(key):
    try:
        a = r.get(key)
        return a
    except Exception as e:
        return e