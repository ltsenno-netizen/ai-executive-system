import json
import os
from typing import Optional, Dict, Any
from datetime import datetime

from src.backend.app.services.enterprise_evolution_engine import EnterpriseEvolutionEngine
from src.backend.app.models.enterprise_evolution_model import EnterpriseEvolutionResult
from src.backend.app.models.culture_model import CultureProfile
from src.backend.app.models.external_environment_model_v2 import ExternalEnvironmentState

class EnterpriseEvolutionService:
    """Service for managing enterprise evolution cycles and data persistence."""

    def __init__(self, data_dir: str = "data/evolution"):
        self.data_dir = data_dir
        self.engine = EnterpriseEvolutionEngine()
        os.makedirs(self.data_dir, exist_ok=True)

    def run_and_save_evolution(self, period: Optional[str] = None) -> EnterpriseEvolutionResult:
        """
        Run a complete evolution cycle and save the results.
        """
        if period is None:
            period = self._generate_period_string()

        # Get current state (placeholder implementations)
        culture = self._get_current_culture()
        environment = self._get_current_environment()
        leadership = self._get_current_leadership()

        # Compute evolution
        result = self.engine.compute_enterprise_evolution(
            culture=culture,
            environment=environment,
            leadership=leadership,
            period=period
        )

        # Save result
        self._save_evolution_result(result)

        return result

    def get_latest_evolution(self) -> Optional[EnterpriseEvolutionResult]:
        """Get the most recent evolution result."""
        files = [f for f in os.listdir(self.data_dir) if f.endswith('.json')]
        if not files:
            return None

        # Sort by timestamp (assuming filename format: evolution_YYYY-MM-DD_HH-MM-SS.json)
        files.sort(reverse=True)
        latest_file = files[0]

        return self._load_evolution_result(latest_file)

    def get_evolution_by_period(self, period: str) -> Optional[EnterpriseEvolutionResult]:
        """Get evolution result for a specific period."""
        # Look for files containing the period
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json') and period in filename:
                result = self._load_evolution_result(filename)
                if result and result.period == period:
                    return result
        return None

    def _get_current_culture(self) -> CultureProfile:
        """Get current culture state (placeholder)."""
        # In a real implementation, this would fetch from culture service
        return CultureProfile(
            period="2024-Q1",
            aggressiveness_culture=0.6,
            risk_aversion_culture=0.4,
            brand_culture=0.7,
            cost_culture=0.5,
            people_culture=0.8,
            execution_culture=0.6,
            innovation_culture=0.7,
            stability_culture=0.6
        )

    def _get_current_environment(self) -> ExternalEnvironmentState:
        """Get current environment state (placeholder)."""
        # In a real implementation, this would fetch from environment service
        return ExternalEnvironmentState(
            period="2024-Q1",
            economic_pressure=0.4,
            market_volatility=0.5,
            competitive_intensity=0.6,
            regulatory_pressure=0.3,
            technological_disruption=0.7,
            active_events=[],
            active_shocks=[]
        )

    def _get_current_leadership(self) -> ExecutiveTeam:
        """Get current leadership state (placeholder)."""
        # In a real implementation, this would fetch from executive team service
        # For now, return a mock object with required attributes
        class MockExecutiveTeam:
            def __init__(self):
                self.innovation_focus = 0.6
                self.risk_appetite = 0.5
                self.team_cohesion = 0.7

        return MockExecutiveTeam()

    def _generate_period_string(self) -> str:
        """Generate a period string based on current date."""
        now = datetime.now()
        return f"{now.year}-Q{(now.month-1)//3 + 1}"

    def _save_evolution_result(self, result: EnterpriseEvolutionResult):
        """Save evolution result to JSON file."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"evolution_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)

    def _load_evolution_result(self, filename: str) -> Optional[EnterpriseEvolutionResult]:
        """Load evolution result from JSON file."""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return EnterpriseEvolutionResult(**data)
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            return None