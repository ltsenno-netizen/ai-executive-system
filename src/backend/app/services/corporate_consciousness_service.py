"""
Corporate Consciousness Service (Step AE)

Service layer for managing corporate consciousness lifecycle:
- Consciousness generation and updates
- State persistence and retrieval
- Dashboard integration
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime

from ..models.corporate_consciousness_model import (
    CorporateConsciousness,
    ConsciousnessDashboardSummary,
)
from ..models.corporate_intent_model import CorporateIntent
from ..models.executive_agent_model import ExecutiveAgentConfig
from .consciousness_engine import ConsciousnessEngine
from .corporate_intent_service import CorporateIntentService
from .executive_agent_service import ExecutiveAgentService
from .frontier_optimization_service import FrontierOptimizationService
from .culture_service import CultureService
from .external_environment_service_v2 import ExternalEnvironmentServiceV2
from .autonomous_enterprise_service import AutonomousEnterpriseService


class CorporateConsciousnessService:
    """Service for managing corporate consciousness"""

    def __init__(self):
        self.engine = ConsciousnessEngine()
        self.intent_service = CorporateIntentService()
        self.agent_service = ExecutiveAgentService()
        self.frontier_service = FrontierOptimizationService()
        self.culture_service = CultureService()
        self.environment_service = ExternalEnvironmentServiceV2()
        self.autonomous_service = AutonomousEnterpriseService()
        
        self.consciousness_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/consciousness')
        )
        os.makedirs(self.consciousness_dir, exist_ok=True)
        
        self._consciousness_cache: Dict[str, CorporateConsciousness] = {}

    def generate_consciousness(
        self,
        period: str,
        company_name: str,
        company_history: Optional[Dict] = None,
    ) -> CorporateConsciousness:
        """
        Generate corporate consciousness for the given period.

        Args:
            period: Current period (e.g., "2026-01")
            company_name: Name of the enterprise
            company_history: Optional company history data

        Returns:
            CorporateConsciousness: Generated consciousness model
        """
        # Get all required inputs
        intent = self.intent_service.get_intent()
        agents = self.agent_service.get_default_agents()
        
        frontier_health = self.frontier_service.get_frontier_health_score()
        
        culture = None
        try:
            culture = self.culture_service.get_latest_culture()
        except Exception:
            pass
        
        environment = None
        try:
            env_service_obj = self.environment_service.get_environment(period)
            if env_service_obj:
                environment = {
                    "economic": getattr(env_service_obj.pest, "economic", 0.5),
                    "competitors": len(getattr(env_service_obj, "competitors", [])),
                    "shocks": len(getattr(env_service_obj, "shocks", [])),
                }
        except Exception:
            pass
        
        current_cycle = None
        try:
            current_cycle = self.autonomous_service.get_latest_cycle()
        except Exception:
            pass

        # Generate consciousness
        consciousness = self.engine.generate_corporate_consciousness(
            intent=intent,
            agents=agents,
            frontier_analysis=None,  # Optional for now
            frontier_health=frontier_health,
            culture=culture,
            company_history=company_history,
            environment=environment,
            current_cycle=current_cycle,
            period=period,
            company_name=company_name,
        )

        # Cache and persist
        self._consciousness_cache[period] = consciousness
        self._save_consciousness(consciousness)

        return consciousness

    def get_consciousness(self, period: str) -> Optional[CorporateConsciousness]:
        """Get consciousness for a specific period"""
        if period in self._consciousness_cache:
            return self._consciousness_cache[period]
        
        try:
            consciousness_file = os.path.join(
                self.consciousness_dir, f"consciousness_{period}.json"
            )
            if os.path.exists(consciousness_file):
                with open(consciousness_file, "r") as f:
                    data = json.load(f)
                    # Reconstruct model (would need full deserialization in production)
                    return None  # Simplified for now
        except Exception:
            pass
        
        return None

    def get_latest_consciousness(self) -> Optional[CorporateConsciousness]:
        """Get most recent consciousness"""
        try:
            files = sorted(
                [f for f in os.listdir(self.consciousness_dir) if f.startswith("consciousness_")],
                reverse=True
            )
            if files:
                latest_file = os.path.join(self.consciousness_dir, files[0])
                with open(latest_file, "r") as f:
                    data = json.load(f)
                    # Simplified deserialization
                    return None
        except Exception:
            pass
        
        return None

    def get_consciousness_summary(
        self, period: str
    ) -> Optional[ConsciousnessDashboardSummary]:
        """
        Get dashboard summary of consciousness.

        Returns simplified summary suitable for dashboard display.
        """
        consciousness = self.get_consciousness(period)
        
        if not consciousness:
            # Generate fresh if needed
            consciousness = self.generate_consciousness(period, "AI Executive System")
        
        if not consciousness:
            return None
        
        self_model = consciousness.self_model
        stmt = consciousness.consciousness_statement
        
        return ConsciousnessDashboardSummary(
            consciousness_id=consciousness.consciousness_id,
            period=consciousness.period,
            identity_statement=self_model.identity_statement.core_identity,
            purpose_statement=self_model.purpose_statement.mission,
            strategic_direction=self_model.strategic_direction.primary_strategy,
            current_phase=self_model.evolution_trajectory.current_phase_name,
            next_phase=self_model.evolution_trajectory.next_phase_anticipated,
            overall_score=consciousness.overall_consciousness_score,
            clarity_score=consciousness.clarity_score,
            alignment_score=consciousness.alignment_score,
            top_strengths=self_model.self_assessment.strengths[:3],
            top_challenges=self_model.self_assessment.weaknesses[:3],
            strategic_implications=consciousness.strategic_implications[:2],
            consciousness_statement_summary=stmt.consciousness_summary[:500],
            last_updated=consciousness.updated_at or consciousness.created_at,
        )

    def update_consciousness(
        self,
        period: str,
        company_name: str,
        company_history: Optional[Dict] = None,
    ) -> CorporateConsciousness:
        """
        Update consciousness (regenerate for new data).

        Args:
            period: Current period
            company_name: Enterprise name
            company_history: Updated history if available

        Returns:
            Updated consciousness
        """
        # Invalidate cache
        if period in self._consciousness_cache:
            del self._consciousness_cache[period]
        
        # Regenerate
        return self.generate_consciousness(period, company_name, company_history)

    def _save_consciousness(self, consciousness: CorporateConsciousness) -> None:
        """Save consciousness to JSON"""
        try:
            consciousness_file = os.path.join(
                self.consciousness_dir, f"consciousness_{consciousness.period}.json"
            )
            with open(consciousness_file, "w") as f:
                # Simplified save (would need proper serialization)
                data = {
                    "consciousness_id": consciousness.consciousness_id,
                    "period": consciousness.period,
                    "company_name": consciousness.company_name,
                    "identity_statement": consciousness.self_model.identity_statement.core_identity,
                    "purpose_statement": consciousness.self_model.purpose_statement.mission,
                    "strategic_direction": consciousness.self_model.strategic_direction.primary_strategy,
                    "overall_consciousness_score": consciousness.overall_consciousness_score,
                    "clarity_score": consciousness.clarity_score,
                    "alignment_score": consciousness.alignment_score,
                    "authenticity_score": consciousness.authenticity_score,
                    "created_at": consciousness.created_at.isoformat() if consciousness.created_at else None,
                }
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save consciousness: {e}")

    def get_consciousness_history(self, limit: int = 5) -> List[Dict]:
        """Get history of consciousness generations"""
        try:
            files = sorted(
                [f for f in os.listdir(self.consciousness_dir) if f.startswith("consciousness_")],
                reverse=True
            )[:limit]
            
            history = []
            for file in files:
                filepath = os.path.join(self.consciousness_dir, file)
                try:
                    with open(filepath, "r") as f:
                        data = json.load(f)
                        history.append(data)
                except Exception:
                    pass
            
            return history
        except Exception:
            return []

    def compute_consciousness_metrics(
        self, consciousness: CorporateConsciousness
    ) -> Dict[str, float]:
        """
        Compute comprehensive metrics about consciousness.

        Returns:
            Dict with various quality metrics
        """
        return {
            "overall_consciousness_score": consciousness.overall_consciousness_score,
            "clarity_score": consciousness.clarity_score,
            "coherence_score": consciousness.coherence_score,
            "alignment_score": consciousness.alignment_score,
            "authenticity_score": consciousness.authenticity_score,
            "model_coherence": consciousness.self_model.model_coherence,
            "self_awareness_level": consciousness.self_model.self_awareness_level,
            "identity_confidence": consciousness.self_model.identity_statement.identity_confidence,
            "purpose_clarity": consciousness.self_model.purpose_statement.purpose_clarity_score,
            "direction_confidence": consciousness.self_model.strategic_direction.direction_confidence,
            "adaptability_index": consciousness.self_model.evolution_trajectory.adaptability_index,
            "resilience_index": consciousness.self_model.evolution_trajectory.resilience_index,
        }

    def export_consciousness_markdown(
        self, consciousness: CorporateConsciousness
    ) -> str:
        """Export consciousness as markdown for reporting"""
        self_model = consciousness.self_model
        stmt = consciousness.consciousness_statement
        
        md = f"""# Corporate Consciousness Report
