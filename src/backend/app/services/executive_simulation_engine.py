import uuid
from datetime import datetime
from typing import List, Optional

from ..models.executive_simulation_model import (
    ExecutiveRole,
    ExecutiveStance,
    ExecutiveComment,
    ExecutiveVote,
    ExecutiveSimulationInput,
    ExecutiveSimulationResult,
    StrategyBundle,
)
from ..models.meta_cognition_model import MetaCognitionReport
from ..models.multi_company_comparative_model import MultiCompanyComparisonReport
from ..models.scenario_simulation_model import ScenarioSimulationResult


def _extract_risk_signals(scenario_result: ScenarioSimulationResult) -> List[str]:
    risks = []
    risk_text = scenario_result.risk_assessment.lower() if scenario_result.risk_assessment else ""
    if "high" in risk_text or "critical" in risk_text or "severe" in risk_text:
        risks.append("Scenario indicates significant downside risk for the business.")
    if scenario_result.financial_impact_summary.get("profit", 0.0) < 0:
        risks.append("Projected profits are negative in the scenario outlook.")
    if scenario_result.financial_impact_summary.get("cash", 0.0) < 0:
        risks.append("Cash pressure is expected under this scenario.")
    return risks


def _extract_opportunity_signals(scenario_result: ScenarioSimulationResult) -> List[str]:
    opportunities = []
    opp_text = scenario_result.opportunity_assessment.lower() if scenario_result.opportunity_assessment else ""
    if "growth" in opp_text or "expand" in opp_text or "market" in opp_text:
        opportunities.append("The scenario presents growth and market expansion opportunities.")
    if scenario_result.financial_impact_summary.get("revenue", 0.0) > 0:
        opportunities.append("Revenue upside is available if execution remains disciplined.")
    return opportunities


def _build_role_note(role: ExecutiveRole, strategy_bundle: StrategyBundle) -> str:
    if role == ExecutiveRole.CFO:
        return "Assess the plan through cost, cash, and risk lenses."
    if role == ExecutiveRole.CPO:
        return "Validate product differentiation, roadmap realism, and customer value."
    if role == ExecutiveRole.COO:
        return "Confirm execution feasibility, pacing, and operational readiness."
    if role == ExecutiveRole.CMO:
        return "Judge brand positioning, narrative clarity, and market resonance."
    if role == ExecutiveRole.CHRO:
        return "Focus on people readiness, culture fit, and talent requirements."
    if role == ExecutiveRole.CSO:
        return "Evaluate long-term positioning, strategic coherence, and discontinuities."
    return "Provide the final corporate endorsement and integrated perspective."


def generate_comment_for_role(
    role: ExecutiveRole,
    strategy_bundle: StrategyBundle,
    scenario_result: ScenarioSimulationResult,
    comparison_report: Optional[MultiCompanyComparisonReport],
    meta_report: Optional[MetaCognitionReport],
) -> ExecutiveComment:
    key_points: List[str] = []
    risks: List[str] = []
    opportunities: List[str] = []
    suggested_changes: List[str] = []

    role_note = _build_role_note(role, strategy_bundle)
    key_points.append(role_note)

    if strategy_bundle.executive_summary:
        key_points.append(f"Strategy summary indicates: {strategy_bundle.executive_summary[:120]}")

    scenario_risks = _extract_risk_signals(scenario_result)
    scenario_opps = _extract_opportunity_signals(scenario_result)
    risks.extend(scenario_risks)
    opportunities.extend(scenario_opps)

    if role == ExecutiveRole.CFO:
        if scenario_result.financial_impact_summary.get("cash", 0.0) < 0.2:
            risks.append("Cash runway is tight for this scenario.")
            suggested_changes.append("Reevaluate cost levers and cash conservation measures.")
        if "resilience" in strategy_bundle.context_notes.lower() if strategy_bundle.context_notes else False:
            opportunities.append("There is a clear resilience angle to support financial stability.")
    elif role == ExecutiveRole.CPO:
        if any("product" in d.name.lower() or "feature" in d.name.lower() for d in strategy_bundle.directives):
            opportunities.append("Product and differentiation themes are present in the strategy.")
        else:
            risks.append("The bundle lacks a strong product innovation signal.")
            suggested_changes.append("Add sharper product differentiation or customer value messaging.")
    elif role == ExecutiveRole.COO:
        if scenario_result.confidence < 0.5:
            risks.append("Execution uncertainty is high given scenario volatility.")
            suggested_changes.append("Build clearer operational contingencies.")
        else:
            opportunities.append("Execution confidence is reasonable under current assumptions.")
    elif role == ExecutiveRole.CMO:
        if comparison_report is not None and comparison_report.narrative_summary:
            opportunities.append("Competitive narrative can be sharpened relative to peers.")
        if "brand" not in strategy_bundle.executive_summary.lower():
            risks.append("Brand and positioning are not emphasized enough.")
            suggested_changes.append("Improve strategic framing around brand and customer perception.")
    elif role == ExecutiveRole.CHRO:
        if meta_report is not None and meta_report.overall_score < 0.6:
            risks.append("Team bias and system health concerns may weaken execution.")
            suggested_changes.append("Prioritize people alignment and culture readiness.")
        else:
            opportunities.append("Meta-cognition health is acceptable for change adoption.")
    elif role == ExecutiveRole.CSO:
        if strategy_bundle.executive_summary and "long-term" in strategy_bundle.executive_summary.lower():
            opportunities.append("The bundle includes long-term strategic intent.")
        else:
            risks.append("Long-term positioning is not yet clear.")
            suggested_changes.append("Clarify the multi-year strategic horizon.")

    if comparison_report is not None and not comparison_report.metrics:
        risks.append("The comparative benchmark lacks sufficient metric depth.")

    if len(suggested_changes) == 0 and len(risks) <= len(opportunities):
        opportunities.append("The plan is generally aligned with the current scenario and benchmarks.")

    return ExecutiveComment(
        role=role,
        stance=ExecutiveStance.NEUTRAL,
        key_points=key_points,
        risks=risks,
        opportunities=opportunities,
        suggested_changes=suggested_changes,
    )


