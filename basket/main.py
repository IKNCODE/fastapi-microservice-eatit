from config import channel, connection
from cache_func import set_data_long, get_data
import json
queue_name = 'hello'

# Функция, которая будет вызвана при получении сообщения
def callback(ch, method, properties, body):
    set_data_long(int(body), 1)
    lst = []
    json.dumps(lst.append({int(body) : "1" }))
    print(f"Received: '{int(body)}'")

# Подписка на очередь и установка обработчика сообщений
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=True  # Автоматическое подтверждение обработки сообщений
)

print('Waiting for messages. To exit, press Ctrl+C')
channel.start_consuming()

# Закрытие соединения
connection.close()