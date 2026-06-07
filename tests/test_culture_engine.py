import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.services.culture_engine import CultureEngine
from app.models.ai_ceo_model import AICeoPersona
from app.models.culture_model import CultureProfile


def test_ceo_influence_on_culture():
    """CEO パーソナリティが文化に反映される"""
    engine = CultureEngine()
    
    # 攻め寄りの CEO
    aggressive_ceo = AICeoPersona(
        aggressiveness=0.85,
        risk_tolerance=0.5,
        brand_priority=0.5,
        short_term_focus=0.5,
        long_term_focus=0.5,
    )
    
    previous_culture = CultureProfile(
        period="2026-01",
        aggressiveness_culture=0.5,
        risk_aversion_culture=0.5,
        brand_culture=0.5,
        cost_culture=0.5,
        people_culture=0.5,
        execution_culture=0.5,
        innovation_culture=0.5,
        stability_culture=0.5,
    )
    
    updated = engine.update_culture(
        previous_culture=previous_culture,
        ceo_persona=aggressive_ceo,
        board_decisions=[],
        quarterly_review=None,
    )
    
    # 攻め寄り CEO により aggressiveness_culture が上がるはず
    assert updated['aggressiveness_culture'] > 0.5


def test_culture_natural_decay():
    """文化は徐々に変わる (0.5 に向けて収束)"""
    engine = CultureEngine()
    
    extreme_culture = CultureProfile(
        period="2026-01",
        aggressiveness_culture=0.9,
        risk_aversion_culture=0.1,
        brand_culture=0.9,
        cost_culture=0.9,
        people_culture=0.1,
        execution_culture=0.9,
        innovation_culture=0.9,
        stability_culture=0.1,
    )
    
    base_ceo = AICeoPersona(
        aggressiveness=0.5,
        risk_tolerance=0.5,
        brand_priority=0.5,
        short_term_focus=0.5,
        long_term_focus=0.5,
    )
    
    updated = engine.update_culture(
        previous_culture=extreme_culture,
        ceo_persona=base_ceo,
        board_decisions=[],
        quarterly_review=None,
    )
    
    # 文化が 0.5 に向かって収束していることを確認
    assert updated['aggressiveness_culture'] < 0.9
    assert updated['aggressiveness_culture'] > 0.5  # 0.5に向けて減衰
    assert updated['risk_aversion_culture'] > 0.1
    assert updated['risk_aversion_culture'] < 0.5  # 0.5に向けて増加
