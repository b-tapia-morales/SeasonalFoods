import uuid
from enum import Enum
from typing import Optional, List

from bson import ObjectId
from pydantic import BaseModel, Field
from datetime import datetime, date


class Food(BaseModel):
    product_name: str
    group: str


class HarvestFoods(BaseModel):
    foods: List[str]


class History(BaseModel):
    date: datetime
    week: int
    year: int
    region: str
    sector: str
    point_type: str
    variety: str
    quality: str
    unit: str
    min_price: int
    mean_price: float
    max_price: int


class FoodDateAndPrice(BaseModel):
    date: date
    week: int
    mean_price: float


class FoodWeekAndPrice(BaseModel):
    week: int
    mean_price: float


class FoodSummarized(BaseModel):
    product_name: str
    group: str
    region: str
    price: float
    point_type: str
    date: datetime


class SeasonalFoodSeries(BaseModel):
    name: str
    category: str
    series: List[FoodWeekAndPrice]
