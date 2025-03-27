import sys

from dotenv import load_dotenv
import pythonjsonlogger
import pika
from pika.exceptions import AMQPConnectionError
import os

load_dotenv()

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')



# Параметры подключения
connection_params = pika.ConnectionParameters(
    host='localhost',  # Замените на адрес вашего RabbitMQ сервера
    port=5672,          # Порт по умолчанию для RabbitMQ
    virtual_host='/',   # Виртуальный хост (обычно '/')
    credentials=pika.PlainCredentials(
        username='guest',  # Имя пользователя по умолчанию
        password='guest'   # Пароль по умолчанию
    ),
    heartbeat=0
)
connection = None
channel = None
# Установка соединения
try:
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
except AMQPConnectionError:
    print("Ошибка AMQPConnectionError! Невозможно подключиться к брокеру сообщений!")




log_file = os.path.join(os.path.dirname(__file__), "logs/host_metrics_app.log")

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
        "json": {  # The formatter name
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",  # The class to instantiate!
            # Json is more complex, but easier to read, display all attributes!
            "format": """
                   asctime: %(asctime)s
                   created: %(created)f
                   filename: %(filename)s
                   funcName: %(funcName)s
                   levelname: %(levelname)s
                   levelno: %(levelno)s
                   lineno: %(lineno)d
                   message: %(message)s
                   module: %(module)s
                   msec: %(msecs)d
                   name: %(name)s
                   pathname: %(pathname)s
                   process: %(process)d
                   processName: %(processName)s
                   relativeCreated: %(relativeCreated)d
                   thread: %(thread)d
                   threadName: %(threadName)s
                   exc_info: %(exc_info)s
               """,
            "datefmt": "%Y-%m-%d %H:%M:%S",  # How to display dates
        },
    },
    'handlers' : {
        'default' : {
            'level' : 'INFO',
            'formatter' : 'standard',
            'class' : 'logging.StreamHandler',

        },
        "file":{
            "formatter":"json",
            "class":"logging.FileHandler",
            "level":"INFO",
            "filename":f"{log_file}",
            'mode' : 'a',
        }
    },

}

DB_CONN = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"