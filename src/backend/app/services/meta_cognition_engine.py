from datetime import datetime
from statistics import mean
from typing import Any, Dict, List, Optional

from ..models.meta_cognition_model import (
    MetaBias,
    MetaCognitionReport,
    MetaDimension,
    MetaScore,
)


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _extract(source: Any, key: str, default: Any = None) -> Any:
    if source is None:
        return default
    if isinstance(source, dict):
        return source.get(key, default)
    return getattr(source, key, default)


def _average(values: List[float], default: float = 0.0) -> float:
    if not values:
        return default
    return mean(values)


def evaluate_intent(intent: Any, decisions: Optional[List[Any]] = None, frontier: Optional[Any] = None) -> MetaScore:
    if not intent:
        rationale = "Intent data unavailable."
        return MetaScore(dimension=MetaDimension.INTENT, score=0.20, confidence=0.20, rationale=rationale)

    alignment = _extract(intent, "alignment_score", None)
    if alignment is None:
        weights = [
            _extract(intent, "growth_weight", 0.0),
            _extract(intent, "profitability_weight", 0.0),
            _extract(intent, "innovation_weight", 0.0),
            _extract(intent, "stability_weight", 0.0),
        ]
        alignment = _average(weights, default=0.45)

    score = _clamp(alignment)
    confidence = 0.60
    rationale = (
        f"Intent alignment estimated at {score:.2f}. "
        "Higher alignment supports more consistent decision making."
    )

    if decisions:
        consistent_choices = sum(
            1 for decision in decisions
            if _extract(decision, "intent_alignment", score) >= 0.5
        )
        ratio = consistent_choices / max(len(decisions), 1)
        score = _clamp((score * 0.6) + (ratio * 0.4))
        confidence = 0.70
        rationale += f" {ratio:.0%} of recent decisions aligned with intent."

    return MetaScore(
        dimension=MetaDimension.INTENT,
        score=score,
        confidence=confidence,
        rationale=rationale,
    )


def evaluate_agents(agents: Optional[List[Any]] = None, votes: Optional[List[Any]] = None) -> MetaScore:
    if not agents:
        rationale = "Executive agent configuration unavailable."
        return MetaScore(dimension=MetaDimension.AGENTS, score=0.25, confidence=0.25, rationale=rationale)

    weights = [_extract(agent, "vote_weight", 1.0) for agent in agents]
    spread = max(weights) - min(weights) if weights else 0.0
    diversity = 1.0 - _clamp(spread / max(max(weights), 1.0))
    score = 0.5 + (diversity * 0.3)
    confidence = 0.60
    rationale = f"Agent weight diversity is {diversity:.2f}. "

    if votes:
        support_levels = [_extract(vote, "score", 0.0) for vote in votes]
        consensus = _average(support_levels, default=0.5)
        score = _clamp((score * 0.5) + (consensus * 0.5))
        confidence = 0.70
        rationale += f"Consensus score is {consensus:.2f}."
    else:
        rationale += "No decision vote history was available."

    return MetaScore(
        dimension=MetaDimension.AGENTS,
        score=score,
        confidence=confidence,
        rationale=rationale,
    )


def evaluate_autonomous(cycles: Optional[List[Any]] = None, metrics: Optional[Any] = None) -> MetaScore:
    if metrics is not None:
        volatility = _extract(metrics, "evolution_score_volatility", 0.5)
        total_cycles = _extract(metrics, "total_cycles_executed", 0)
        average_gain = _extract(metrics, "total_evolution_score_change", 0.0) / max(total_cycles, 1)
        score = _clamp(0.5 + (average_gain * 0.2) - (volatility * 0.3))
        confidence = 0.70
        rationale = (
            f"Autonomous metrics show {total_cycles} cycles with volatility {volatility:.2f}. "
            "Stable positive evolution supports autonomy."
        )
        return MetaScore(dimension=MetaDimension.AUTONOMOUS, score=score, confidence=confidence, rationale=rationale)

    if not cycles:
        return MetaScore(
            dimension=MetaDimension.AUTONOMOUS,
            score=0.30,
            confidence=0.30,
            rationale="No autonomous cycle history available.",
        )

    changes = [_extract(cycle, "evolution_score_change", 0.0) for cycle in cycles]
    avg_change = _average(changes)
    volatility = _average([abs(change - avg_change) for change in changes])
    score = _clamp(0.5 + (avg_change * 0.15) - (volatility * 0.1))
    return MetaScore(
        dimension=MetaDimension.AUTONOMOUS,
        score=score,
        confidence=0.65,
        rationale=(
            f"Average cycle change {avg_change:.3f} with volatility {volatility:.3f}. "
            "Higher stability increases trust in autonomous operations."
        ),
    )


