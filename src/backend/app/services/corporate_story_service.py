import os
import json
from typing import Dict, Optional
from .corporate_story_engine import generate_corporate_story
from ..models.corporate_story_model import CorporateStory
from .company_history_service import CompanyHistoryService
from .culture_service import CultureService
from .external_environment_service_v2 import ExternalEnvironmentServiceV2
from .scenario_service import ScenarioService
from .self_optimization_service import SelfOptimizationService
from .enterprise_evolution_service import EnterpriseEvolutionService


class CorporateStoryService:
    """企業統合ストーリー生成サービス"""

    def __init__(self):
        self.history_service = CompanyHistoryService()
        self.culture_service = CultureService()
        self.environment_service = ExternalEnvironmentServiceV2()
        self.scenario_service = ScenarioService()
        self.optimization_service = SelfOptimizationService()
        self.evolution_service = EnterpriseEvolutionService()
        
        self.story_dir = os.path.join(
            os.path.dirname(__file__), '../../../data/stories'
        )
        os.makedirs(self.story_dir, exist_ok=True)

    def generate_story(self, period: str) -> CorporateStory:
        """指定期間の企業ストーリーを生成"""
        
        # 1. 各データを取得
        history = self._get_history()
        culture = self._get_culture()
        environment = self._get_environment(period)
        executive_team = self._get_executive_team()
        evolution = self._get_evolution()
        scenarios = self._get_scenarios()
        optimization_plan = self._get_optimization_plan()
        
        # 2. ストーリー生成
        story = generate_corporate_story(
            period,
            history,
            culture,
            environment,
            executive_team,
            evolution,
            scenarios,
            optimization_plan
        )
        
        # 3. Markdown と JSON で保存
        self._save_story(story)
        
        return story

    def get_story(self, period: str) -> Optional[CorporateStory]:
        """指定期間のストーリーを取得"""
        file_path = os.path.join(self.story_dir, f'story_{period}.json')
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return CorporateStory(**data)
        
        return None

    def get_latest_story(self) -> Optional[CorporateStory]:
        """最新のストーリーを取得"""
        if not os.path.exists(self.story_dir):
            return None
        
        files = [f for f in os.listdir(self.story_dir) if f.startswith('story_') and f.endswith('.json')]
        
        if not files:
            return None
        
        latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(self.story_dir, f)))
        
        return self.get_story(latest_file.replace('story_', '').replace('.json', ''))

    def _get_history(self) -> Dict:
        """企業史データを取得"""
        try:
            history = self.history_service.get_latest_annual_history()
            if history:
                return {
                    "major_events": history.major_events,
                    "culture_trends": history.culture_trends,
                    "evolution_trend": history.evolution_trend
                }
        except Exception:
            pass
        
        return {
            "major_events": [],
            "culture_trends": {},
            "evolution_trend": 0.5
        }

    def _get_culture(self) -> Dict:
        """企業文化データを取得"""
        try:
            return self.culture_service.get_latest_culture()
        except Exception:
            return {}

    def _get_environment(self, period: str) -> Dict:
        """外部環境データを取得"""
        try:
            return self.environment_service.get_environment(period)
        except Exception:
            return {}

    def _get_executive_team(self) -> Dict:
        """経営チームデータを取得"""
        # TODO: 実装に応じて修正
        return {
            "CEO": {"aggressiveness": 0.5, "risk_tolerance": 0.5, "brand_priority": 0.5, "short_term_focus": 0.5, "long_term_focus": 0.5},
            "CFO": {"aggressiveness": 0.4, "risk_tolerance": 0.3, "brand_priority": 0.4, "short_term_focus": 0.5, "long_term_focus": 0.5},
            "CMO": {"aggressiveness": 0.6, "risk_tolerance": 0.6, "brand_priority": 0.7, "short_term_focus": 0.5, "long_term_focus": 0.5},
        }

    def _get_evolution(self) -> Dict:
        """進化スコアデータを取得"""
        try:
            result = self.evolution_service.get_latest_evolution_result()
            if result:
                return result
        except Exception:
            pass
        
        return {
            "evolution_score": 0.5,
            "environment_pressure": 0.5,
            "culture_shift": {},
            "leadership_shift": {}
        }

    def _get_scenarios(self) -> list:
        """シナリオデータを取得"""
        try:
            return self.scenario_service.get_all_scenario_results()
        except Exception:
            return []

    def _get_optimization_plan(self) -> Dict:
        """最適化プランを取得"""
        try:
            plan = self.optimization_service.get_latest_plan()
            if plan:
                return plan
        except Exception:
            pass
        
        # フォールバック
        from ..models.self_optimization_model import OptimizationObjective
        from ..models.scenario_model import ScenarioType, ScenarioResult
        
        return {
            "objective": OptimizationObjective.GROWTH,
            "selected_scenario": ScenarioType.BASELINE,
            "recommended_strategies": [],
            "recommended_culture_shifts": [],
            "recommended_leadership_changes": [],
            "expected_evolution_score": 0.5
        }

    def _save_story(self, story: CorporateStory) -> None:
        """ストーリーをファイルに保存"""
        
        # JSON 保存
        json_path = os.path.join(self.story_dir, f'story_{story.period}.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(story.model_dump(), f, ensure_ascii=False, indent=2)
        
        # Markdown 保存
        md_path = os.path.join(self.story_dir, f'story_{story.period}.md')
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# 企業ストーリー（{story.period}）\n\n")
            f.write(f"{story.summary}\n\n")
            f.write("---\n\n")
            
            for section in story.sections:
                f.write(f"## {section.title}\n\n")
                f.write(f"{section.content}\n\n")
        
        # パスを更新
        story.markdown_path = md_path
