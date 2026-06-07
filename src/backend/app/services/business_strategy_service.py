import json
import os
from ..models.business_strategy import (
    BusinessStrategyModel,
    RevenueBreakdown,
    BusinessInsight,
    SensitivityAnalysis,
    StrategicPriority,
    BusinessStrategyDefinition,
)

class BusinessStrategyService:
    """戦略レイヤーとしての事業モデル読み込みサービス"""

    def __init__(self):
        self.data_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/samples')
        )
        self.strategy_file = os.path.join(self.data_path, 'business_strategy_horipro.json')
        self.definition_file = os.path.join(self.data_path, 'business_strategy_definition_horipro.json')

    def load_business_strategy(self) -> BusinessStrategyModel:
        if not os.path.exists(self.strategy_file):
            raise FileNotFoundError(f"Strategy data not found: {self.strategy_file}")

        with open(self.strategy_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return BusinessStrategyModel(**data)

    def load_business_strategy_definition(self) -> BusinessStrategyDefinition:
        if not os.path.exists(self.definition_file):
            raise FileNotFoundError(f"Strategy definition data not found: {self.definition_file}")

        with open(self.definition_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return BusinessStrategyDefinition(**data)

    def calculate_total_gross_profit(self, model: BusinessStrategyModel) -> float:
        total = sum(item.gross_profit for item in model.revenue_breakdown)
        return round(total, 3)
