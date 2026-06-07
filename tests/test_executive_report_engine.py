import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.models.executive_narrative_model import DecisionRationale, ExecutiveNarrative
from app.services.executive_report_engine import ExecutiveReportEngine


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


def test_build_monthly_report():
    engine = ExecutiveReportEngine()
    narrative = make_sample_narrative()
    financials = {'revenue': 12.3, 'profit': 1.2, 'cash_balance': 3.2, 'profit_margin': 0.12, 'investment_requests_pending': []}
    market_state = {'market_index_by_segment': {'AI': 1.2}, 'active_events': []}
    org_state = {'units': [{'headcount': 100, 'open_positions': 2, 'workload_index': 0.9}]}
    meeting_state = {'selected_option_id': 'A', 'decision_options': [{'id': 'A', 'label': '積極投資'}]}

    report = engine.build_monthly_report('2026-04', narrative, financials, market_state, org_state, meeting_state)

    assert report.period == '2026-04'
    assert report.title == '月次経営レポート 2026年4月'
    assert report.management_summary == narrative.summary
    assert len(report.sections) == 8


def test_report_includes_ai_ceo_decision_reason():
    engine = ExecutiveReportEngine()
    narrative = make_sample_narrative()
    financials = {'revenue': 12.3, 'profit': 1.2, 'cash_balance': 3.2, 'profit_margin': 0.12, 'investment_requests_pending': []}
    market_state = {'market_index_by_segment': {'AI': 1.2}, 'active_events': []}
    org_state = {'units': [{'headcount': 100, 'open_positions': 2, 'workload_index': 0.9}]}
    meeting_state = {
        'selected_option_id': 'C',
        'decision_options': [{'id': 'C', 'label': 'バランス型'}],
        'ceo_selected_option_label': 'バランス型',
        'ceo_decision_rationale': '成長と安全のバランスを重視しました。',
        'ceo_persona': {
            'aggressiveness': 0.7,
            'risk_tolerance': 0.6,
            'brand_priority': 0.8,
            'short_term_focus': 0.6,
            'long_term_focus': 0.8,
        },
        'decision_actor': 'AI CEO',
    }

    report = engine.build_monthly_report('2026-04', narrative, financials, market_state, org_state, meeting_state)
    markdown = engine.render_report_markdown(report)

    assert 'AI CEO' in markdown
    assert '成長と安全のバランスを重視しました。' in markdown
    assert 'CEO 経営スタイル（2026）' in markdown
    assert '攻め度' in markdown or 'ブランド重視' in markdown


def test_report_includes_board_review_section():
    engine = ExecutiveReportEngine()
    narrative = make_sample_narrative()
    financials = {'revenue': 12.3, 'profit': 1.2, 'cash_balance': 3.2, 'profit_margin': 0.12, 'investment_requests_pending': []}
    market_state = {'market_index_by_segment': {'AI': 1.2}, 'active_events': []}
    org_state = {'units': [{'headcount': 100, 'open_positions': 2, 'workload_index': 0.9}]}
    meeting_state = {
        'selected_option_id': 'C',
        'decision_options': [{'id': 'C', 'label': 'バランス型'}],
        'ceo_selected_option_label': 'バランス型',
        'ceo_decision_rationale': '成長と安全のバランスを重視しました。',
        'board_decision': {
            'status': 'approved',
            'final_option_id': 'C',
            'final_option_label': 'バランス型',
            'board_rationale': 'CEOの案は財務・組織面で妥当と判断しました。',
            'conditions': None,
        },
    }

    report = engine.build_monthly_report('2026-04', narrative, financials, market_state, org_state, meeting_state)
    markdown = engine.render_report_markdown(report)

    assert '5. 取締役会の判断' in markdown
    assert 'CEO 提案: バランス型' in markdown
    assert 'Board 判定: approved' in markdown
    assert '最終決定案: バランス型' in markdown
    assert 'CEOの案は財務・組織面で妥当と判断しました。' in markdown


def test_render_report_markdown():
    engine = ExecutiveReportEngine()
    narrative = make_sample_narrative()
    financials = {'revenue': 12.3, 'profit': 1.2, 'cash_balance': 3.2, 'profit_margin': 0.12, 'investment_requests_pending': []}
    market_state = {'market_index_by_segment': {'AI': 1.2}, 'active_events': []}
    org_state = {'units': [{'headcount': 100, 'open_positions': 2, 'workload_index': 0.9}]}
    meeting_state = {'selected_option_id': 'A', 'decision_options': [{'id': 'A', 'label': '積極投資'}]}

    report = engine.build_monthly_report('2026-04', narrative, financials, market_state, org_state, meeting_state)
    markdown = engine.render_report_markdown(report)

    assert '# 月次経営レポート — 2026年4月' in markdown
    assert '## 1. マネジメントサマリ' in markdown
    assert '## 2. 財務ハイライト' in markdown
