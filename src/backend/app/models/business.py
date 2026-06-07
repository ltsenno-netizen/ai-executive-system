from typing import List
from pydantic import BaseModel

class BusinessRevenue(BaseModel):
    source: str
    amount: float
    ratio: float

class BusinessCost(BaseModel):
    category: str
    amount: float
    ratio: float

class BusinessPL(BaseModel):
    total_revenue: float
    total_cost: float
    profit: float
    profit_margin: float
    revenues: List[BusinessRevenue]
    costs: List[BusinessCost]

class BusinessModel(BaseModel):
    name: str
    fiscal_year: int
    pl: BusinessPL
