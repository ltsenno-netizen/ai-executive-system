"""
Multi-Company Comparative Engine Tests (Step AK)
"""

from src.backend.app.models.multi_company_comparative_model import CompanyId, CompanyProfile
from src.backend.app.services.multi_company_comparative_engine import MultiCompanyComparativeEngine


def test_compute_comparative_metrics():
    """Test metric computation across profiles."""
    engine = MultiCompanyComparativeEngine()
    
    profiles = [
        CompanyProfile(
            company=CompanyId(company_id="company_a", name="Company A"),
            consciousness_clarity=0.8,
            evolution_phase="INTENTIONAL",
            evolution_speed=0.7,
            frontier_health=0.75,
            frontier_score=75.0,
            culture_profile={"innovation": 0.8, "execution": 0.7},
            risk_posture=0.7,
            narrative_consistency=0.8,
            narrative_clarity=0.8,
            meta_cognition_score=0.8,
            scenario_resilience={"RECESSION": 0.7, "TECH_BOOM": 0.9},
            learning_agility=0.8,
        ),
        CompanyProfile(
            company=CompanyId(company_id="company_b", name="Company B"),
            consciousness_clarity=0.5,
            evolution_phase="REACTIVE",
            evolution_speed=0.4,
            frontier_health=0.5,
            frontier_score=50.0,
            culture_profile={"innovation": 0.4, "execution": 0.5},
            risk_posture=0.3,
            narrative_consistency=0.5,
            narrative_clarity=0.5,
            meta_cognition_score=0.5,
            scenario_resilience={"RECESSION": 0.4, "TECH_BOOM": 0.5},
            learning_agility=0.5,
        ),
    ]
    
    metrics = engine.compute_comparative_metrics(profiles)
    
    assert len(metrics) > 0
    assert all(hasattr(m, 'best_company_id') for m in metrics)
    assert all(hasattr(m, 'values') for m in metrics)
    
    # Check consciousness clarity metric
    clarity_metric = [m for m in metrics if m.metric_id == "consciousness_clarity"][0]
    assert clarity_metric.best_company_id == "company_a"
    assert clarity_metric.worst_company_id == "company_b"
    assert clarity_metric.best_value == 0.8
    assert clarity_metric.worst_value == 0.5


def test_cluster_companies():
    """Test company clustering/archetype classification."""
    engine = MultiCompanyComparativeEngine()
    
    profiles = [
        CompanyProfile(
            company=CompanyId(company_id="aggressive", name="Aggressive Corp"),
            consciousness_clarity=0.7,
            evolution_phase="EMERGENT",
            evolution_speed=0.75,
            frontier_health=0.8,
            frontier_score=80.0,
            culture_profile={},
            risk_posture=0.8,
            narrative_consistency=0.7,
            narrative_clarity=0.7,
            meta_cognition_score=0.7,
            scenario_resilience={},
            learning_agility=0.8,
        ),
        CompanyProfile(
            company=CompanyId(company_id="stable", name="Stable Inc"),
            consciousness_clarity=0.6,
            evolution_phase="INTENTIONAL",
            evolution_speed=0.4,
            frontier_health=0.5,
            frontier_score=50.0,
            culture_profile={},
            risk_posture=0.2,
            narrative_consistency=0.8,
            narrative_clarity=0.8,
            meta_cognition_score=0.6,
            scenario_resilience={},
            learning_agility=0.5,
        ),
    ]
    
    clusters = engine.cluster_companies(profiles)
    
    assert len(clusters) > 0
    assert any(c.cluster_id == "aggressive_innovator" for c in clusters)
    assert any(c.cluster_id == "stable_operator" for c in clusters)


def test_build_dimension_analyses():
    """Test dimension-level analysis."""
    engine = MultiCompanyComparativeEngine()
    
    profiles = [
        CompanyProfile(
            company=CompanyId(company_id="a", name="A"),
            consciousness_clarity=0.8,
            evolution_phase="INTENTIONAL",
            evolution_speed=0.7,
            frontier_health=0.75,
            frontier_score=75.0,
            culture_profile={},
            risk_posture=0.7,
            narrative_consistency=0.8,
            narrative_clarity=0.8,
            meta_cognition_score=0.8,
            scenario_resilience={},
            learning_agility=0.8,
        ),
    ]
    
    metrics = engine.compute_comparative_metrics(profiles)
    dimensions = engine.build_dimension_analyses(profiles, metrics)
    
    assert len(dimensions) > 0
    assert any(d.dimension == "Consciousness" for d in dimensions)
    assert any(d.dimension == "Evolution" for d in dimensions)
    assert any(d.dimension == "Frontier" for d in dimensions)


def test_build_comparison_report():
    """Test full report generation."""
    engine = MultiCompanyComparativeEngine()
    
    company_ids = [
        CompanyId(company_id="a", name="Company A"),
        CompanyId(company_id="b", name="Company B"),
    ]
    
    profiles = [
        CompanyProfile(
            company=cid,
            consciousness_clarity=0.6 + (i * 0.2),
            evolution_phase="INTENTIONAL",
            evolution_speed=0.5 + (i * 0.2),
            frontier_health=0.6 + (i * 0.2),
            frontier_score=60.0 + (i * 20),
            culture_profile={},
            risk_posture=0.5 + (i * 0.2),
            narrative_consistency=0.6 + (i * 0.2),
            narrative_clarity=0.6 + (i * 0.2),
            meta_cognition_score=0.6 + (i * 0.2),
            scenario_resilience={},
            learning_agility=0.6 + (i * 0.2),
        )
        for i, cid in enumerate(company_ids)
    ]
    
    report = engine.build_comparison_report(company_ids, profiles)
    
    assert report.report_id is not None
    assert len(report.companies) == 2
    assert len(report.metrics) > 0
    assert len(report.clusters) > 0
    assert len(report.dimensions) > 0
    assert len(report.narrative_summary) > 0
    assert len(report.strategic_implications) > 0
