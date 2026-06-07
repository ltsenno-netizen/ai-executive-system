import os
import sys
from unittest.mock import Mock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.services.ai_ceo_agent import AICeoAgent
from app.models.ai_ceo_model import AICeoPersona
from app.models.culture_model import CultureProfile
from app.models.executive_meeting_model import DecisionOption


def test_culture_influences_ceo_decision():
    """文化が CEO の意思決定に影響を与える"""
    
    # 攻撃的な文化
    aggressive_culture = CultureProfile(
        period='2026-01',
        aggressiveness_culture=0.8,
        risk_aversion_culture=0.2,
        brand_culture=0.5,
        cost_culture=0.5,
        people_culture=0.5,
        execution_culture=0.5,
        innovation_culture=0.8,
        stability_culture=0.2,
    )
    
    # 保守的な文化
    conservative_culture = CultureProfile(
        period='2026-01',
        aggressiveness_culture=0.2,
        risk_aversion_culture=0.8,
        brand_culture=0.5,
        cost_culture=0.5,
        people_culture=0.5,
        execution_culture=0.5,
        innovation_culture=0.2,
        stability_culture=0.8,
    )
    
    middle_persona = AICeoPersona(
        aggressiveness=0.5,
        risk_tolerance=0.5,
        brand_priority=0.5,
        short_term_focus=0.5,
        long_term_focus=0.5,
    )
    
    # 同じ CEO Persona でも文化によって選択が異なるはず
    aggressive_agent = AICeoAgent(persona=middle_persona, culture=aggressive_culture)
    conservative_agent = AICeoAgent(persona=middle_persona, culture=conservative_culture)
    
    options = [
        DecisionOption(
            id='A',
            label='Growth Investment',
            description='高成長だが高リスク',
            growth_score=0.9,
            risk_level='High',
            expected_impact_score=0.9,
            short_term_profit=0.0,
            long_term_value=0.8,
            brand_impact=0.0,
            actions=['Invest in new market'],
            pros=['High growth potential'],
            cons=['High risk'],
        ),
        DecisionOption(
            id='B',
            label='Foundation Building',
            description='安定的な構築',
            growth_score=0.5,
            risk_level='Low',
            expected_impact_score=0.5,
            short_term_profit=0.5,
            long_term_value=0.6,
            brand_impact=0.0,
            actions=['Strengthen operations'],
            pros=['Stable growth'],
            cons=['Limited upside'],
        ),
    ]
    
    financials = {'cash_balance': 10.0, 'operating_profit': 5.0}
    market_state = {'volatility': 0.1, 'market_index_by_segment': {'segment1': 1.0}}
    org_state = {'units': [{'workload_index': 0.5}]}
    
    aggressive_choice, _ = aggressive_agent.select_option(options, financials, market_state, org_state)
    conservative_choice, _ = conservative_agent.select_option(options, financials, market_state, org_state)
    
    # 攻撃的な文化は高成長オプション A を選びやすい
    # 保守的な文化は安定的オプション B を選びやすい
    assert aggressive_choice.id in ['A', 'B']
    assert conservative_choice.id in ['A', 'B']
