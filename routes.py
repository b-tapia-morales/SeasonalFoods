from datetime import datetime, timezone, date, timedelta

from fastapi import APIRouter, Body, Request, Response, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from typing import List, Annotated

import models
import pipeline_utils
from models import Food, FoodDateAndPrice, FoodSeries, HarvestFoods, FoodPricesInRegion
import enums

router = APIRouter()


@router.get("/", response_description="Get all foods", response_model=List[Food])
def get_foods(request: Request):
    return request.app.database["foods"].find()


@router.get("/foods_search/year/{year_val}/",
            response_description="Food list by specified parameters.",
            response_model=List[Food])
def advanced_food_search(request: Request,
                         year_val: int,
                         region_id: Annotated[int | None, Query(alias='region')] = None,
                         group_id: Annotated[int | None, Query(alias='category')] = None,
                         week_from: Annotated[int | None, Query(alias="week_gte")] = None,
                         week_to: Annotated[int | None, Query(alias="week_lte")] = None,
                         quality_val: Annotated[int | None, Query(alias="quality")] = None,
                         store_type_id: Annotated[int | None, Query(alias="store")] = None,
                         in_season: Annotated[bool | None, Query(alias='in_season')] = None):
    pipeline = pipeline_utils.generate_history_pipeline(year_val=year_val,
                                                        region_id=region_id,
                                                        quality_val=quality_val,
                                                        store_id=store_type_id,
                                                        week_from=week_from,
                                                        week_to=week_to)
    pipeline.extend([
        {
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
        }
    ])
    if group_id is not None:
        pipeline.append(
            {
                '$match': {
                    'food.group': enums.category_dict[group_id].value
                }
            })
    pipeline.extend([
        {
            '$group': {
                '_id': {
                    'name': '$food.product_name',
                    'group': '$food.group',
                    'region': '$region',
                    'quality': '$quality',
                    'point_type': '$point_type',
                    'week': '$week',
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
                    'region': '$_id.region',
                    'quality': '$_id.quality',
                    'point_type': '$_id.point_type',
                    'category': '$_id.group'
                },
                'series': {
                    '$push': {
                        'week': '$_id.week',
                        'date': '$_id.date',
                        'mean_price': '$mean_price',
                    }
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'name': '$_id.name',
                'category': '$_id.category',
                'quality': '$_id.quality',
                'point_type': '$_id.point_type',
                'region': '$_id.region',
                'price': {
                    '$avg': '$series.mean_price'
                }
            }
        }
    ])

    if region_id is not None and (in_season is not None and in_season is True):
        region = enums.region_dict[region_id].value
        zone = enums.region_zone_dict[region]
        current_month = datetime.now().month
        pipeline.extend([
            {
                '$lookup': {
                    'from': 'harvest',
                    'localField': 'name',
                    'foreignField': 'ingredient_id',
                    'as': 'harvest'
                }
            }, {
                '$unwind': {
                    'path': '$harvest',
                    'preserveNullAndEmptyArrays': False
                }
            }, {
                '$match': {
                    'harvest.zone': zone,
                    'harvest.harvest_months': current_month
                }
            }, {
                '$project': {
                    'name': '$name',
                    'category': '$category',
                    'price': '$price'
                }
            }
        ])

    result = request.app.database['history'].aggregate(pipeline)
    if result is not None:
        result = list(result)
        return result
    raise HTTPException(status_code=404)


@router.get("/product/{product_name}/quality/{quality_val}/region/{region_id}",
            response_description="Product's price history from the last 4 weeks.",
            response_model=List[FoodSeries])
def get_food_history_last_weeks(request: Request,
                                region_id: int,
                                product_name: str,
                                quality_val: int):
    pipeline = pipeline_utils.generate_history_pipeline(year_val=datetime.now().year,
                                                        region_id=region_id,
                                                        quality_val=quality_val,
                                                        store_id=None,
                                                        week_from=None,
                                                        week_to=None)

    pipeline.extend([
        {
            '$lookup': {
                'from': 'foods',
                'localField': 'food_id',
                'foreignField': '_id',
                'as': 'food'
            }
        }, {
            '$match': {
                'food.product_name': product_name
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
                    'category': '$food.group',
                    'region': '$region',
                    'point_type': '$point_type',
                    'quality': '$quality',
                    'week': '$week',
                    'date': '$date'
                },
                'min_price': {
                    '$min': '$min_price'
                },
                'mean_price': {
                    '$avg': '$mean_price'
                },
                'max_price': {
                    '$max': '$max_price'
                }
            }
        }, {
            '$group': {
                '_id': {
                    'name': '$_id.name',
                    'category': '$_id.group',
                    'region': '$_id.region',
                    'point_type': '$_id.point_type',
                    'quality': '$_id.quality'
                },
                'series': {
                    '$push': {
                        'week': '$_id.week',
                        'date': '$_id.date',
                        'min_price': '$min_price',
                        'mean_price': '$mean_price',
                        'max_price': '$max_price'
                    }
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'name': '$_id.name',
                'category': '$_id.group',
                'region': '$_id.region',
                'point_type': '$_id.point_type',
                'quality': '$_id.quality',
                'history': '$series'
            }
        }
    ])
    print(pipeline)
    result = request.app.database['history'].aggregate(pipeline)

    if result is not None:
        result = list(result)
        for r in result:
            r['history'] = sorted(r['history'], key=lambda x: x['week'], reverse=True)
        return result
    raise HTTPException(status_code=404)


@router.get(
    "/product/{product_name}/quality/{quality_val}",
    response_description="---.",
    response_model=List[FoodPricesInRegion])
def testtt(request: Request,
           product_name: str,
           quality_val: int,
           week_from: Annotated[int | None, Query(alias="week_gte")] = None,
           week_to: Annotated[int | None, Query(alias="week_lte")] = None,
           ):
    pipeline = pipeline_utils.generate_history_pipeline(year_val=datetime.now().year,
                                                        region_id=None,
                                                        quality_val=quality_val,
                                                        store_id=None,
                                                        week_from=week_from,
                                                        week_to=week_to)
    pipeline.extend([
        {
            '$lookup': {
                'from': 'foods',
                'localField': 'food_id',
                'foreignField': '_id',
                'as': 'food'
            }
        }, {
            '$match': {
                'food.product_name': product_name
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
                    'category': '$food.group',
                    'region': '$region',
                    'point_type': '$point_type',
                    'quality': '$quality',
                    'week': '$week',
                    'date': '$date'
                },
                'min_price': {
                    '$min': '$min_price'
                },
                'mean_price': {
                    '$avg': '$mean_price'
                },
                'max_price': {
                    '$max': '$max_price'
                }
            }
        }, {
            '$group': {
                '_id': {
                    'name': '$_id.name',
                    'category': '$_id.group',
                    'region': '$_id.region',
                    'quality': '$_id.quality'
                },
                'series': {
                    '$push': {
                        'week': '$_id.week',
                        'date': '$_id.date',
                        'min_price': '$min_price',
                        'mean_price': '$mean_price',
                        'max_price': '$max_price'
                    }
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'region': '$_id.region',
                'quality': '$_id.quality',
                'history': '$series'
            }
        }
    ])
    result = request.app.database['history'].aggregate(pipeline)

    if result is not None:
        result = list(result)
        for r in result:
            r['history'] = sorted(r['history'], key=lambda x: x['week'], reverse=True)
        return result
    raise HTTPException(status_code=404)


@router.get("/year/{year_val}/product/{product_name}/",
            response_description="Product's price history from the last 4 weeks.",
            response_model=List[FoodDateAndPrice])
def get_food_history(request: Request,
                     year_val: int,
                     product_name: str,
                     region_id: Annotated[int | None, Query(alias='region')] = None,
                     week_from: Annotated[int | None, Query(alias="week_gte")] = None,
                     week_to: Annotated[int | None, Query(alias="week_lte")] = None,
                     quality_val: Annotated[int | None, Query(alias="quality")] = None,
                     store_type_id: Annotated[int | None, Query(alias="store")] = None):
    pipeline = pipeline_utils.generate_history_pipeline(year_val=year_val,
                                                        region_id=region_id,
                                                        quality_val=quality_val,
                                                        store_id=store_type_id,
                                                        week_from=week_from,
                                                        week_to=week_to)
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
                'week': '$week',
                'date': '$date'
            },
            'mean_price': {
                '$avg': '$mean_price'
            },
            'min_price': {
                '$min': '$min_price'
            },
            'max_price': {
                '$max': '$max_price'
            },
        }
    }, {
        '$project': {
            '_id': 0,
            'week': '$_id.week',
            'date': '$_id.date',
            'mean_price': '$mean_price',
            'min_price': '$min_price',
            'max_price': '$max_price'
        }
    }])

    result = request.app.database['history'].aggregate(pipeline)
    if result is not None:
        return list(result)
    raise HTTPException(status_code=404)


