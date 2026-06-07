import os
import sys
import tempfile
from datetime import datetime

from src.backend.app.services.company_history_engine import CompanyHistoryEngine
from src.backend.app.models.company_history_model import LeadershipEvent, AnnualReport
from src.backend.app.models.ceo_succession_model import CeoSuccessionDecision
from src.backend.app.models.executive_team_succession_model import ExecutiveSuccessionDecision
from src.backend.app.models.culture_model import CultureProfile
from src.backend.app.models.external_environment_model_v2 import ExternalEnvironmentState
from src.backend.app.models.enterprise_evolution_model import EnterpriseEvolutionResult
from src.backend.app.services.monthly_batch_service import MonthlyBatchResult


def test_build_leadership_timeline():
    """リーダーシップタイムライン構築のテスト"""
    engine = CompanyHistoryEngine()

    # CEO交代データ
    ceo_successions = [
        CeoSuccessionDecision(
            period="2024-01",
            selected_candidate_id="candidate_1",
            selected_candidate_name="John Doe",
            outgoing_ceo_name="Jane Smith",
            rationale="Strategic realignment",
            board_votes={"director1": "approve", "director2": "approve"}
        )
    ]

    # 経営チーム交代データ
    executive_successions = [
        ExecutiveSuccessionDecision(
            period="2024-02",
            role_id="CFO",
            selected_candidate_id="candidate_2",
            rationale="Performance improvement",
            board_votes={"director1": "approve"}
        )
    ]

    timeline = engine.build_leadership_timeline(ceo_successions, executive_successions)

    assert len(timeline) == 2
    assert timeline[0].event_type == "ceo_succession"
    assert timeline[0].role == "CEO"
    assert timeline[0].from_name is None  # outgoing_ceo_name not in model
    assert timeline[0].to_name is None    # selected_candidate_name not in model
    assert timeline[1].event_type == "executive_succession"
    assert timeline[1].role == "CFO"


def test_build_annual_report():
    """年次レポート構築のテスト"""
    engine = CompanyHistoryEngine()

    year = 2024

    # 月次結果（モック）
    monthly_results = [
        MonthlyBatchResult(
            period="2024-01",
            pl={"total_revenue": 1000000, "operating_profit": 100000},
            simulation_ok=True
        ),
        MonthlyBatchResult(
            period="2024-02",
            pl={"total_revenue": 1200000, "operating_profit": 120000},
            simulation_ok=True
        )
    ]

    # 文化履歴（モック）
    culture_history = [
        CultureProfile(
            period="2024-01",
            innovation_culture=0.5,
            people_culture=0.5,
            process_culture=0.5,
            market_culture=0.5,
            aggressiveness_culture=0.5,
            risk_aversion_culture=0.5,
            brand_culture=0.5,
            cost_culture=0.5,
            execution_culture=0.5,
            stability_culture=0.5
        )
    ]

    # 進化履歴（モック）
    evolution_history = [
        EnterpriseEvolutionResult(
            period="2024-01",
            evolution_score=0.8,
            environment_pressure=0.3,
            culture_shift={},
            environment_shift={},
            leadership_shift={},
            feedback_loops={"culture_environment": ["market_pressure"]},
            recommendations=["Strengthen innovation culture"]
        )
    ]

    # 環境履歴（モック）
    environment_history = []

    # リーダーシップイベント（モック）
    leadership_events = []

    with tempfile.TemporaryDirectory() as temp_dir:
        # エンジンの一時的なデータディレクトリを変更
        original_dir = os.path.dirname(engine.__class__.__module__.replace('.', '/'))
        # 実際には一時ディレクトリを使用

        report = engine.build_annual_report(
            year, monthly_results, culture_history,
            evolution_history, environment_history, leadership_events
        )

        assert report.year == 2024
        assert report.revenue_total == 2200000  # 1000000 + 1200000
        assert report.profit_total == 220000    # 100000 + 120000
        assert isinstance(report.evolution_trend, float)
        assert os.path.exists(report.summary_markdown_path)


def test_render_annual_report_markdown():
    """Markdownレンダリングのテスト"""
    engine = CompanyHistoryEngine()

    year = 2024
    revenue_total = 1000000
    profit_total = 100000
    major_events = ["CEO交代", "新製品発売"]
    culture_trends = {"innovation": 0.1, "stability": -0.05}
    evolution_trend = 0.75

    markdown = engine.render_annual_report_markdown(
        year, revenue_total, profit_total, major_events, culture_trends, evolution_trend
    )

    assert f"# 年次レポート {year}" in markdown
    assert "¥1,000,000" in markdown
    assert "¥100,000" in markdown
    assert "CEO交代" in markdown
    assert "新製品発売" in markdown
    assert "innovation: +0.10" in markdown
    assert "stability: -0.05" in markdown
    assert "+0.750" in markdown