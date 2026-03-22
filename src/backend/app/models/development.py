from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

class DevelopmentMilestone(BaseModel):
    month: int
    title: str
    description: str
    objectives: List[str]
    activities: List[str]
    evaluation_criteria: List[str]

class DevelopmentPlan(BaseModel):
    member_id: int
    member_name: str
    role: str
    current_level: str
    target_level: str
    plan_duration_months: int
    milestones: List[DevelopmentMilestone]
    overall_objectives: List[str]
    success_metrics: List[str]
    created_date: str

class Achievement(BaseModel):
    milestone_month: int
    milestone_title: str
    completion_percentage: int  # 0-100
    completed_objectives: List[str]
    remaining_objectives: List[str]
    completed_activities: List[str]
    remaining_activities: List[str]
    evaluation_results: List[str]
    notes: Optional[str] = None

class MonthlyReview(BaseModel):
    member_id: int
    month: int
    review_date: str
    achievements: List[Achievement]
    overall_progress: int  # 0-100
    strengths_demonstrated: List[str]
    challenges_encountered: List[str]
    next_month_focus: List[str]
    manager_feedback: str
    member_reflection: Optional[str] = None

class DevelopmentProgress(BaseModel):
    member_id: int
    member_name: str
    role: str
    plan_created_date: str
    current_month: int
    overall_completion: int  # 0-100
    monthly_reviews: List[MonthlyReview]
    upcoming_milestones: List[DevelopmentMilestone]
    recommended_actions: List[str]
    last_updated: str

class AssessmentCase(BaseModel):
    id: str
    title: str
    scenario: str
    context: str
    challenge: str
    role: str  # 受験者の役割（部長、課長など）
    difficulty_level: str  # "basic", "intermediate", "advanced"
    evaluation_criteria: List[str]
    key_competencies: List[str]  # 判断力、リーダーシップ、コミュニケーションなど
    estimated_time: int  # 分単位
    created_date: str

class AssessmentAnswer(BaseModel):
    case_id: str
    member_id: int
    member_name: str
    answer_text: str
    approach_analysis: str  # 回答のアプローチ分析
    submitted_date: str

class AssessmentFeedback(BaseModel):
    answer_id: str
    case_id: str
    member_id: int
    overall_score: int  # 0-100
    competency_scores: dict[str, int]  # 各コンピテンシーのスコア
    strengths: List[str]
    improvement_areas: List[str]
    detailed_feedback: str
    recommended_actions: List[str]
    sample_better_answer: str
    created_date: str

class AssessmentPractice(BaseModel):
    member_id: int
    member_name: str
    role: str
    target_role: str  # 目指す役職
    practice_sessions: List[Dict[str, Any]]  # 練習セッションの履歴
    overall_progress: Dict[str, int]  # 各コンピテンシーの進捗
    recommended_cases: List[str]  # おすすめのケースID
    last_practice_date: str

# フェーズ3: 事業性・予算管理エージェント
class Business(BaseModel):
    id: str
    name: str
    description: str
    business_type: str  # "product", "service", "consulting", etc.
    start_date: str
    status: str  # "active", "planning", "completed"
    owner_id: int  # 担当者ID
    owner_name: str
    created_date: str

class Revenue(BaseModel):
    business_id: str
    month: str  # "YYYY-MM"
    product_sales: float  # 商品売上
    service_sales: float  # サービス売上
    other_revenue: float  # その他収入
    total_revenue: float

class Cost(BaseModel):
    business_id: str
    month: str  # "YYYY-MM"
    direct_materials: float  # 直接材料費
    direct_labor: float  # 直接労務費
    subcontracting: float  # 外注費
    other_direct_costs: float  # その他直接費
    total_direct_costs: float

class Expense(BaseModel):
    business_id: str
    month: str  # "YYYY-MM"
    personnel_expenses: float  # 人件費
    rent_expenses: float  # 家賃
    utilities: float  # 水道光熱費
    marketing_expenses: float  # 販促費
    travel_expenses: float  # 旅費交通費
    communication_expenses: float  # 通信費
    office_supplies: float  # 事務用品費
    depreciation: float  # 減価償却費
    other_expenses: float  # その他経費
    total_expenses: float

class PLStatement(BaseModel):
    business_id: str
    business_name: str
    month: str
    revenue: Revenue
    cost: Cost
    expense: Expense
    gross_profit: float  # 売上総利益
    operating_profit: float  # 営業利益
    profit_margin: float  # 利益率
    break_even_point: float  # 損益分岐点
    status: str  # "黒字" or "赤字"
    analysis: Dict[str, Any]  # 分析結果
    recommendations: List[str]  # 改善提案
    created_date: str

class BusinessSimulation(BaseModel):
    business_id: str
    scenario_name: str
    simulation_months: int  # シミュレーション期間（ヶ月）
    assumptions: Dict[str, Any]  # 前提条件
    monthly_projections: List[Dict[str, Any]]  # 月次予測
    final_projection: Dict[str, Any]  # 最終予測
    risk_analysis: List[str]  # リスク分析
    created_date: str

# フェーズ3続：事業別KPIダッシュボード機能
class KPIMetric(BaseModel):
    metric_name: str  # "売上高", "利益率", "顧客数" など
    current_value: float
    previous_value: float  # 前月値
    target_value: Optional[float] = None  # 目標値
    month_over_month_change: float  # MoM変化率（%）
    year_over_year_change: Optional[float] = None  # YoY変化率（%）
    trend: str  # "上昇", "下降", "横ばい"
    status: str  # "良好", "注意", "要改善"
    assessment: str  # 詳細評価

class KPIDashboard(BaseModel):
    business_id: str
    business_name: str
    month: str
    
    # 財務KPI
    revenue_metrics: KPIMetric  # 売上高
    profit_margin_metrics: KPIMetric  # 利益率
    gross_profit_metrics: KPIMetric  # 売上総利益
    operating_profit_metrics: KPIMetric  # 営業利益
    cost_ratio_metrics: KPIMetric  # 原価率
    expense_ratio_metrics: KPIMetric  # 経費率
    
    # 顧客KPI
    customer_count_metrics: Optional[KPIMetric] = None  # 顧客数
    new_customer_metrics: Optional[KPIMetric] = None  # 新規顧客
    customer_lifetime_value: Optional[KPIMetric] = None  # 顧客価値
    contract_value_metrics: Optional[KPIMetric] = None  # 平均契約単価
    
    # 運営KPI
    utilization_rate_metrics: Optional[KPIMetric] = None  # 稼働率
    employee_productivity: Optional[KPIMetric] = None  # 従業員生産性
    
    # 予算対実績
    budget_vs_actual: Dict[str, Any]  # 予算 vs 実績
    
    # ダッシュボード総評
    overall_health_score: int  # 0-100
    executive_summary: str  # 経営層向けサマリー
    key_insights: List[str]  # 主要インサイト
    recommendations: List[str]  # アクション提案
    
    created_date: str

class DashboardReport(BaseModel):
    report_month: str
    generated_date: str
    business_dashboards: List[KPIDashboard]  # 全事業のダッシュボード
    company_health_score: int  # 企業全体のヘルススコア
    company_summary: str  # 企業全体の状況サマリー
    cross_business_insights: List[str]  # 事業間の比較インサイト
    strategic_recommendations: List[str]  # 経営層向け戦略提案
    urgent_alerts: List[Dict[str, Any]]  # 緊急アラート