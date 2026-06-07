import random
from typing import Optional
from ..models.external_environment_model_v2 import (
    ExternalEnvironmentState,
    PESTFactors,
    CompetitorAction,
    MarketShock,
)


def build_external_environment_state(
    period: str,
    previous_state: Optional[ExternalEnvironmentState]
) -> ExternalEnvironmentState:
    # Initialize PEST factors
    if previous_state:
        political = previous_state.pest.political
        economic = previous_state.pest.economic + random.uniform(-0.05, 0.05)
        social = previous_state.pest.social + random.uniform(-0.02, 0.02)
        technological = previous_state.pest.technological + 0.01

        pest = PESTFactors(
            political=max(0.0, min(1.0, political)),
            economic=max(0.0, min(1.0, economic)),
            social=max(0.0, min(1.0, social)),
            technological=max(0.0, min(1.0, technological)),
        )
    else:
        pest = PESTFactors(
            political=0.5,
            economic=0.5,
            social=0.5,
            technological=0.3,
        )

    # Generate competitor actions
    competitors = [
        CompetitorAction(
            competitor_name="Competitor A",
            aggressiveness=random.uniform(0.0, 1.0),
            market_share_shift=random.uniform(-0.05, 0.05),
            notes="Random action"
        ),
        CompetitorAction(
            competitor_name="Competitor B",
            aggressiveness=random.uniform(0.0, 1.0),
            market_share_shift=random.uniform(-0.05, 0.05),
            notes="Random action"
        ),
    ]

    # Generate market shocks randomly
    shocks = []
    if random.random() < 0.1:  # 10% chance of shock
        shock_types = ["recession", "currency", "trend_shift"]
        shock_type = random.choice(shock_types)
        severity = random.uniform(0.1, 0.5)
        duration = random.randint(1, 6)
        description = f"{shock_type} with severity {severity:.2f}"
        shocks.append(MarketShock(
            shock_type=shock_type,
            severity=severity,
            duration_months=duration,
            description=description
        ))

    # Calculate modifiers
    market_growth_modifier = 0.0
    risk_modifier = 0.0

    # PEST influences
    market_growth_modifier += (pest.economic - 0.5) * 0.1
    market_growth_modifier += (pest.technological - 0.5) * 0.05
    risk_modifier += (pest.political - 0.5) * 0.05

    # Competitor influences
    competitor_agg = sum(c.aggressiveness for c in competitors) / len(competitors)
    market_growth_modifier -= competitor_agg * 0.05
    risk_modifier += competitor_agg * 0.02

    # Shock influences
    for shock in shocks:
        if shock.shock_type == "recession":
            market_growth_modifier -= shock.severity * 0.1
            risk_modifier += shock.severity * 0.05
            pest.political = max(0.0, min(1.0, pest.political - shock.severity * 0.1))
        elif shock.shock_type == "currency":
            market_growth_modifier += shock.severity * 0.05  # Could be positive or negative depending on context
            pest.political = max(0.0, min(1.0, pest.political + shock.severity * 0.05))
        elif shock.shock_type == "trend_shift":
            market_growth_modifier += shock.severity * 0.1
            pest.technological = max(0.0, min(1.0, pest.technological + shock.severity * 0.02))

    return ExternalEnvironmentState(
        period=period,
        pest=pest,
        competitors=competitors,
        shocks=shocks,
        market_growth_modifier=market_growth_modifier,
        risk_modifier=risk_modifier,
    )