def decide_stance_for_role(comment: ExecutiveComment) -> ExecutiveStance:
    risk_count = len(comment.risks)
    opp_count = len(comment.opportunities)
    change_count = len(comment.suggested_changes)

    if change_count >= 2 or (risk_count > opp_count and risk_count >= 2):
        return ExecutiveStance.OPPOSE if risk_count > opp_count * 1.5 else ExecutiveStance.CONCERNED
    if opp_count >= risk_count and change_count == 0:
        return ExecutiveStance.STRONGLY_SUPPORT if opp_count >= risk_count + 2 else ExecutiveStance.SUPPORT
    return ExecutiveStance.NEUTRAL


def compute_consensus_level(votes: List[ExecutiveVote]) -> float:
    mapping = {
        ExecutiveStance.STRONGLY_SUPPORT: 1.0,
        ExecutiveStance.SUPPORT: 0.7,
        ExecutiveStance.NEUTRAL: 0.5,
        ExecutiveStance.CONCERNED: 0.3,
        ExecutiveStance.OPPOSE: 0.0,
    }
    if not votes:
        return 0.0
    return float(sum(mapping[v.stance] for v in votes) / len(votes))


def build_ceo_summary(
    strategy_bundle: StrategyBundle,
    votes: List[ExecutiveVote],
    comments: List[ExecutiveComment],
    consensus: float,
) -> str:
    support_count = sum(1 for vote in votes if vote.stance in {ExecutiveStance.STRONGLY_SUPPORT, ExecutiveStance.SUPPORT})
    oppose_count = sum(1 for vote in votes if vote.stance in {ExecutiveStance.CONCERNED, ExecutiveStance.OPPOSE})
    neutral_count = sum(1 for vote in votes if vote.stance == ExecutiveStance.NEUTRAL)

    summary_lines = [
        f"Overall consensus is {consensus:.2f}, with {support_count} support, {neutral_count} neutral, and {oppose_count} concerned/opposed roles.",
    ]

    main_concerns = [
        f"{c.role.value}: {', '.join(c.risks)}"
        for c in comments
        if c.risks and c.role != ExecutiveRole.CEO
    ]
    if main_concerns:
        summary_lines.append("Primary concerns: " + " | ".join(main_concerns[:3]))

    change_points = [change for c in comments for change in c.suggested_changes]
    if change_points:
        summary_lines.append("Suggested changes: " + "; ".join(change_points[:3]))

    conclusion = "The recommendation should be approved." if consensus >= 0.6 else "The recommendation requires revision before approval."
    summary_lines.append(conclusion)

    if strategy_bundle.recommended_actions:
        summary_lines.append("Next action focus: " + "; ".join(strategy_bundle.recommended_actions[:2]))

    return " \n".join(summary_lines)


class ExecutiveSimulationEngine:
    def run_executive_simulation(
        self,
        sim_input: ExecutiveSimulationInput,
        strategy_bundle: StrategyBundle,
        scenario_result: ScenarioSimulationResult,
        comparison_report: Optional[MultiCompanyComparisonReport],
        meta_report: Optional[MetaCognitionReport],
    ) -> ExecutiveSimulationResult:
        simulation_id = str(uuid.uuid4())
        comments: List[ExecutiveComment] = []
        votes: List[ExecutiveVote] = []

        roles = [
            ExecutiveRole.CEO,
            ExecutiveRole.CFO,
            ExecutiveRole.COO,
            ExecutiveRole.CPO,
            ExecutiveRole.CMO,
            ExecutiveRole.CHRO,
            ExecutiveRole.CSO,
        ]

        for role in roles:
            comment = generate_comment_for_role(role, strategy_bundle, scenario_result, comparison_report, meta_report)
            stance = decide_stance_for_role(comment)
            comment.stance = stance
            comments.append(comment)
            votes.append(ExecutiveVote(role=role, stance=stance, rationale="; ".join(comment.key_points)))

        consensus = compute_consensus_level(votes)
        approved = consensus >= 0.6
        minority_reports = [
            f"{comment.role.value}: {', '.join(comment.key_points)}"
            for comment in comments
            if comment.stance in {ExecutiveStance.CONCERNED, ExecutiveStance.OPPOSE}
        ]
        ceo_summary = build_ceo_summary(strategy_bundle, votes, comments, consensus)

        return ExecutiveSimulationResult(
            simulation_id=simulation_id,
            scenario_type=sim_input.scenario_type,
            strategy_bundle_id=strategy_bundle.directive_id,
            comments=comments,
            votes=votes,
            consensus_level=consensus,
            approved=approved,
            minority_reports=minority_reports,
            ceo_summary=ceo_summary,
            timestamp=datetime.utcnow(),
        )