@router.get(
    "/seasonal/month/{month_val}/region/{region_id}",
    response_description="Foods that are in season.",
    response_model=List[FoodSeries])
def get_foods_in_season(request: Request,
                        month_val: int,
                        region_id: int):
    current_date = datetime.today()
    date_lower = datetime(current_date.year, month_val, 1, 0, 0, 0)
    date_upper = datetime(current_date.year, month_val + 1, 1, 0, 0, 0) - timedelta(days=1)
    region = enums.region_dict[region_id].value
    zone = enums.region_zone_dict[region]
    pipeline = [
        {
            '$match': {
                'date': {
                    '$gte': datetime(2023, 10, 1, 0, 0, 0, tzinfo=timezone.utc),
                    '$lte': datetime(2023, 10, 31, 0, 0, 0, tzinfo=timezone.utc)
                }
            }
        }, {
            '$match': {
                'region': region
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
                'min_price': {
                    '$min': '$min_price'
                },
                'mean_price': {
                    '$avg': '$mean_price'
                },
                'max_price': {
                    '$max': '$max_price'
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
                        'min_price': '$min_price',
                        'mean_price': '$mean_price',
                        'max_price': '$max_price'
                    }
                }
            }
        }, {
            '$lookup': {
                'from': 'harvest',
                'localField': '_id.name',
                'foreignField': 'ingredient_id',
                'as': 'harvest'
            }
        }, {
            '$unwind': {
                'path': '$harvest',
                'preserveNullAndEmptyArrays': False
            }
        }, {
            '$match': {
                'harvest.zone': zone,
                'harvest.harvest_months': month_val
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
            item['series'] = sorted(item['series'], key=lambda x: x['week'], reverse=True)
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

