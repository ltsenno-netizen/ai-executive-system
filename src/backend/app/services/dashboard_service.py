import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..models.development import (
    KPIMetric, KPIDashboard, DashboardReport
)
from .pl_service import PLService

class DashboardService:
    """事業別KPIダッシュボード生成エージェント"""
    
    def __init__(self):
        self.pl_service = PLService()
        self.kpi_history_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/samples/kpi_history.json')
        )
    
    def load_kpi_history(self) -> Dict[str, Dict[str, Any]]:
        """KPI履歴を読み込む（business_id -> month -> KPI data）"""
        if not os.path.exists(self.kpi_history_path):
            return {}
        with open(self.kpi_history_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_kpi_history(self, history: Dict[str, Dict[str, Any]]):
        """KPI履歴を保存"""
        os.makedirs(os.path.dirname(self.kpi_history_path), exist_ok=True)
        with open(self.kpi_history_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    
    def generate_dashboard(self, business_id: str, month: str) -> Optional[KPIDashboard]:
        """事業別KPIダッシュボードを生成"""
        businesses = self.pl_service.load_businesses()
        if business_id not in businesses:
            return None
        
        business = businesses[business_id]
        
        # PLステートメントを取得（財務KPI算出用）
        pl_statement = self.pl_service.generate_pl_statement(business_id, month)
        if not pl_statement:
            return None
        
        # KPI履歴を読み込み（前月比・YoY比較用）
        kpi_history = self.load_kpi_history()
        business_history = kpi_history.get(business_id, {})
        
        # 前月データを取得
        previous_month = self._get_previous_month(month)
        previous_pl = self.pl_service.generate_pl_statement(business_id, previous_month)
        
        # 各KPIを計算
        revenue_metrics = self._calculate_revenue_kpi(
            pl_statement, previous_pl, business_history.get(month, {})
        )
        
        profit_margin_metrics = self._calculate_margin_kpi(
            pl_statement, previous_pl
        )
        
        gross_profit_metrics = self._calculate_gross_profit_kpi(
            pl_statement, previous_pl
        )
        
        operating_profit_metrics = self._calculate_operating_profit_kpi(
            pl_statement, previous_pl
        )
        
        cost_ratio_metrics = self._calculate_cost_ratio_kpi(
            pl_statement, previous_pl
        )
        
        expense_ratio_metrics = self._calculate_expense_ratio_kpi(
            pl_statement, previous_pl
        )
        
        # 顧客・運営KPI（サンプルデータから計算）
        customer_metrics = self._calculate_customer_kpis(business_id, month, business_history)
        utilization_metrics = self._calculate_utilization_kpi(business_id, month, business_history)
        
        # 予算対実績
        budget_vs_actual = self._calculate_budget_vs_actual(business_id, month, pl_statement)
        
        # ダッシュボード総評
        overall_health_score = self._calculate_health_score(
            revenue_metrics, profit_margin_metrics, cost_ratio_metrics
        )
        
        executive_summary = self._generate_executive_summary(
            business.name, pl_statement, overall_health_score
        )
        
        key_insights = self._generate_key_insights(
            business_id, pl_statement, revenue_metrics, profit_margin_metrics, 
            cost_ratio_metrics, overall_health_score
        )
        
        recommendations = self._generate_recommendations(
            pl_statement, revenue_metrics, profit_margin_metrics, cost_ratio_metrics
        )
        
        dashboard = KPIDashboard(
            business_id=business_id,
            business_name=business.name,
            month=month,
            revenue_metrics=revenue_metrics,
            profit_margin_metrics=profit_margin_metrics,
            gross_profit_metrics=gross_profit_metrics,
            operating_profit_metrics=operating_profit_metrics,
            cost_ratio_metrics=cost_ratio_metrics,
            expense_ratio_metrics=expense_ratio_metrics,
            customer_count_metrics=customer_metrics.get("count"),
            new_customer_metrics=customer_metrics.get("new"),
            customer_lifetime_value=customer_metrics.get("lifetime_value"),
            contract_value_metrics=customer_metrics.get("contract_value"),
            utilization_rate_metrics=utilization_metrics,
            budget_vs_actual=budget_vs_actual,
            overall_health_score=overall_health_score,
            executive_summary=executive_summary,
            key_insights=key_insights,
            recommendations=recommendations,
            created_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        return dashboard
    
    def generate_monthly_report(self, month: str) -> DashboardReport:
        """月次経営ダッシュボード報告書を生成"""
        businesses = self.pl_service.load_businesses()
        
        dashboards = []
        company_health_scores = []
        urgent_alerts = []
        
        for business_id, business in businesses.items():
            dashboard = self.generate_dashboard(business_id, month)
            if dashboard:
                dashboards.append(dashboard)
                company_health_scores.append(dashboard.overall_health_score)
                
                # 緊急アラート検出
                if dashboard.overall_health_score < 50:
                    urgent_alerts.append({
                        "business_id": business_id,
                        "business_name": business.name,
                        "alert_type": "健全性低下",
                        "health_score": dashboard.overall_health_score,
                        "message": f"{business.name}のヘルススコアが{dashboard.overall_health_score}に低下しています"
                    })
        
        company_health_score = int(sum(company_health_scores) / len(company_health_scores)) if company_health_scores else 0
        
        company_summary = self._generate_company_summary(dashboards, company_health_score)
        cross_business_insights = self._generate_cross_business_insights(dashboards)
        strategic_recommendations = self._generate_strategic_recommendations(dashboards)
        
        report = DashboardReport(
            report_month=month,
            generated_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            business_dashboards=dashboards,
            company_health_score=company_health_score,
            company_summary=company_summary,
            cross_business_insights=cross_business_insights,
            strategic_recommendations=strategic_recommendations,
            urgent_alerts=urgent_alerts
        )
        
        return report
    
    # KPI計算メソッド
    def _calculate_revenue_kpi(self, current_pl, previous_pl, history) -> KPIMetric:
        """売上高KPI"""
        current_revenue = current_pl.revenue.total_revenue
        previous_revenue = previous_pl.revenue.total_revenue if previous_pl else current_revenue
        
        mom_change = ((current_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
        
        trend = "上昇" if mom_change > 0 else ("下降" if mom_change < 0 else "横ばい")
        status = self._get_status(mom_change, 5)  # 5%以上が良好
        
        return KPIMetric(
            metric_name="売上高",
            current_value=current_revenue,
            previous_value=previous_revenue,
            month_over_month_change=mom_change,
            trend=trend,
            status=status,
            assessment=f"売上高は{abs(mom_change):.1f}%の{trend}トレンドを示しています"
        )
    
    def _calculate_margin_kpi(self, current_pl, previous_pl) -> KPIMetric:
        """利益率KPI"""
        current_margin = current_pl.profit_margin
        previous_margin = previous_pl.profit_margin if previous_pl else current_margin
        
        margin_change = current_margin - previous_margin
        trend = "上昇" if margin_change > 0 else ("下降" if margin_change < 0 else "横ばい")
        status = self._get_status(current_margin, 10)  # 10%以上が良好
        
        return KPIMetric(
            metric_name="利益率",
            current_value=current_margin,
            previous_value=previous_margin,
            month_over_month_change=margin_change,
            trend=trend,
            status=status,
            assessment=f"営業利益率は{current_margin:.1f}%で、前月比{margin_change:+.1f}%ポイント{trend}しています"
        )
    
    def _calculate_gross_profit_kpi(self, current_pl, previous_pl) -> KPIMetric:
        """売上総利益KPI"""
        current_gross = current_pl.gross_profit
        previous_gross = previous_pl.gross_profit if previous_pl else current_gross
        
        mom_change = ((current_gross - previous_gross) / previous_gross * 100) if previous_gross > 0 else 0
        trend = "上昇" if mom_change > 0 else ("下降" if mom_change < 0 else "横ばい")
        status = self._get_status(mom_change, 3)
        
        return KPIMetric(
            metric_name="売上総利益",
            current_value=current_gross,
            previous_value=previous_gross,
            month_over_month_change=mom_change,
            trend=trend,
            status=status,
            assessment=f"売上総利益は{abs(mom_change):.1f}%の{trend}トレンドです"
        )
    
    def _calculate_operating_profit_kpi(self, current_pl, previous_pl) -> KPIMetric:
        """営業利益KPI"""
        current_profit = current_pl.operating_profit
        previous_profit = previous_pl.operating_profit if previous_pl else current_profit
        
        mom_change = ((current_profit - previous_profit) / max(abs(previous_profit), 1) * 100) if previous_profit != 0 else 0
        trend = "上昇" if current_profit > previous_profit else ("下降" if current_profit < previous_profit else "横ばい")
        status = self._get_status(current_profit / current_pl.revenue.total_revenue * 100, 8) if current_pl.revenue.total_revenue > 0 else "注意"
        
        return KPIMetric(
            metric_name="営業利益",
            current_value=current_profit,
            previous_value=previous_profit,
            month_over_month_change=mom_change,
            trend=trend,
            status=status,
            assessment=f"営業利益は{current_profit:,.0f}円で前月比{mom_change:+.1f}%{trend}しています"
        )
    
    def _calculate_cost_ratio_kpi(self, current_pl, previous_pl) -> KPIMetric:
        """原価率KPI"""
        current_ratio = (current_pl.cost.total_direct_costs / current_pl.revenue.total_revenue * 100) if current_pl.revenue.total_revenue > 0 else 0
        previous_ratio = (previous_pl.cost.total_direct_costs / previous_pl.revenue.total_revenue * 100) if previous_pl and previous_pl.revenue.total_revenue > 0 else current_ratio
        
        ratio_change = current_ratio - previous_ratio
        trend = "低下（改善）" if ratio_change < 0 else ("上昇（悪化）" if ratio_change > 0 else "横ばい")
        status = self._get_status(100 - current_ratio, 50)  # 原価率が低いほどよい
        
        return KPIMetric(
            metric_name="原価率",
            current_value=current_ratio,
            previous_value=previous_ratio,
            month_over_month_change=ratio_change,
            trend=trend,
            status=status,
            assessment=f"原価率は{current_ratio:.1f}%で、前月比{ratio_change:+.1f}%ポイント{trend}しています"
        )
    
    def _calculate_expense_ratio_kpi(self, current_pl, previous_pl) -> KPIMetric:
        """経費率KPI"""
        current_ratio = (current_pl.expense.total_expenses / current_pl.revenue.total_revenue * 100) if current_pl.revenue.total_revenue > 0 else 0
        previous_ratio = (previous_pl.expense.total_expenses / previous_pl.revenue.total_revenue * 100) if previous_pl and previous_pl.revenue.total_revenue > 0 else current_ratio
        
        ratio_change = current_ratio - previous_ratio
        trend = "低下（改善）" if ratio_change < 0 else ("上昇（悪化）" if ratio_change > 0 else "横ばい")
        status = self._get_status(100 - current_ratio, 60)
        
        return KPIMetric(
            metric_name="経費率",
            current_value=current_ratio,
            previous_value=previous_ratio,
            month_over_month_change=ratio_change,
            trend=trend,
            status=status,
            assessment=f"経費率は{current_ratio:.1f}%で、コスト管理の{status}です"
        )
    
    def _calculate_customer_kpis(self, business_id: str, month: str, history: Dict) -> Dict[str, Optional[KPIMetric]]:
        """顧客関連KPI（サンプルデータから推定）"""
        # 実装では外部CRMシステムと統合
        previous_month = self._get_previous_month(month)
        
        # サンプル計算
        current_customers = history.get(month, {}).get("customer_count", 0) or 100
        previous_customers = history.get(previous_month, {}).get("customer_count", 0) or 95
        
        customer_count_metric = KPIMetric(
            metric_name="顧客数",
            current_value=current_customers,
            previous_value=previous_customers,
            month_over_month_change=((current_customers - previous_customers) / previous_customers * 100) if previous_customers > 0 else 0,
            trend="上昇" if current_customers > previous_customers else "下降",
            status="良好" if current_customers > previous_customers else "注意",
            assessment=f"顧客数は{int(current_customers)}で、前月比{((current_customers - previous_customers) / previous_customers * 100):+.1f}%"
        )
        
        return {
            "count": customer_count_metric,
            "new": None,
            "lifetime_value": None,
            "contract_value": None
        }
    
    def _calculate_utilization_kpi(self, business_id: str, month: str, history: Dict) -> Optional[KPIMetric]:
        """稼働率KPI（サンプルデータから推定）"""
        current_util = history.get(month, {}).get("utilization_rate", 0) or 85
        previous_util = history.get(self._get_previous_month(month), {}).get("utilization_rate", 0) or 83
        
        return KPIMetric(
            metric_name="稼働率",
            current_value=current_util,
            previous_value=previous_util,
            month_over_month_change=current_util - previous_util,
            trend="上昇" if current_util > previous_util else "下降",
            status="良好" if current_util >= 80 else "注意",
            assessment=f"稼働率は{current_util:.1f}%で、前月比{(current_util - previous_util):+.1f}%ポイント"
        )
    
    def _calculate_budget_vs_actual(self, business_id: str, month: str, pl: Any) -> Dict[str, Any]:
        """予算対実績"""
        # 実装では予算マスタから取得
        budget_revenue = pl.revenue.total_revenue * 1.1  # サンプル：予算は実績の110%
        budget_operating_profit = pl.operating_profit * 1.2
        
        return {
            "revenue": {
                "budget": budget_revenue,
                "actual": pl.revenue.total_revenue,
                "variance": ((pl.revenue.total_revenue - budget_revenue) / budget_revenue * 100) if budget_revenue > 0 else 0,
                "status": "未達" if pl.revenue.total_revenue < budget_revenue else "達成"
            },
            "operating_profit": {
                "budget": budget_operating_profit,
                "actual": pl.operating_profit,
                "variance": ((pl.operating_profit - budget_operating_profit) / abs(budget_operating_profit) * 100) if budget_operating_profit != 0 else 0,
                "status": "未達" if pl.operating_profit < budget_operating_profit else "達成"
            }
        }
    
    # 評価・分析メソッド
    def _get_status(self, value: float, threshold: float) -> str:
        """数値から状態を判定"""
        if value >= threshold:
            return "良好"
        elif value >= threshold * 0.5:
            return "注意"
        else:
            return "要改善"
    
    def _calculate_health_score(self, revenue_metric, profit_metric, cost_metric) -> int:
        """ダッシュボードヘルススコア（0-100）を計算"""
        scores = []
        
        # 売上成長性（MoM変化率）
        revenue_score = min(100, max(0, 50 + (revenue_metric.month_over_month_change * 5)))
        scores.append(revenue_score)
        
        # 収益性（利益率）
        profit_score = min(100, max(0, profit_metric.current_value * 5))
        scores.append(profit_score)
        
        # コスト効率（原価率が低いほどよい）
        cost_score = min(100, max(0, (100 - cost_metric.current_value) * 1.5))
        scores.append(cost_score)
        
        health_score = int(sum(scores) / len(scores))
        return health_score
    
    def _generate_executive_summary(self, business_name: str, pl, health_score: int) -> str:
        """経営層向けサマリー文生成"""
        status = "好調" if health_score >= 70 else ("要注視" if health_score >= 50 else "要改善")
        profit_status = "黒字" if pl.operating_profit > 0 else "赤字"
        
        return f"{business_name}は現在{status}な状態です。売上高{pl.revenue.total_revenue:,.0f}円に対し、営業利益は{pl.operating_profit:,.0f}円({profit_status})となっています。ヘルススコアは{health_score}点です。"
    
    def _generate_key_insights(self, business_id, pl, revenue_metric, profit_metric, cost_metric, health_score) -> List[str]:
        """主要インサイト生成"""
        insights = []
        
        if revenue_metric.month_over_month_change > 10:
            insights.append(f"✓ 売上が好調に推移（前月比{revenue_metric.month_over_month_change:.1f}%増）")
        elif revenue_metric.month_over_month_change < -5:
            insights.append(f"⚠ 売上が減少（前月比{revenue_metric.month_over_month_change:.1f}%）")
        
        if profit_metric.status == "良好":
            insights.append(f"✓ 利益率が良好水準（{profit_metric.current_value:.1f}%）")
        elif profit_metric.status == "要改善":
            insights.append(f"⚠ 利益率が低い（{profit_metric.current_value:.1f}%）")
        
        if cost_metric.month_over_month_change < -2:
            insights.append(f"✓ コスト削減が進行中（原価率が{cost_metric.month_over_month_change:.1f}%ポイント低下）")
        elif cost_metric.month_over_month_change > 2:
            insights.append(f"⚠ コストが増加傾向（原価率が{cost_metric.month_over_month_change:.1f}%ポイント上昇）")
        
        return insights if insights else [f"ビジネスはヘルススコア{health_score}で推移しています"]
    
    def _generate_recommendations(self, pl, revenue_metric, profit_metric, cost_metric) -> List[str]:
        """アクション提案生成"""
        recommendations = []
        
        if profit_metric.current_value < 5:
            recommendations.append("⚡ 利益率が低い。コスト削減と売上改善を急務とします")
        
        if cost_metric.current_value > 60:
            recommendations.append("⚡ 原価率が高い。仕入れの最適化や生産効率の改善を検討してください")
        
        if revenue_metric.month_over_month_change < -5:
            recommendations.append("⚡ 売上減少に対応。営業活動の強化や新規顧客開拓を加速させてください")
        
        if len(recommendations) == 0:
            recommendations.append("✓ 現在のビジネス推移は良好です。成長投資の検討をお勧めします")
        
        return recommendations
    
    def _generate_company_summary(self, dashboards: List[KPIDashboard], health_score: int) -> str:
        """企業全体のサマリー"""
        total_revenue = sum(d.revenue_metrics.current_value for d in dashboards)
        total_profit = sum(d.operating_profit_metrics.current_value for d in dashboards)
        
        status = "好調" if health_score >= 70 else ("安定" if health_score >= 50 else "低調")
        
        return f"当月企業全体は{status}に推移しています。総売上{total_revenue:,.0f}円に対し、営業利益は{total_profit:,.0f}円です。企業ヘルススコアは{health_score}点です。"
    
    def _generate_cross_business_insights(self, dashboards: List[KPIDashboard]) -> List[str]:
        """事業間比較インサイト"""
        insights = []
        
        if len(dashboards) < 2:
            return insights
        
        # 利益率トップ・ボトム
        sorted_by_margin = sorted(dashboards, key=lambda d: d.profit_margin_metrics.current_value, reverse=True)
        best_margin = sorted_by_margin[0]
        worst_margin = sorted_by_margin[-1]
        
        insights.append(f"利益率で見ると、{best_margin.business_name}が最高（{best_margin.profit_margin_metrics.current_value:.1f}%）で、{worst_margin.business_name}が最低（{worst_margin.profit_margin_metrics.current_value:.1f}%）です")
        
        # 売上成長トップ・ボトム
        sorted_by_growth = sorted(dashboards, key=lambda d: d.revenue_metrics.month_over_month_change, reverse=True)
        if sorted_by_growth[0].revenue_metrics.month_over_month_change > 0:
            insights.append(f"成長率で見ると、{sorted_by_growth[0].business_name}が最も好調です")
        
        return insights
    
    def _generate_strategic_recommendations(self, dashboards: List[KPIDashboard]) -> List[str]:
        """戦略提案生成"""
        recommendations = []
        
        # 赤字事業の検出
        unprofitable = [d for d in dashboards if d.operating_profit_metrics.current_value < 0]
        if unprofitable:
            names = ", ".join([d.business_name for d in unprofitable])
            recommendations.append(f"🎯 {names}が赤字です。改善計画を立案し、3ヶ月で黒字化を目指してください")
        
        # 低健全性事業の検出
        low_health = [d for d in dashboards if d.overall_health_score < 50]
        if low_health:
            names = ", ".join([d.business_name for d in low_health])
            recommendations.append(f"🎯 {names}のヘルススコアが低い。経営面談を開催し、改革プランを策定してください")
        
        # ポートフォリオ最適化
        if len(dashboards) > 2:
            recommendations.append("🎯 事業ポートフォリオ分析を実施し、リソース配分の最適化を検討してください")
        
        return recommendations
    
    def _get_previous_month(self, month: str) -> str:
        """前月を取得（YYYY-MM形式）"""
        from datetime import datetime, timedelta
        current = datetime.strptime(month, "%Y-%m")
        previous = current - timedelta(days=1)
        return previous.strftime("%Y-%m")
