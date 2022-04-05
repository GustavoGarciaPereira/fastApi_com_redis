from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
import os
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


class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis


@app.get("/products")
def all():
    return [format(pk) for pk in Product.all_pks()]


def format(pk: str):
    product = Product.get(pk)
    return {
        "id": product.pk,
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity,
    }

 
@app.post("/products")
def create(product: Product):
    product.save()
    return product


@app.get("/products/{pk}")
def get(pk: str):
    return format(pk)


@app.delete("/products/{pk}")
def delete(pk: str):
    product = Product.delete(pk)
    return product
