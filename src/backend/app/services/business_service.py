import json
import os
from typing import Optional
from ..models.business import BusinessModel, BusinessPL, BusinessRevenue, BusinessCost

class BusinessService:
    """事業モデルの読み込みとPL分析サービス"""

    def __init__(self):
        self.data_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/samples')
        )
        self.business_file = os.path.join(self.data_path, 'business_horipro.json')

    def load_business_model(self) -> BusinessModel:
        if not os.path.exists(self.business_file):
            raise FileNotFoundError(f"Business data not found: {self.business_file}")

        with open(self.business_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        revenue_items = [BusinessRevenue(**item) for item in data['pl'].get('revenues', [])]
        cost_items = [BusinessCost(**item) for item in data['pl'].get('costs', [])]

        pl = BusinessPL(
            total_revenue=data['pl'].get('total_revenue', 0.0),
            total_cost=data['pl'].get('total_cost', 0.0),
            profit=data['pl'].get('profit', 0.0),
            profit_margin=data['pl'].get('profit_margin', 0.0),
            revenues=revenue_items,
            costs=cost_items
        )

        # 必要ならPLを自動計算する
        if pl.profit == 0.0:
            pl.profit = self.calculate_profit(pl)
        if pl.profit_margin == 0.0:
            pl.profit_margin = self.calculate_profit_margin(pl)

        return BusinessModel(
            name=data.get('name', ''),
            fiscal_year=data.get('fiscal_year', 0),
            pl=pl
        )

    def calculate_profit(self, pl: BusinessPL) -> float:
        return round(pl.total_revenue - pl.total_cost, 2)

    def calculate_profit_margin(self, pl: BusinessPL) -> float:
        if pl.total_revenue == 0:
            return 0.0
        return round((pl.profit / pl.total_revenue) * 100, 1)
