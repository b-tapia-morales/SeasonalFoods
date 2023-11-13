from datetime import datetime, timezone, date, timedelta

from fastapi import APIRouter, Body, Request, Response, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from typing import List, Annotated

import models
from models import Food, FoodDateAndPrice, SeasonalFoodSeries
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


@router.get("/product/{product_name}/quality/{quality_val}/region/{user_region}",
            response_description="get food's history",
            response_model=List[FoodDateAndPrice])
def get_food_history_time_series_last_weeks(request: Request,
                                            user_region: int,
                                            product_name: str,
                                            quality_val: int):
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
        }
    ]
    current_date = datetime.today()
    pipeline.append({
        '$match': {
            'price.date': {
                '$gte': (current_date - timedelta(weeks=4)).replace(
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0
                )
            }, 'price.quality': enums.quality_dict.get(quality_val)
        }
    })

    pipeline.append({
        '$sort': {
            'price.date': -1
        }
    })

    pipeline.append({
        '$project': {
            'date': '$price.date',
            'mean_price': '$price.mean_price'
        }
    })

    print(pipeline)
    result = request.app.database['foods'].aggregate(pipeline)

    if result is not None:
        return list(result)
    raise HTTPException(status_code=404)


@router.get(
    "/product/{product_name}/quality/{quality_val}/region/{user_region}/store_type/{store_type_id}/year/{year_val}/week",
    response_description="advanced food search",
    response_model=List[FoodDateAndPrice])
def get_food_history_time_series_week_range(request: Request,
                                            product_name: str,
                                            quality_val: int,
                                            user_region: int,
                                            store_type_id: int,
                                            year_val: int,
                                            week_from: Annotated[int, Query(alias="gte")],
                                            week_to: Annotated[int, Query(alias="lte")]):
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
                'price.region': enums.region_dict[user_region].value,
                'price.quality': enums.quality_dict[quality_val],
                'price.point_type': enums.point_dict[store_type_id].value
            }
        }
    ]
    dt_lower = date.fromisocalendar(year_val, week_from, 1)
    dt_upper = date.fromisocalendar(year_val, week_to, 1)
    pipeline.append({
        '$match': {
            'price.date': {
                '$gte': datetime.combine(dt_lower, datetime.min.time()),
                '$lte': datetime.combine(dt_upper, datetime.min.time())
            }
        }
    })

    pipeline.append({
        '$sort': {
            'price.date': -1
        }
    })

    pipeline.append({
        '$project': {
            'date': '$price.date',
            'mean_price': '$price.mean_price'
        }
    })

    print(pipeline)
    result = request.app.database['foods'].aggregate(pipeline)

    if result is not None:
        return list(result)
    raise HTTPException(status_code=404)


@router.get(
    "/product/{product_name}/quality/{quality_val}/region/{user_region}/store_type/{store_type_id}/date",
    response_description="advanced food search",
    response_model=List[FoodDateAndPrice])
def get_food_history_time_series_date_range(request: Request,
                                            product_name: str,
                                            quality_val: int,
                                            user_region: int,
                                            store_type_id: int,
                                            date_from: Annotated[str, Query(alias="gte")],
                                            date_to: Annotated[str, Query(alias="lte")]):
    pipeline = [{
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
            'price.region': enums.region_dict[user_region].value,
            'price.quality': enums.quality_dict.get(quality_val),
            'price.point_type': enums.point_dict[store_type_id].value
        }
    }, {
        '$match': {
            'price.date': {
                '$gte': datetime.strptime(date_from, '%Y-%m-%d'),
                '$lte': datetime.strptime(date_to, '%Y-%m-%d')
            }
        }
    }, {
        '$sort': {
            'price.date': -1
        }
    }, {
        '$project': {
            'date': '$price.date',
            'mean_price': '$price.mean_price'
        }
    }]

    print(pipeline)
    result = request.app.database['foods'].aggregate(pipeline)

    if result is not None:
        return list(result)
    raise HTTPException(status_code=404)


# slow ahh pipeline do not use this for now
"""
@router.get(
    "/seasonal/month/{month_val}/region/{region_id}",
    response_description="advanced food search",
    response_model=List[SeasonalFoodSeries])
def get_seasonal_foods(request: Request,
                       month_val: int,
                       region_id: int):
    current_date = datetime.today()
    date_lower = datetime(current_date.year, month_val, 1, 0, 0, 0, tzinfo=timezone.utc),
    date_upper = datetime(current_date.year, month_val + 1, 1, 0, 0, 0, tzinfo=timezone.utc) - timedelta(days=1)

    pipeline = [
        {
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
                'price.date': {
                    '$gte': date_lower,
                    '$lte': date_upper
                }
            }
        }, {
            '$match': {
                'price.region': enums.region_dict[region_id].value
            }
        }, {
            '$group': {
                '_id': {
                    'product_name': '$product_name',
                    'group': '$group'
                },
                'prices': {
                    '$push': {
                        'date': {
                            '$week': '$price.date'
                        },
                        'mean_price': '$price.mean_price'
                    }
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'name': '$_id.product_name',
                'category': '$_id.group',
                'series': '$prices'
            }
        }
    ]
    print(pipeline)
    result = request.app.database['foods'].aggregate(pipeline)

    if result is not None:
        return list(result)
    raise HTTPException(status_code=404)
"""