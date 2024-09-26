from dotenv import load_dotenv

import os

load_dotenv()

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')

SECRET_KEY = "d3432h54iu3fh894utf83jfidc9238ry8923djfc92"
ALGORITHM = "HS256"

DB_CONN = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"