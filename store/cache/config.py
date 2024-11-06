import os

import redis

redis_host = os.environ.get('REDIS_HOST')

r = redis.Redis(host=redis_host, port=6379, db=0)

TTL = 200
LONG_TTL = 60 * 60 * 24 * 365
