from datetime import datetime, timezone, date

from fastapi import APIRouter, Body, Request, Response, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from typing import List, Annotated

import models
from models import Food, History, FoodDateAndPrice
import enums

router = APIRouter()


@router.get("/", response_description="Get all foods", response_model=List[Food])
def get_foods(request: Request):
    return request.app.database["foods"].find()


@router.get("/{product_name}", response_description="Get a certain food", response_model=Food)
def get_food(request: Request, product_name: str):
    item = request.app.database["foods"].find_one({"product_name": product_name})
    print(item)
    if item is not None:
        return item
    raise HTTPException(status_code=404)


@router.get("/history/region/{user_region}/product/{product_name}/date",
            response_description="get food's history",
            response_model=List[FoodDateAndPrice])
def get_food_history(request: Request, user_region: int,
                     product_name: str,
                     date_from: Annotated[str, Query(alias="gte")],
                     date_to: Annotated[str, Query(alias="lte")]):
    pipeline = [
        {
            '$match': {
                'product_name': product_name
            }
        }, {
            '$lookup': {
                'from': 'history',
                'localField': '_id',
                'foreignField': 'food_id',
                'as': 'price'
            }
        }, {
            '$unwind': {
                'path': '$price',
                'preserveNullAndEmptyArrays': False
            }
        }, {
            '$match': {
                'price.region': enums.region_dict[user_region].value
            }
        }, {
            '$project': {
                'date': '$price.date',
                'mean_price': '$price.mean_price'
            }
        }, {
            '$sort': {
                'date': -1
            }
        }
    ]

    if date_from is not None:
        pipeline.append({
            '$match': {
                'date': {
                    '$gte': datetime.strptime(date_from, '%Y-%m-%d'),
                }
            }
        })

    if date_to is not None:
        pipeline.append({
            '$match': {
                'date': {
                    '$lte': datetime.strptime(date_to, '%Y-%m-%d')
                }
            }
        })
    print(pipeline)
    result = request.app.database['foods'].aggregate(pipeline)

    if result is not None:
        return list(result)
    raise HTTPException(status_code=404)


"""@router.get("/history/region/{user_region}/product/{product_name}/",
            response_description="get food's history",
            response_model=List[FoodDateAndPrice])
def get_food_history_current_month(request: Request, user_region: int, product_name: str):
"""