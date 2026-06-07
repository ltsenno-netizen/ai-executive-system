import os
import sys
import tempfile
from unittest.mock import Mock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.services.culture_service import CultureService
from app.models.ai_ceo_model import AICeoPersona


def test_update_and_store_culture():
    """文化が更新・保存される"""
    with tempfile.TemporaryDirectory() as temp_dir:
        service = CultureService(culture_root=temp_dir)
        service.ceo_learning_service.get_latest_persona = Mock(
            return_value=AICeoPersona(
                aggressiveness=0.6,
                risk_tolerance=0.5,
                brand_priority=0.7,
                short_term_focus=0.5,
                long_term_focus=0.8,
            )
        )
        
        culture = service.update_and_store_culture('2026-01')
        
        assert culture.period == '2026-01'
        assert culture.aggressiveness_culture >= 0.0
        assert culture.aggressiveness_culture <= 1.0
        assert os.path.exists(os.path.join(temp_dir, '2026-01.json'))


def test_get_latest_culture():
    """最新の文化を取得"""
    with tempfile.TemporaryDirectory() as temp_dir:
        service = CultureService(culture_root=temp_dir)
        service.ceo_learning_service.get_latest_persona = Mock(
            return_value=AICeoPersona(
                aggressiveness=0.5,
                risk_tolerance=0.5,
                brand_priority=0.5,
                short_term_focus=0.5,
                long_term_focus=0.5,
            )
        )
        
        # 3期間の文化を作成
        for i in range(1, 4):
            period = f'2026-{i:02d}'
            service.update_and_store_culture(period)
        
        latest = service.get_latest_culture()
        assert latest is not None
        assert latest.period == '2026-03'


def test_get_culture_history():
    """文化の履歴を取得"""
    with tempfile.TemporaryDirectory() as temp_dir:
        service = CultureService(culture_root=temp_dir)
        service.ceo_learning_service.get_latest_persona = Mock(
            return_value=AICeoPersona(
                aggressiveness=0.5,
                risk_tolerance=0.5,
                brand_priority=0.5,
                short_term_focus=0.5,
                long_term_focus=0.5,
            )
        )
        
        # 3 期間の文化を作成
        for i in range(1, 4):
            period = f'2026-{i:02d}'
            service.update_and_store_culture(period)
        
        history = service.get_culture_history(periods=12)
        assert len(history) == 3
        assert history[0].period == '2026-01'
        assert history[-1].period == '2026-03'
