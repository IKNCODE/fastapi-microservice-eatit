from dotenv import load_dotenv

import os

load_dotenv()

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')

LOG_DICT = {
    'version': 1,
    'disable_existing_loggers': False,
    'root' : {
        'handlers': ['default', 'file'],
        'level': 'INFO',
    },
    'formatters' : {
        'standard' : {
            'format' : '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        },
    },
    'handlers' : {
        'default' : {
            'level' : 'INFO',
            'formatter' : 'standard',
            'class' : 'logging.StreamHandler',

        },
        "file":{
            "formatter":"standard",
            "class":"logging.FileHandler",
            "level":"INFO",
            "filename":"./logs/host_metrics_app.log",
            'mode' : 'a',
        }
    },

}

DB_CONN = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"