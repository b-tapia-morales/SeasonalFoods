import uuid
from enum import Enum
from typing import Optional, List

from bson import ObjectId
from pydantic import BaseModel, Field
from datetime import datetime


class Food(BaseModel):
    product_name: str
    group: str


class History(BaseModel):
    date: datetime
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
    date: datetime
    mean_price: float