def evaluate_frontier(frontier: Optional[Any] = None, summary: Optional[Dict[str, Any]] = None) -> MetaScore:
    if summary is not None:
        health = _extract(summary, "frontier_quality", 0.6)
        convexity = _extract(summary, "convexity_ratio", 0.5)
        score = _clamp((health * 0.6) + (convexity * 0.4))
        confidence = 0.65
        rationale = f"Frontier health {health:.2f} and convexity {convexity:.2f}."
        return MetaScore(dimension=MetaDimension.FRONTIER, score=score, confidence=confidence, rationale=rationale)

    if not frontier:
        return MetaScore(
            dimension=MetaDimension.FRONTIER,
            score=0.35,
            confidence=0.35,
            rationale="Frontier data unavailable.",
        )

    frontier_health = _extract(frontier, "quality_score", None)
    score = _clamp(frontier_health if frontier_health is not None else 0.5)
    return MetaScore(
        dimension=MetaDimension.FRONTIER,
        score=score,
        confidence=0.60,
        rationale="Frontier health was estimated from available frontier metrics.",
    )


def evaluate_consciousness(consciousness: Optional[Any] = None) -> MetaScore:
    if not consciousness:
        return MetaScore(
            dimension=MetaDimension.CONSCIOUSNESS,
            score=0.30,
            confidence=0.30,
            rationale="Consciousness state unavailable.",
        )

    alignment = _extract(consciousness, "alignment_score", 0.5)
    authenticity = _extract(consciousness, "authenticity_score", 0.5)
    score = _clamp((alignment * 0.6) + (authenticity * 0.4))
    return MetaScore(
        dimension=MetaDimension.CONSCIOUSNESS,
        score=score,
        confidence=0.65,
        rationale=f"Alignment {alignment:.2f} and authenticity {authenticity:.2f} indicate coherence.",
    )


def evaluate_evolution(state: Optional[Any] = None, history: Optional[List[Any]] = None) -> MetaScore:
    if not state:
        return MetaScore(
            dimension=MetaDimension.EVOLUTION,
            score=0.30,
            confidence=0.30,
            rationale="Evolution state unavailable.",
        )

    momentum = _extract(state, "momentum", 0.4)
    stability = _extract(state, "stability", 0.5)
    score = _clamp((momentum * 0.55) + (stability * 0.45))
    rationale = f"Momentum {momentum:.2f}, stability {stability:.2f}."
    if history:
        recent_phase = _extract(history[0], "current_phase", None)
        if recent_phase:
            rationale += f" Recent phase is {recent_phase}."
    return MetaScore(dimension=MetaDimension.EVOLUTION, score=score, confidence=0.60, rationale=rationale)


def evaluate_narrative(narratives: Optional[List[Any]] = None) -> MetaScore:
    if not narratives:
        return MetaScore(
            dimension=MetaDimension.NARRATIVE,
            score=0.35,
            confidence=0.35,
            rationale="Narrative history unavailable.",
        )

    diversity = len({_extract(narrative, "audience", "unknown") for narrative in narratives}) / max(len(narratives), 1)
    score = _clamp(0.4 + (diversity * 0.4))
    rationale = f"Narrative audience diversity is {diversity:.2f}."
    return MetaScore(dimension=MetaDimension.NARRATIVE, score=score, confidence=0.55, rationale=rationale)


def evaluate_memory(memory_summary: Optional[Any] = None) -> MetaScore:
    if not memory_summary:
        return MetaScore(
            dimension=MetaDimension.MEMORY,
            score=0.40,
            confidence=0.40,
            rationale="Memory summary unavailable.",
        )

    types = _extract(memory_summary, "memory_types", {}) or {}
    total = sum(types.values())
    if total <= 0:
        return MetaScore(
            dimension=MetaDimension.MEMORY,
            score=0.45,
            confidence=0.45,
            rationale="No recorded memory distribution available.",
        )

    dominant = max(types.values()) / total
    freshness = min(1.0, _extract(memory_summary, "memories_this_month", 0) / max(total, 1))
    score = _clamp((1.0 - dominant) * 0.6 + freshness * 0.4)
    rationale = (
        f"Memory dominant type share is {dominant:.2f}. "
        f"Recent memory freshness is {freshness:.2f}."
    )
    return MetaScore(dimension=MetaDimension.MEMORY, score=score, confidence=0.60, rationale=rationale)