**Period:** {consciousness.period}
**Company:** {consciousness.company_name}

## Overall Consciousness Score: {consciousness.overall_consciousness_score:.1%}

---

## Identity Statement
**Core Identity:** {self_model.identity_statement.core_identity}

**Archetype:** {self_model.identity_statement.cultural_archetype}

**Brand Promise:** {self_model.identity_statement.brand_promise}

**Identity Confidence:** {self_model.identity_statement.identity_confidence:.1%}

---

## Purpose Statement
**Mission:** {self_model.purpose_statement.mission}

**Vision:** {self_model.purpose_statement.vision}

**Purpose Clarity:** {self_model.purpose_statement.purpose_clarity_score:.1%}

**Purpose Alignment:** {self_model.purpose_statement.purpose_alignment_score:.1%}

---

## Strategic Direction
**Primary Strategy:** {self_model.strategic_direction.primary_strategy}

**Growth Vector:** {self_model.strategic_direction.growth_vector}

**Competitive Position:** {self_model.strategic_direction.competitive_positioning}

**Time Horizon:** {self_model.strategic_direction.time_horizon}

**Direction Confidence:** {self_model.strategic_direction.direction_confidence:.1%}

### Strategic Focus Areas
{chr(10).join(f"- {area}" for area in self_model.strategic_direction.strategic_focus_areas)}

