import uuid
from enum import Enum
from typing import Optional, List

from bson import ObjectId
from pydantic import BaseModel, Field
from datetime import datetime, date


class Food(BaseModel):
    name: str
    category: str
    price: float


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
    min_price: int
    max_price: int


class FoodSummarized(BaseModel):
    product_name: str
    group: str
    region: str
    price: float
    point_type: str
    date: datetime


class FoodSeries(BaseModel):
    name: str
    region: str
    point_type: str
    quality: str
    history: List[FoodDateAndPrice]


class FoodPricesInRegion(BaseModel):
    region: str
    quality: str
    history: List[FoodDateAndPrice]