def detect_biases(scores: List[MetaScore], data_sources: Optional[Dict[str, Any]] = None) -> List[MetaBias]:
    data_sources = data_sources or {}
    source_memory = data_sources.get("memory_summary")

    intent_score = next((s.score for s in scores if s.dimension == MetaDimension.INTENT), 0.0)
    agents_score = next((s.score for s in scores if s.dimension == MetaDimension.AGENTS), 0.0)
    narrative_score = next((s.score for s in scores if s.dimension == MetaDimension.NARRATIVE), 0.0)
    frontier_score = next((s.score for s in scores if s.dimension == MetaDimension.FRONTIER), 0.0)
    memory_score = next((s.score for s in scores if s.dimension == MetaDimension.MEMORY), 0.0)

    biases: List[MetaBias] = []

    if agents_score > 0.75 and intent_score < 0.50:
        biases.append(MetaBias(
            name="現場ドリブン過多",
            description="エージェント依存は高いが、企業意思との整合性が低い。",
            severity=_clamp((agents_score - intent_score) * 0.8),
            affected_dimensions=[MetaDimension.AGENTS, MetaDimension.INTENT],
        ))

    if narrative_score > 0.75 and frontier_score < 0.50:
        biases.append(MetaBias(
            name="語り先行",
            description="ナラティブが強い一方でフロンティア最適化への実装が弱い。",
            severity=_clamp((narrative_score - frontier_score) * 0.8),
            affected_dimensions=[MetaDimension.NARRATIVE, MetaDimension.FRONTIER],
        ))

    if source_memory and isinstance(source_memory, dict):
        types = source_memory.get("memory_types", {})
        total = sum(types.values())
        if total > 0:
            dominant = max(types.values()) / total
            if dominant > 0.75:
                biases.append(MetaBias(
                    name="成功バイアス",
                    description="記憶が特定のタイプに偏っており、失敗や多様な学習が反映されていない。",
                    severity=_clamp((dominant - 0.75) * 2.0),
                    affected_dimensions=[MetaDimension.MEMORY],
                ))

    if next((s.score for s in scores if s.dimension == MetaDimension.AUTONOMOUS), 0.0) > 0.80 and frontier_score < 0.45:
        biases.append(MetaBias(
            name="過度な自動化依存",
            description="自律ループは強いが、フロンティア最適化の実効性に懸念がある。",
            severity=_clamp(0.6 + (0.4 - frontier_score)),
            affected_dimensions=[MetaDimension.AUTONOMOUS, MetaDimension.FRONTIER],
        ))

    return biases


def generate_recommendations(scores: List[MetaScore], biases: List[MetaBias]) -> List[str]:
    recommendations: List[str] = []
    overall = _average([score.score for score in scores], default=0.0)
    if overall < 0.55:
        recommendations.append("Intent とエージェント判断の整合性を再評価し、ガードレールを強化してください。")
    else:
        recommendations.append("現在の評価は概ね安定していますが、定期的な再評価を継続してください。")

    for bias in biases:
        if bias.name == "現場ドリブン過多":
            recommendations.append("意思決定における企業意思の重みを引き上げ、役割間のバランスを改善してください。")
        if bias.name == "語り先行":
            recommendations.append("ナラティブ戦略をフロンティア実行計画と連携させ、実現可能性を確認してください。")
        if bias.name == "成功バイアス":
            recommendations.append("失敗やリスクイベントの記録を増やし、学習データの偏りを低減してください。")
        if bias.name == "過度な自動化依存":
            recommendations.append("自律ループの結果を定期的に検証し、人間の監督を組み込みましょう。")

    if not biases:
        recommendations.append("バイアスは検出されませんでした。継続的なモニタリングを維持してください。")

    return recommendations


def build_meta_cognition_report(
    intent: Optional[Any] = None,
    agents: Optional[List[Any]] = None,
    autonomous_history: Optional[List[Any]] = None,
    autonomous_metrics: Optional[Any] = None,
    frontier: Optional[Any] = None,
    frontier_summary: Optional[Dict[str, Any]] = None,
    consciousness: Optional[Any] = None,
    evolution_state: Optional[Any] = None,
    evolution_history: Optional[List[Any]] = None,
    narratives: Optional[List[Any]] = None,
    memory_summary: Optional[Any] = None,
) -> MetaCognitionReport:
    scores = [
        evaluate_intent(intent, decisions=None, frontier=frontier),
        evaluate_agents(agents),
        evaluate_autonomous(autonomous_history, autonomous_metrics),
        evaluate_frontier(frontier, frontier_summary),
        evaluate_consciousness(consciousness),
        evaluate_evolution(evolution_state, evolution_history),
        evaluate_narrative(narratives),
        evaluate_memory(memory_summary),
    ]

    biases = detect_biases(scores, {"memory_summary": memory_summary})
    overall = _average([s.score for s in scores])
    recommendations = generate_recommendations(scores, biases)

    return MetaCognitionReport(
        overall_score=overall,
        scores=scores,
        biases=biases,
        recommendations=recommendations,
        timestamp=datetime.utcnow(),
    )


class MetaCognitionEngine:
    """Engine wrapper for the meta-cognition service."""

    def build_meta_cognition_report(
        self,
        intent: Optional[Any] = None,
        agents: Optional[List[Any]] = None,
        autonomous_history: Optional[List[Any]] = None,
        autonomous_metrics: Optional[Any] = None,
        frontier: Optional[Any] = None,
        frontier_summary: Optional[Dict[str, Any]] = None,
        consciousness: Optional[Any] = None,
        evolution_state: Optional[Any] = None,
        evolution_history: Optional[List[Any]] = None,
        narratives: Optional[List[Any]] = None,
        memory_summary: Optional[Any] = None,
    ) -> MetaCognitionReport:
        return build_meta_cognition_report(
            intent=intent,
            agents=agents,
            autonomous_history=autonomous_history,
            autonomous_metrics=autonomous_metrics,
            frontier=frontier,
            frontier_summary=frontier_summary,
            consciousness=consciousness,
            evolution_state=evolution_state,
            evolution_history=evolution_history,
            narratives=narratives,
            memory_summary=memory_summary,
        )
