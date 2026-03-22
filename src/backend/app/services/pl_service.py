import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..models.development import (
    Business, Revenue, Cost, Expense, PLStatement, BusinessSimulation
)

class PLService:
    def __init__(self):
        self.businesses_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../data/samples/businesses.json'))
        self.revenue_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../data/samples/revenue.json'))
        self.cost_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../data/samples/cost.json'))
        self.expense_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../data/samples/expense.json'))

    def load_businesses(self) -> Dict[str, Business]:
        if not os.path.exists(self.businesses_path):
            return {}
        with open(self.businesses_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        businesses = {}
        for item in data:
            business = Business(**item)
            businesses[business.id] = business
        return businesses

    def save_businesses(self, businesses: Dict[str, Business]):
        data = [business.dict() for business in businesses.values()]
        os.makedirs(os.path.dirname(self.businesses_path), exist_ok=True)
        with open(self.businesses_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_revenue_data(self) -> Dict[str, Dict[str, Revenue]]:
        """business_id -> month -> Revenue"""
        if not os.path.exists(self.revenue_path):
            return {}
        with open(self.revenue_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        revenue_data = {}
        for item in data:
            business_id = item['business_id']
            month = item['month']
            if business_id not in revenue_data:
                revenue_data[business_id] = {}
            revenue_data[business_id][month] = Revenue(**item)
        return revenue_data

    def save_revenue_data(self, revenue_data: Dict[str, Dict[str, Revenue]]):
        data = []
        for business_id, months in revenue_data.items():
            for month, revenue in months.items():
                data.append(revenue.dict())
        os.makedirs(os.path.dirname(self.revenue_path), exist_ok=True)
        with open(self.revenue_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_cost_data(self) -> Dict[str, Dict[str, Cost]]:
        """business_id -> month -> Cost"""
        if not os.path.exists(self.cost_path):
            return {}
        with open(self.cost_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        cost_data = {}
        for item in data:
            business_id = item['business_id']
            month = item['month']
            if business_id not in cost_data:
                cost_data[business_id] = {}
            cost_data[business_id][month] = Cost(**item)
        return cost_data

    def save_cost_data(self, cost_data: Dict[str, Dict[str, Cost]]):
        data = []
        for business_id, months in cost_data.items():
            for month, cost in months.items():
                data.append(cost.dict())
        os.makedirs(os.path.dirname(self.cost_path), exist_ok=True)
        with open(self.cost_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_expense_data(self) -> Dict[str, Dict[str, Expense]]:
        """business_id -> month -> Expense"""
        if not os.path.exists(self.expense_path):
            return {}
        with open(self.expense_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        expense_data = {}
        for item in data:
            business_id = item['business_id']
            month = item['month']
            if business_id not in expense_data:
                expense_data[business_id] = {}
            expense_data[business_id][month] = Expense(**item)
        return expense_data

    def save_expense_data(self, expense_data: Dict[str, Dict[str, Expense]]):
        data = []
        for business_id, months in expense_data.items():
            for month, expense in months.items():
                data.append(expense.dict())
        os.makedirs(os.path.dirname(self.expense_path), exist_ok=True)
        with open(self.expense_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def generate_pl_statement(self, business_id: str, month: str) -> Optional[PLStatement]:
        """指定された事業・月のPLを生成"""
        businesses = self.load_businesses()
        if business_id not in businesses:
            return None

        business = businesses[business_id]
        revenue_data = self.load_revenue_data()
        cost_data = self.load_cost_data()
        expense_data = self.load_expense_data()

        # データ取得
        revenue = revenue_data.get(business_id, {}).get(month)
        cost = cost_data.get(business_id, {}).get(month)
        expense = expense_data.get(business_id, {}).get(month)

        if not revenue or not cost or not expense:
            return None

        # PL計算
        gross_profit = revenue.total_revenue - cost.total_direct_costs
        operating_profit = gross_profit - expense.total_expenses
        profit_margin = (operating_profit / revenue.total_revenue * 100) if revenue.total_revenue > 0 else 0

        # 損益分岐点計算（簡易版）
        break_even_point = self._calculate_break_even_point(revenue, cost, expense)

        # 分析
        analysis = self._analyze_pl(revenue, cost, expense, gross_profit, operating_profit)

        # 改善提案
        recommendations = self._generate_recommendations(revenue, cost, expense, operating_profit)

        pl_statement = PLStatement(
            business_id=business_id,
            business_name=business.name,
            month=month,
            revenue=revenue,
            cost=cost,
            expense=expense,
            gross_profit=gross_profit,
            operating_profit=operating_profit,
            profit_margin=profit_margin,
            break_even_point=break_even_point,
            status="黒字" if operating_profit > 0 else "赤字",
            analysis=analysis,
            recommendations=recommendations,
            created_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        return pl_statement

    def simulate_business_projection(self, business_id: str, months_ahead: int = 6,
                                   growth_rate: float = 0.0, cost_reduction: float = 0.0) -> Optional[BusinessSimulation]:
        """事業の将来予測シミュレーション"""
        businesses = self.load_businesses()
        if business_id not in businesses:
            return None

        business = businesses[business_id]

        # 最新のデータを取得
        current_month = datetime.now().strftime("%Y-%m")
        revenue_data = self.load_revenue_data()
        cost_data = self.load_cost_data()
        expense_data = self.load_expense_data()

        current_revenue = revenue_data.get(business_id, {}).get(current_month)
        current_cost = cost_data.get(business_id, {}).get(current_month)
        current_expense = expense_data.get(business_id, {}).get(current_month)

        if not current_revenue or not current_cost or not current_expense:
            return None

        # シミュレーション実行
        monthly_projections = []
        cumulative_profit = 0

        for i in range(1, months_ahead + 1):
            # 月次予測
            projected_revenue = current_revenue.total_revenue * (1 + growth_rate) ** i
            projected_cost = current_cost.total_direct_costs * (1 - cost_reduction)
            projected_expense = current_expense.total_expenses * (1 - cost_reduction * 0.5)

            projected_profit = projected_revenue - projected_cost - projected_expense
            cumulative_profit += projected_profit

            projection = {
                "month": i,
                "revenue": projected_revenue,
                "cost": projected_cost,
                "expense": projected_expense,
                "profit": projected_profit,
                "cumulative_profit": cumulative_profit
            }
            monthly_projections.append(projection)

        # 最終予測
        final_projection = {
            "total_profit": cumulative_profit,
            "average_monthly_profit": cumulative_profit / months_ahead,
            "profit_trend": "黒字" if cumulative_profit > 0 else "赤字",
            "break_even_month": self._calculate_break_even_month(monthly_projections)
        }

        # リスク分析
        risk_analysis = self._analyze_simulation_risks(growth_rate, cost_reduction, monthly_projections)

        simulation = BusinessSimulation(
            business_id=business_id,
            scenario_name=f"{months_ahead}ヶ月予測 (成長率: {growth_rate*100:.1f}%, コスト削減: {cost_reduction*100:.1f}%)",
            simulation_months=months_ahead,
            assumptions={
                "growth_rate": growth_rate,
                "cost_reduction": cost_reduction,
                "base_revenue": current_revenue.total_revenue,
                "base_cost": current_cost.total_direct_costs,
                "base_expense": current_expense.total_expenses
            },
            monthly_projections=monthly_projections,
            final_projection=final_projection,
            risk_analysis=risk_analysis,
            created_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        return simulation

    def get_business_summary(self) -> List[Dict[str, Any]]:
        """全事業のサマリーを取得"""
        businesses = self.load_businesses()
        revenue_data = self.load_revenue_data()

        summary = []
        for business_id, business in businesses.items():
            # 最新月のデータを取得
            business_revenue = revenue_data.get(business_id, {})
            if business_revenue:
                latest_month = max(business_revenue.keys())
                latest_revenue = business_revenue[latest_month]

                # PL生成を試行
                pl = self.generate_pl_statement(business_id, latest_month)
                if pl:
                    summary.append({
                        "business_id": business_id,
                        "business_name": business.name,
                        "month": latest_month,
                        "revenue": pl.revenue.total_revenue,
                        "profit": pl.operating_profit,
                        "profit_margin": pl.profit_margin,
                        "status": "黒字" if pl.operating_profit > 0 else "赤字"
                    })

        return summary

    def _calculate_break_even_point(self, revenue: Revenue, cost: Cost, expense: Expense) -> float:
        """損益分岐点を計算（簡易版）"""
        # 変動費率を仮定（売上の30%）
        variable_cost_ratio = 0.3
        fixed_costs = expense.total_expenses

        if revenue.total_revenue <= 0:
            return 0

        # 損益分岐点売上 = 固定費 / (1 - 変動費率)
        break_even_sales = fixed_costs / (1 - variable_cost_ratio)
        return break_even_sales

    def _analyze_pl(self, revenue: Revenue, cost: Cost, expense: Expense,
                   gross_profit: float, operating_profit: float) -> Dict[str, Any]:
        """PLを分析"""
        analysis = {
            "収益性分析": {},
            "コスト構造分析": {},
            "リスク評価": ""
        }

        # 収益性分析
        revenue_composition = {
            "商品売上": revenue.product_sales / revenue.total_revenue * 100 if revenue.total_revenue > 0 else 0,
            "サービス売上": revenue.service_sales / revenue.total_revenue * 100 if revenue.total_revenue > 0 else 0,
            "その他収入": revenue.other_revenue / revenue.total_revenue * 100 if revenue.total_revenue > 0 else 0
        }

        analysis["収益性分析"] = {
            "売上構成比": revenue_composition,
            "粗利益率": gross_profit / revenue.total_revenue * 100 if revenue.total_revenue > 0 else 0,
            "営業利益率": operating_profit / revenue.total_revenue * 100 if revenue.total_revenue > 0 else 0
        }

        # コスト構造分析
        cost_structure = {
            "直接費": cost.total_direct_costs / revenue.total_revenue * 100 if revenue.total_revenue > 0 else 0,
            "間接費": expense.total_expenses / revenue.total_revenue * 100 if revenue.total_revenue > 0 else 0
        }

        analysis["コスト構造分析"] = {
            "コスト構成比": cost_structure,
            "最大コスト項目": self._find_largest_expense(expense)
        }

        # リスク評価
        if operating_profit < 0:
            analysis["リスク評価"] = "赤字状態です。コスト削減または売上増加が必要です。"
        elif operating_profit / revenue.total_revenue < 0.05:
            analysis["リスク評価"] = "利益率が低めです。収益性改善を検討してください。"
        else:
            analysis["リスク評価"] = "健全な収益状態です。"

        return analysis

    def _generate_recommendations(self, revenue: Revenue, cost: Cost, expense: Expense,
                                operating_profit: float) -> List[str]:
        """改善提案を生成"""
        recommendations = []

        if operating_profit < 0:
            recommendations.append("赤字改善のため、以下の施策を検討してください：")
            recommendations.append("1. 売上増加施策：新規顧客開拓、既存顧客深耕")
            recommendations.append("2. コスト削減：無駄な経費の見直し、外注費の削減")
            recommendations.append("3. 価格改定：利益率の改善")

        # コスト構造の分析
        if expense.personnel_expenses > expense.total_expenses * 0.5:
            recommendations.append("人件費比率が高いため、業務効率化を検討してください")

        if expense.marketing_expenses < revenue.total_revenue * 0.05:
            recommendations.append("販促投資が不足している可能性があります")

        # 売上構成の分析
        if revenue.product_sales < revenue.total_revenue * 0.3:
            recommendations.append("商品売上の比率が低いため、主力商品の強化を検討してください")

        if not recommendations:
            recommendations.append("全体的に安定した収益構造です。成長投資を検討してください")

        return recommendations

    def _find_largest_expense(self, expense: Expense) -> str:
        """最大の経費項目を特定"""
        expense_items = {
            "人件費": expense.personnel_expenses,
            "家賃": expense.rent_expenses,
            "水道光熱費": expense.utilities,
            "販促費": expense.marketing_expenses,
            "旅費交通費": expense.travel_expenses,
            "通信費": expense.communication_expenses,
            "事務用品費": expense.office_supplies,
            "減価償却費": expense.depreciation,
            "その他経費": expense.other_expenses
        }

        max_item = max(expense_items.items(), key=lambda x: x[1])
        return f"{max_item[0]} ({max_item[1]:,.0f}円)"

    def _calculate_break_even_month(self, projections: List[Dict[str, Any]]) -> Optional[int]:
        """損益分岐に達する月を計算"""
        cumulative_profit = 0
        for i, projection in enumerate(projections, 1):
            cumulative_profit += projection["profit"]
            if cumulative_profit >= 0:
                return i
        return None

    def _analyze_simulation_risks(self, growth_rate: float, cost_reduction: float,
                                projections: List[Dict[str, Any]]) -> List[str]:
        """シミュレーションのリスク分析"""
        risks = []

        if growth_rate < 0:
            risks.append("売上成長率がマイナスです。市場環境の悪化リスクがあります")

        if cost_reduction > 0.2:
            risks.append("コスト削減率が20%を超えています。品質低下やモチベーション低下のリスクがあります")

        # 収益変動の分析
        profits = [p["profit"] for p in projections]
        if max(profits) - min(profits) > abs(sum(profits)) * 0.5:
            risks.append("収益変動が大きいです。安定した成長戦略が必要です")

        final_cumulative = projections[-1]["cumulative_profit"] if projections else 0
        if final_cumulative < 0:
            risks.append("シミュレーション期間終了時に累積赤字となります")

        if not risks:
            risks.append("大きなリスクは見られません。ただし、市場環境の変化に注意してください")

        return risks