from datetime import datetime, timezone, date, timedelta

from fastapi import APIRouter, Body, Request, Response, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from typing import List, Annotated

import models
from models import Food, FoodDateAndPrice, SeasonalFoodSeries, HarvestFoods, MeanPriceInRegion
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


@router.get("/product/{product_name}/quality/{quality_val}/region/{region_id}",
            response_description="Product's price history from the last 4 weeks.",
            response_model=List[FoodDateAndPrice])
def get_food_history_last_weeks(request: Request,
                                region_id: int,
                                product_name: str,
                                quality_val: int):
    curr_date = datetime.today()
    week_num = curr_date.isocalendar()[1]

    pipeline = [
        {
            '$match': {
                'week': {
                    '$gte': week_num - 4
                }
            }
        }, {
            '$match': {
                'region': enums.region_dict[region_id].value,
                'quality': enums.quality_dict[quality_val],
            }
        }, {
            '$lookup': {
                'from': 'foods',
                'localField': 'food_id',
                'foreignField': '_id',
                'as': 'food'
            }
        }, {
            '$unwind': {
                'path': '$food',
                'preserveNullAndEmptyArrays': False
            }
        }, {
            '$match': {
                'food.product_name': product_name
            }
        }, {
            '$project': {
                'date': '$date',
                'week': '$week',
                'mean_price': '$mean_price',
            }
        }
    ]

    print(pipeline)
    result = request.app.database['history'].aggregate(pipeline)

    if result is not None:
        return list(result)
    raise HTTPException(status_code=404)


@router.get(
    "/product/{product_name}/quality/{quality_val}/region/{region_id}/store_type/{store_type_id}/year/{year_val}/week",
    response_description="Product's price history using weeks from a certain year.",
    response_model=List[FoodDateAndPrice])
def get_food_history_week_range(request: Request,
                                product_name: str,
                                quality_val: int,
                                region_id: int,
                                store_type_id: int,
                                year_val: int,
                                week_from: Annotated[int, Query(alias="gte")],
                                week_to: Annotated[int, Query(alias="lte")]):
    dt_lower = date.fromisocalendar(year_val, week_from, 1)
    dt_upper = date.fromisocalendar(year_val, week_to, 1)

    pipeline = [
        {
            '$match': {
                'date': {
                    '$gte': datetime.combine(dt_lower, datetime.min.time()),
                    '$lte': datetime.combine(dt_upper, datetime.min.time())
                }
            }
        }, {
            '$match': {
                'region': enums.region_dict[region_id].value,
                'quality': enums.quality_dict[quality_val],
                'point_type': enums.point_dict[store_type_id].value
            }
        }, {
            '$lookup': {
                'from': 'foods',
                'localField': 'food_id',
                'foreignField': '_id',
                'as': 'food'
            }
        }, {
            '$unwind': {
                'path': '$food',
                'preserveNullAndEmptyArrays': False
            }
        }, {
            '$match': {
                'food.product_name': product_name
            }
        }, {
            '$project': {
                'date': '$date',
                'week': '$week',
                'mean_price': '$mean_price',
            }
        }
    ]

    print(pipeline)
    result = request.app.database['history'].aggregate(pipeline)

    if result is not None:
        return list(result)
    raise HTTPException(status_code=404)


@router.get(
    "/product/{product_name}/quality/{quality_val}/region/{region_id}/store_type/{store_type_id}/date",
    response_description="Product's price history using dates.",
    response_model=List[FoodDateAndPrice])
def get_food_history_date_range(request: Request,
                                product_name: str,
                                quality_val: int,
                                region_id: int,
                                store_type_id: int,
                                date_from: Annotated[str, Query(alias="gte")],
                                date_to: Annotated[str, Query(alias="lte")]):
    pipeline = [
        {
            '$match': {
                'date': {
                    '$gte': datetime.strptime(date_from, '%Y-%m-%d'),
                    '$lte': datetime.strptime(date_to, '%Y-%m-%d')
                }
            }
        }, {
            '$match': {
                'region': enums.region_dict[region_id].value,
                'quality': enums.quality_dict[quality_val],
                'point_type': enums.point_dict[store_type_id].value
            }
        }, {
            '$lookup': {
                'from': 'foods',
                'localField': 'food_id',
                'foreignField': '_id',
                'as': 'food'
            }
        }, {
            '$unwind': {
                'path': '$food',
                'preserveNullAndEmptyArrays': False
            }
        }, {
            '$match': {
                'food.product_name': product_name
            }
        }, {
            '$project': {
                'date': '$date',
                'week': '$week',
                'mean_price': '$mean_price',
            }
        }
    ]

    print(pipeline)
    result = request.app.database['history'].aggregate(pipeline)

    if result is not None:
        return list(result)
    raise HTTPException(status_code=404)


@router.get(
    "/seasonal/month/{month_val}/region/{region_id}",
    response_description="Foods that are in season.",
    response_model=List[SeasonalFoodSeries])
