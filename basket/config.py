import pika
import redis

# Параметры подключения
connection_params = pika.ConnectionParameters(
    host='localhost',  # Замените на адрес вашего RabbitMQ сервера
    port=5672,          # Порт по умолчанию для RabbitMQ
    virtual_host='/',   # Виртуальный хост (обычно '/')
)

# Установка соединения
connection = pika.BlockingConnection(connection_params)

# Создание канала
channel = connection.channel()


r = redis.Redis(host='localhost', port=6379, db=0)

TTL = 200
LONG_TTL = 60 * 60 * 24 * 365