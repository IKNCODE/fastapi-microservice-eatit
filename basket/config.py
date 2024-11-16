import redis


r = redis.Redis(host='redis', port=6379, db=0)

TTL = 200
LONG_TTL = 60 * 60 * 24 * 365