import redis


r = redis.Redis(host='localhost', port=6379, db=0)

TTL = 200
LONG_TTL = 60 * 60 * 24 * 365
print(r)