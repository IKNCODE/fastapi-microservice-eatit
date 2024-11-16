from config import r, TTL, LONG_TTL


def set_data(key, value):
    try:
        r.setex(key, TTL, value)
        return True
    except Exception as e:
        return False
def set_data_long(key, value : dict):
    try:
        r.setex(key, LONG_TTL, value)
        return True
    except Exception as e:
        print(e)
        return False


def update_data(key, value):
    try:
        r.append(key, value)
        return True
    except Exception:
        return False

def get_data(key):
    try:
        a = r.get(key)
        return a
    except Exception as e:
        return e

