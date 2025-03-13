from typing import Optional

from pydantic import BaseModel, Field
from datetime import date

class NewRollSchema(BaseModel):
    length: float = Field(gt=0)
    weight: float = Field(gt=0)

class RollsSchema(BaseModel):
    id: int
    length: float = Field(gt=0)
    weight: float = Field(gt=0)
    date_create: date | None
    date_delete: date | None

class FilterRollsSchema(BaseModel):
    id_more: Optional[int] = None
    id_less: Optional[int] = None
    length_more: Optional[float] = None
    length_less: Optional[float] = None
    weight_more: Optional[float] = None
    weight_less: Optional[float] = None
    date_create_more: Optional[date] = None
    date_create_less: Optional[date] = None
    date_delete_more: Optional[date] = None
    date_delete_less: Optional[date] = None
    date_delete_is_null: Optional[bool] = None

class SelectRollsSchema(BaseModel):
    date_more: date
    date_less: date

class SelectSchema(BaseModel):
    count_add_rolls: int
    count_delete_rolls: int
    avg_lenght: float
    avg_weight: float
    max_lenght: float
    min_lenght: float
    max_weight: float
    min_weight: float
    sum_weight: float
    max_day_delay: int | None
    min_day_delay: int | None
    max_count_day: date
    min_count_day: date
    max_weight_day: date
    min_weigth_day: date


