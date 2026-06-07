import os
import sys
import tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.models.executive_narrative_model import DecisionRationale, ExecutiveNarrative
from app.services.executive_report_service import ExecutiveReportService


def make_sample_narrative():
    return ExecutiveNarrative(
        period='2026-04',
        summary='4月の経営は市場動向と資本政策の調整が中心でした。',
        financial_section='主要財務項目は安定しています。',
        market_section='市場は依然として不安定です。',
        organization_section='組織は実行力強化フェーズです。',
        investment_section='投資は保守的に進められました。',
        risk_section='流動性リスクに注意が必要です。',
        decisions_section=DecisionRationale(
            option_id='A',
            label='積極投資',
            pros=['成長機会を確保', 'シェア拡大'],
            cons=['キャッシュ負担', '実行リスク'],
            why_chosen='長期価値を優先しました。',
        ),
        next_month_focus=['収益性の高い施策に集中する', '組織の実行状況を確認する'],
    )


def test_generate_get_list_report():
    with tempfile.TemporaryDirectory() as tmp_dir:
        service = ExecutiveReportService(data_path=tmp_dir)
        narrative = make_sample_narrative()
        financials = {'revenue': 12.3, 'profit': 1.2, 'cash_balance': 3.2, 'profit_margin': 0.12, 'investment_requests_pending': []}
        market_state = {'market_index_by_segment': {'AI': 1.2}, 'active_events': []}
        org_state = {'units': [{'headcount': 100, 'open_positions': 2, 'workload_index': 0.9}]}
        meeting_state = {'selected_option_id': 'A', 'decision_options': [{'id': 'A', 'label': '積極投資'}]}

        report = service.generate_and_store_report('2026-04', narrative, financials, market_state, org_state, meeting_state)
        assert report.period == '2026-04'

        path = os.path.join(service.reports_path, '2026-04.md')
        assert os.path.exists(path)

        content = service.get_report('2026-04')
        assert '# 月次経営レポート — 2026年4月' in content

        history = service.list_reports(limit=1)
        assert history[0]['period'] == '2026-04'
        assert history[0]['title'] == '月次経営レポート — 2026年4月'
