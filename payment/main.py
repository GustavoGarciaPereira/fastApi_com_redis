from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request
import requests
import os
import time
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

redis = get_redis_connection(
    host=os.environ.get("host"),
    port=os.environ.get("port"),
    password=os.environ.get("password"),
    decode_responses=os.environ.get("decode_responses"),
)


class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str

    class Meta:
        database = redis


@app.get("/orders/{pk}")
def get(pk: str):
    order = Order.get(pk)
    return order


@app.post("/orders")
async def create(request: Request, backward_task: BackgroundTasks):
    body = await request.json()

    req = requests.get('http://127.0.0.1:8000/products/%s' % body['id'])

    product = req.json()
    order = Order(
        product_id=body['id'],
        price=product['price'],
        fee=0.2 * product['price'],
        total=1.2 * product['price'],
        quantity=product['quantity'],
        status='pending'
    )
    order.save()
    backward_task.add_task(order_complete, order)
    return order


def order_complete(order: Order):
    time.sleep(5)
    order.status = 'completed'
    order.save()