def get_foods_in_season(request: Request,
                        month_val: int,
                        region_id: int):
    current_date = datetime.today()
    date_lower = datetime(current_date.year, month_val, 1, 0, 0, 0)
    date_upper = datetime(current_date.year, month_val + 1, 1, 0, 0, 0) - timedelta(days=1)

    pipeline = [
        {
            '$match': {
                'date': {
                    '$gte': date_lower,
                    '$lte': date_upper
                }
            }
        }, {
            '$match': {
                'region': enums.region_dict[region_id].value
            }
        }, {
            '$lookup': {
                'from': 'foods',
                'localField': 'food_id',
                'foreignField': '_id',
                'as': 'food'
            }
        }, {
            '$unwind': {
                'path': '$food',
                'preserveNullAndEmptyArrays': False
            }
        }, {
            '$group': {
                '_id': {
                    'name': '$food.product_name',
                    'group': '$food.group',
                    'week': {
                        '$week': '$date'
                    },
                    'date': '$date'
                },
                'mean_price': {
                    '$avg': '$mean_price'
                }
            }
        }, {
            '$group': {
                '_id': {
                    'name': '$_id.name',
                    'category': '$_id.group'
                },
                'series': {
                    '$push': {
                        'week': '$_id.week',
                        'date': '$_id.date',
                        'mean_price': '$mean_price'
                    }
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'name': '$_id.name',
                'category': '$_id.category',
                'series': '$series'
            }
        }
    ]
    print(pipeline)
    result = request.app.database['history'].aggregate(pipeline)

    if result is not None:
        result = list(result)
        for item in result:
            item['series'] = sorted(item['series'], key=lambda x: x['week'])
        return result
    raise HTTPException(status_code=404)


@router.get(
    "/seasonal/zone/{zone_id}/harvest_months",
    response_description="Foods in a certain zone and during harvest.",
    response_model=HarvestFoods)
def get_foods_in_zone(request: Request,
                      zone: enums.Zone,
                      harvest_months: int):
    pipeline = [
        {
            '$match': {
                'zone': zone.value
            }
        }, {
            '$lookup': {
                'from': 'foods',
                'localField': 'ingredient_id',
                'foreignField': 'product_name',
                'as': 'food'
            }
        }, {
            '$unwind': {
                'path': '$food',
                'preserveNullAndEmptyArrays': False
            }
        }, {
            '$match': {
                'harvest_months': harvest_months
            }
        }, {
            '$group': {
                '_id': None,
                'names': {
                    '$push': '$food.product_name'
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'foods': '$names'
            }
        }
    ]

    print(pipeline)
    result = request.app.database['harvest'].aggregate(pipeline)

    if result is not None:
        result = list(result)
        return result[0]
    raise HTTPException(status_code=404)


@router.get(
    "/product/{product_name}/year/{year_val}/",
    response_description="---.",
    response_model=List[MeanPriceInRegion])
def testtt(request: Request,
           product_name: str,
           year_val: int,
           week_from: Annotated[int | None, Query(alias="week_gte")] = None,
           week_to: Annotated[int | None, Query(alias="week_lte")] = None,
           quality_val: Annotated[int | None, Query(alias="quality")] = None,
           store_type_id: Annotated[int | None, Query(alias="store")] = None,
           ):
    curr_date = datetime.today()
    week_num = curr_date.isocalendar()[1]
    pipeline = []
    pipeline.append(
        {
            '$match': {
                'week': {
                    '$gte': week_num - 4
                },
                'year': year_val
            }
        } if week_from is None and week_to is None else {
            '$match': {
                'week': {
                    '$gte': week_from,
                    '$lte': week_to
                },
                'year': year_val
            }
        })
    if store_type_id is not None:
        pipeline.append(
            {
                '$match': {
                    'point_type': enums.point_dict[store_type_id].value,
                }
            })

    if quality_val is not None:
        pipeline.append(
            {
                '$match': {
                    'quality': enums.quality_dict[quality_val]
                }
            })

    pipeline.extend([{
        '$lookup': {
            'from': 'foods',
            'localField': 'food_id',
            'foreignField': '_id',
            'as': 'food'
        }
    }, {
        '$unwind': {
            'path': '$food',
            'preserveNullAndEmptyArrays': False
        }
    }, {
        '$match': {
            'food.product_name': product_name
        }
    }, {
        '$group': {
            '_id': {
                'region': '$region',
                'week': '$week',
                'date': '$date'
            },
            'mean_price': {
                '$avg': '$mean_price'
            }
        }
    }, {
        '$project': {
            '_id': 0,
            'region': '$_id.region',
            'week': '$_id.week',
            'date': '$_id.date',
            'mean_price': '$mean_price'
        }
    }])

    print(pipeline)
    result = request.app.database['history'].aggregate(pipeline)

    if result is not None:
        result = list(result)
        return result
    raise HTTPException(status_code=404)
