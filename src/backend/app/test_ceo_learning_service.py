import pytest
import os
import tempfile
from src.backend.app.models.ceo_learning_model import CeoLearningSnapshot, FinancialResultSummary
from src.backend.app.models.ai_ceo_model import AICeoPersona
from src.backend.app.services.ceo_learning_service import CeoLearningService


class TestCeoLearningService:
    def test_build_learning_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            service = CeoLearningService(persona_root=temp_dir)
            periods = ['2026-01', '2026-02']
            history = service.build_learning_history(periods)

            assert len(history) == 2
            assert all(isinstance(s, CeoLearningSnapshot) for s in history)

    def test_update_and_store_ceo_persona(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            service = CeoLearningService(persona_root=temp_dir)
            persona = service.update_and_store_ceo_persona('2026-01')

            assert isinstance(persona, AICeoPersona)

            # Check file saved
            persona_file = os.path.join(temp_dir, '2026-01.json')
            assert os.path.exists(persona_file)

    def test_get_latest_persona(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            service = CeoLearningService(persona_root=temp_dir)
            # Initially None
            assert service.get_latest_persona() is None

            # After update
            service.update_and_store_ceo_persona('2026-01')
            latest = service.get_latest_persona()
            assert latest is not None
            assert isinstance(latest, AICeoPersona)