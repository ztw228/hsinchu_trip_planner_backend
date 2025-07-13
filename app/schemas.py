from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field

# -------- 請求 --------
class PlanRequest(BaseModel):
    areas: List[str]
    start_date: date
    end_date: date
    indoor_outdoor: str                # indoor / outdoor / mixed
    budget_hotel: int                  # 每晚 or 總價，先簡單比較
    budget_play: int
    categories: List[str]              # play / photo / food
    spot_count: int

# -------- 資料庫 --------
class Spot(BaseModel):
    id: str
    name: str
    area: str
    category: str
    indoor: bool
    open_days: str
    open_time: str
    close_time: str
    address: str
    ticket: int = 0

class Hotel(BaseModel):
    id: str
    name: str
    address: str
    price: int
    area: str
    # lat/lng 可有可無
    lat: Optional[float] = None
    lng: Optional[float] = None

# -------- 回傳 --------
class PlanResponse(BaseModel):
    id: Optional[str] = None
    hotel: Hotel
    days: List[List[Spot]] = Field(default_factory=list)
    suggestions: List[Spot] = Field(default_factory=list)
