from http import HTTPStatus
import asyncio

import aio_pika
import uvicorn
from cache_func import set_data, set_data_long,get_data
from cache_func import get_data
from fastapi import FastAPI, Depends, HTTPException, APIRouter
import json
from starlette import status

app = FastAPI()

basket_router= APIRouter(prefix='/basket', tags=['basket'])

@basket_router.get('/{uuid}')
async def get_all_basket(uuid: str):
    try:
        result = get_data(f"basket:{uuid}")
        json_dict = json.loads(result)
        return json_dict
    except Exception as e:
        return {'error': str(e)}

@basket_router.put('/plus/{uuid}/{product_id}')
async def plus_count_basket(uuid: str, product_id: int):
    result = get_data(f"basket:{uuid}")
    if result:
        json_dict = json.loads(result)
        if str(product_id) in json_dict:
            json_dict[str(product_id)]['count'] += 1
            json_dict = json.dumps(json_dict, default=str)
            set_data_long(f"basket:{uuid}", json_dict)
            final = get_data(f"basket:{uuid}")
            final = json.loads(final)
            return {'status': 'ok', "result": final}

@basket_router.put('/minus/{uuid}/{product_id}')
async def minus_count_basket(uuid: str, product_id: int):
    try:
        result = get_data(f"basket:{uuid}")
        if result:
            json_dict = json.loads(result)
            if str(product_id) in json_dict:
                if json_dict[str(product_id)]['count'] == 1:
                    json_dict.pop(str(product_id))
                    json_dict = json.dumps(json_dict, default=str)
                    set_data_long(f"basket:{uuid}", json_dict)
                    final = get_data(f"basket:{uuid}")
                    final = json.loads(final)
                    return {'status': 'ok', "result": final}
                if json_dict[str(product_id)]['count'] > 1:
                    json_dict[str(product_id)]['count'] -= 1
                    json_dict = json.dumps(json_dict, default=str)
                    set_data_long(f"basket:{uuid}", json_dict)
                    final = get_data(f"basket:{uuid}")
                    final = json.loads(final)
                    return {'status': 'ok', "result":  final}

        return {'status': 'empty of not found'}
    except Exception as e:
        return {'error': str(e)}

@basket_router.delete("/delete/{uuid}/{product_id}")
async def delete_products(uuid: str, product_id: int):
        result = get_data(f"basket:{uuid}")
        if result:
            json_dict = json.loads(result)
            if str(product_id) in json_dict:
                json_dict.pop(str(product_id))
                json_dict = json.dumps(json_dict, default=str)
                set_data_long(f"basket:{uuid}", json_dict)
                final = get_data(f"basket:{uuid}")
                final = json.loads(final)
                return {'status': 'ok', "result":  final}



def basket_work(body):
    basket_dict = json.loads(body.replace("'", '"'))
    basket = get_data(f"basket:{basket_dict['uuid']}")
    if not basket:
        uuid = basket_dict['uuid']
        data = {
            basket_dict['product_id']: {
                'name': basket_dict['name'],
                'price': basket_dict['price'],
                'category': basket_dict['category'],
                'count': 1,
                'unit_count': str(str(basket_dict['count']) + " " + str(basket_dict['unit_name']))
            }
        }
        new_data = json.dumps(data, default=str)
        set_data_long(f"basket:{uuid}", new_data)
    else:
        data = json.loads(basket)
        id = basket_dict['product_id']
        if str(id) in data:
            data[str(id)]['count'] += 1
            json_dict = json.dumps(data, default=str)
            set_data_long(f"basket:{basket_dict['uuid']}", json_dict)
        else:
            data.update({
                basket_dict['product_id']: {
                    'name': basket_dict['name'],
                    'price': basket_dict['price'],
                    'category': basket_dict['category'],
                    'count': 1,
                    'unit_count': str(str(basket_dict['count']) + " " + str(basket_dict['unit_name']))
                }
            })
            json_dict = json.dumps(data)
            set_data_long(f"basket:{basket_dict['uuid']}", json_dict)
    basket = get_data(f"basket:{basket_dict['uuid']}")
    data = json.loads(basket)
    print(data)

async def consuming():
        connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/")

        queue_name = 'hello'

        async with connection:
            channel = await connection.channel()

            queue = await channel.declare_queue(queue_name)
            print("[*] Waiting for messages. To Exit press Ctrl+C")

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        basket_work(message.body.decode('utf-8'))

app.include_router(basket_router)

async def start_fastapi():
    config = uvicorn.Config(app, host="0.0.0.0", port=8002, log_level="info", root_path="/bask")
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await asyncio.gather(
        consuming(),
        start_fastapi()
    )

if __name__ == "__main__":
    asyncio.run(main())