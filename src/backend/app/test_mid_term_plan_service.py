import pytest
import os
import tempfile
from src.backend.app.models.mid_term_plan_model import MidTermPlan
from src.backend.app.services.mid_term_plan_service import MidTermPlanService


class TestMidTermPlanService:
    def test_generate_and_store_mid_term_plan(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            service = MidTermPlanService(plan_root=temp_dir)
            plan = service.generate_and_store_mid_term_plan(start_year=2026, horizon_years=3)

            assert isinstance(plan, MidTermPlan)
            assert plan.start_year == 2026
            assert plan.end_year == 2028

            # Check JSON file
            json_file = os.path.join(temp_dir, '2026-2028.json')
            assert os.path.exists(json_file)

            # Check Markdown file
            md_file = os.path.join(temp_dir, '2026-2028.md')
            assert os.path.exists(md_file)

            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert '# 中期経営計画（2026–2028）' in content
                assert '## 6. 取締役会コメント' in content

    def test_get_latest_plan(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            service = MidTermPlanService(plan_root=temp_dir)
            # Generate a plan
            service.generate_and_store_mid_term_plan(start_year=2026, horizon_years=3)

            latest = service.get_latest_plan()
            assert latest is not None
            assert latest.start_year == 2026

    def test_get_plan_by_period(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            service = MidTermPlanService(plan_root=temp_dir)
            service.generate_and_store_mid_term_plan(start_year=2026, horizon_years=3)

            plan = service.get_plan_by_period('2026-2028')
            assert isinstance(plan, MidTermPlan)