---

## Self-Assessment
**Overall Health:** {self_model.self_assessment.overall_health:.1%}

**Maturity Level:** {self_model.self_assessment.maturity_level}

### Strengths
{chr(10).join(f"- {s}" for s in self_model.self_assessment.strengths)}

### Weaknesses
{chr(10).join(f"- {w}" for w in self_model.self_assessment.weaknesses)}

### Opportunities
{chr(10).join(f"- {o}" for o in self_model.self_assessment.opportunities)}

### Threats
{chr(10).join(f"- {t}" for t in self_model.self_assessment.threats)}

---

## Evolution Trajectory
**Current Phase:** {self_model.evolution_trajectory.current_phase_name}

**Next Phase:** {self_model.evolution_trajectory.next_phase_anticipated}

**Evolutionary Momentum:** {self_model.evolution_trajectory.evolutionary_momentum:+.1f}

**Adaptability:** {self_model.evolution_trajectory.adaptability_index:.1%}

**Resilience:** {self_model.evolution_trajectory.resilience_index:.1%}

---

## Consciousness Statement
{stmt.consciousness_summary}

---

## Strategic Implications
{chr(10).join(f"- {impl}" for impl in consciousness.strategic_implications)}

## Required Actions
{chr(10).join(f"- {action}" for action in consciousness.required_actions)}

## Growth Opportunities
{chr(10).join(f"- {opp}" for opp in consciousness.growth_opportunities)}

---

## Quality Metrics
- **Authenticity:** {consciousness.authenticity_score:.1%}
- **Clarity:** {consciousness.clarity_score:.1%}
- **Coherence:** {consciousness.coherence_score:.1%}
- **Alignment:** {consciousness.alignment_score:.1%}
- **Model Coherence:** {self_model.model_coherence:.1%}
- **Self-Awareness Level:** {self_model.self_awareness_level:.1%}

---
*Generated: {consciousness.created_at.strftime("%Y-%m-%d %H:%M:%S")}*
"""
        return md
