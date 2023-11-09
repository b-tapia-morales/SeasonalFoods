from fastapi import FastAPI
import uvicorn
from dotenv import dotenv_values
from pymongo import MongoClient
from routes import router as food_router

config = dotenv_values(".env")

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient('localhost', 27017)
    app.database = app.mongodb_client[config["DB_NAME"]]


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


app.include_router(food_router, tags=["foods"], prefix="/foods")
