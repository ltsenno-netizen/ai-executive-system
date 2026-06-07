import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

from ..models.corporate_intent_model import (
    CorporateIntent,
    IntentScore,
    IntentAlignment,
    IntentLearningHistory,
    IntentAnalysis,
)
from ..models.multi_objective_model import ParetoFrontier
from .corporate_intent_engine import (
    score_candidate,
    select_strategy_by_intent,
    rank_candidates_by_intent,
    calculate_intent_alignment,
    update_intent_from_history,
    apply_learning_to_intent,
)
from .multi_objective_service import MultiObjectiveService


class CorporateIntentService:
    """企業意思の管理と学習"""

    def __init__(self):
        self.data_dir = Path("data/corporate_intent")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.intent_file = self.data_dir / "intent.json"
        self.multi_objective_service = MultiObjectiveService()
        self._autonomous_service = None  # Lazy-loaded to avoid circular imports

    @property
    def autonomous_service(self):
        """Lazy-load autonomous service to avoid circular imports"""
        if self._autonomous_service is None:
            from .autonomous_enterprise_service import AutonomousEnterpriseService
            self._autonomous_service = AutonomousEnterpriseService()
        return self._autonomous_service

    def get_intent(self) -> Optional[CorporateIntent]:
        """現在の企業意思を取得"""
        try:
            if self.intent_file.exists():
                with open(self.intent_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return CorporateIntent(**data)
            else:
                # デフォルト Intent を作成して返す
                default_intent = CorporateIntent()
                self.save_intent(default_intent)
                return default_intent
        except Exception:
            return CorporateIntent()

    def save_intent(
        self,
        intent: CorporateIntent,
        reason: Optional[str] = None,
    ) -> bool:
        """企業意思を保存"""
        try:
            intent.last_updated = datetime.now()
            if reason:
                intent.update_reason = reason
            intent.normalize_weights()

            with open(self.intent_file, "w", encoding="utf-8") as f:
                json.dump(intent.model_dump(), f, ensure_ascii=False, indent=2, default=str)
            return True
        except Exception:
            return False

    def set_intent(
        self,
        growth_weight: float,
        profitability_weight: float,
        innovation_weight: float,
        stability_weight: float,
        risk_preference: float,
        time_horizon: float,
        cultural_identity: str,
    ) -> CorporateIntent:
        """企業意思を明示的に設定"""
        new_intent = CorporateIntent(
            growth_weight=growth_weight,
            profitability_weight=profitability_weight,
            innovation_weight=innovation_weight,
            stability_weight=stability_weight,
            risk_preference=risk_preference,
            time_horizon=time_horizon,
            cultural_identity=cultural_identity,
        )
        new_intent.normalize_weights()
        self.save_intent(new_intent, reason="Explicit Intent Configuration")
        return new_intent

    def update_intent_from_learning(self) -> CorporateIntent:
        """
        過去のサイクルから学習して Intent を更新

        1. 現在の Intent を取得
        2. Autonomous cycle 履歴を取得
        3. 学習を実行
        4. Intent を更新して保存
        5. 新 Intent を返す
        """
        current_intent = self.get_intent()
        if not current_intent:
            current_intent = CorporateIntent()

        # Autonomous cycle 履歴を取得
        history = self.autonomous_service.get_cycle_history()
        if not history or not history.cycles:
            # 履歴がない場合は、現在の Intent をそのまま返す
            return current_intent

        # 学習を実行
        learning_history = update_intent_from_history(
            current_intent, history.cycles
        )

        # 学習結果を Intent に反映
        updated_intent = apply_learning_to_intent(current_intent, learning_history)

        # 保存
        self.save_intent(
            updated_intent,
            reason=f"Learning from {learning_history.cycle_count} cycles (confidence: {learning_history.learning_confidence:.2%})"
        )

        return updated_intent

    def select_optimal_strategy(self) -> tuple:
        """
        現在の Intent に基づいて Pareto frontier から最適戦略を選択

        Returns:
            (最適候補, スコア) のタプル
        """
        intent = self.get_intent()
        if not intent:
            intent = CorporateIntent()

        # Pareto frontier を取得
        frontier = self.multi_objective_service.get_frontier()
        if not frontier:
            raise ValueError("Pareto frontier not available")

        # Intent に基づいて選択
        candidate, score = select_strategy_by_intent(intent, frontier)
        return candidate, score

    def rank_strategies(self) -> list:
        """
        現在の Intent に基づいてすべての戦略をランク付け

        Returns:
            スコア降順の (候補, スコア) リスト
        """
        intent = self.get_intent()
        if not intent:
            intent = CorporateIntent()

        # Pareto frontier を取得
        frontier = self.multi_objective_service.get_frontier()
        if not frontier:
            raise ValueError("Pareto frontier not available")

        # ランク付け
        ranked = rank_candidates_by_intent(intent, frontier)
        return ranked

    def analyze_intent(self) -> IntentAnalysis:
        """
        現在の企業意思を詳細分析

        Intent、推奨戦略、代替案、学習履歴などを含む
        """
        current_intent = self.get_intent()
        if not current_intent:
            current_intent = CorporateIntent()

        # Pareto frontier を取得
        frontier = self.multi_objective_service.get_frontier()
        if not frontier:
            raise ValueError("Pareto frontier not available")

        # 最適戦略を選択
        ranked_strategies = rank_candidates_by_intent(current_intent, frontier)

        # スコア分布を作成
        score_distribution = {
            f"{candidate.scenario_type}_{candidate.optimization_objective}": score.score
            for candidate, score in ranked_strategies
        }

        # 最適戦略
        best_candidate, best_score = ranked_strategies[0] if ranked_strategies else (None, None)

        # 代替案（上位 3 件のうち最適以外）
        alternatives = [
            {
                "candidate_id": f"{candidate.scenario_type}_{candidate.optimization_objective}",
                "candidate_desc": candidate.roadmap_title,
                "score": score.score,
            }
            for candidate, score in ranked_strategies[1:4]
        ]

        # 学習履歴を取得
        history = self.autonomous_service.get_cycle_history()
        learning_history = None
        if history and history.cycles:
            learning_history = update_intent_from_history(
                current_intent, history.cycles
            )

        return IntentAnalysis(
            current_intent=current_intent,
            frontier_score_distribution=score_distribution,
            recommended_strategy_id=f"{best_candidate.scenario_type}_{best_candidate.optimization_objective}" if best_candidate else None,
            recommended_strategy_score=best_score.score if best_score else None,
            alternative_strategies=alternatives,
            learning_history=learning_history,
        )

    def get_alignment_analysis(self, candidate_id: str) -> Optional[IntentAlignment]:
        """
        特定の戦略の Intent への整合性を分析

        Args:
            candidate_id: "{scenario_type}_{objective}" 形式の候補 ID

        Returns:
            IntentAlignment または None
        """
        intent = self.get_intent()
        if not intent:
            intent = CorporateIntent()

        # Pareto frontier を取得
        frontier = self.multi_objective_service.get_frontier()
        if not frontier:
            return None

        # 候補を探す
        for candidate in frontier.candidates:
            if f"{candidate.scenario_type}_{candidate.optimization_objective}" == candidate_id:
                return calculate_intent_alignment(intent, candidate)

        return None

    def export_intent_to_markdown(self) -> str:
        """Intent を Markdown 形式で出力"""
        intent = self.get_intent()
        if not intent:
            intent = CorporateIntent()

        md = f"""# 企業意思（Corporate Intent）

## 基本設定

### 目的の重み付け

- **成長（Growth）**: {intent.growth_weight:.1%}
- **収益性（Profitability）**: {intent.profitability_weight:.1%}
- **革新性（Innovation）**: {intent.innovation_weight:.1%}
- **安定性（Stability）**: {intent.stability_weight:.1%}

### 企業特性

- **リスク選好度**: {intent.risk_preference:.1%} ({self._risk_preference_label(intent.risk_preference)})
- **時間軸**: {intent.time_horizon:.1%} ({self._time_horizon_label(intent.time_horizon)})
- **文化的アイデンティティ**: {intent.cultural_identity}

### メタデータ

- **最終更新**: {intent.last_updated or 'N/A'}
- **更新理由**: {intent.update_reason or 'Initial Setup'}
- **バージョン**: {intent.version}
"""
        return md

    @staticmethod
    def _risk_preference_label(risk_pref: float) -> str:
        if risk_pref < 0.3:
            return "超保守"
        elif risk_pref < 0.5:
            return "保守"
        elif risk_pref < 0.7:
            return "バランス"
        else:
            return "攻め"

    @staticmethod
    def _time_horizon_label(time_horizon: float) -> str:
        if time_horizon < 0.3:
            return "短期志向"
        elif time_horizon < 0.5:
            return "短期"
        elif time_horizon < 0.7:
            return "中期"
        else:
            return "長期志向"
