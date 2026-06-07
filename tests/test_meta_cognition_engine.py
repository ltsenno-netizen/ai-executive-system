"""
Tests for the Meta-Cognition engine.
"""

from src.backend.app.models.meta_cognition_model import MetaDimension, MetaScore
from src.backend.app.services.meta_cognition_engine import (
    build_meta_cognition_report,
    detect_biases,
    evaluate_intent,
    evaluate_agents,
    evaluate_autonomous,
    evaluate_frontier,
    evaluate_consciousness,
    evaluate_evolution,
    evaluate_narrative,
    evaluate_memory,
)


def test_evaluate_intent_with_alignment():
    intent = {"alignment_score": 0.85}
    score = evaluate_intent(intent)

    assert score.dimension == MetaDimension.INTENT
    assert score.score >= 0.8
    assert "alignment" in score.rationale.lower()


def test_detect_biases_agents_high_intent_low():
    scores = [
        MetaScore(dimension=MetaDimension.INTENT, score=0.30, confidence=0.60, rationale="Low intent."),
        MetaScore(dimension=MetaDimension.AGENTS, score=0.85, confidence=0.70, rationale="Strong agent influence."),
        MetaScore(dimension=MetaDimension.NARRATIVE, score=0.40, confidence=0.50, rationale=""),
        MetaScore(dimension=MetaDimension.FRONTIER, score=0.60, confidence=0.50, rationale=""),
        MetaScore(dimension=MetaDimension.AUTONOMOUS, score=0.50, confidence=0.50, rationale=""),
        MetaScore(dimension=MetaDimension.CONSCIOUSNESS, score=0.50, confidence=0.50, rationale=""),
        MetaScore(dimension=MetaDimension.EVOLUTION, score=0.50, confidence=0.50, rationale=""),
        MetaScore(dimension=MetaDimension.MEMORY, score=0.50, confidence=0.50, rationale=""),
    ]

    biases = detect_biases(scores, {})
    assert any(b.name == "現場ドリブン過多" for b in biases)


def test_build_meta_cognition_report_returns_full_report():
    report = build_meta_cognition_report(
        intent={"alignment_score": 0.9},
        agents=[{"vote_weight": 1.2}, {"vote_weight": 0.8}],
        autonomous_history=[{"evolution_score_change": 0.05}, {"evolution_score_change": 0.02}],
        frontier={"quality_score": 0.7},
        consciousness={"alignment_score": 0.8, "authenticity_score": 0.7},
        evolution_state={"momentum": 0.6, "stability": 0.7},
        narratives=[{"audience": "INVESTORS"}, {"audience": "EMPLOYEES"}],
        memory_summary={"memory_types": {"DECISION": 5, "REVIEW": 1}, "memories_this_month": 2},
    )

    assert report.overall_score >= 0.0
    assert len(report.scores) == 8
    assert isinstance(report.recommendations, list)
    assert report.timestamp is not None
