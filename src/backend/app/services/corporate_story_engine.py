from typing import Dict, List
from ..models.corporate_story_model import CorporateStory, CorporateStorySection
from ..models.company_history_model import CompanyHistory
from ..models.culture_model import CultureProfile
from ..models.external_environment_model_v2 import ExternalEnvironmentState
from ..models.ai_ceo_model import AICeoPersona
from ..models.enterprise_evolution_model import EnterpriseEvolutionResult
from ..models.scenario_model import ScenarioResult
from ..models.self_optimization_model import SelfOptimizationPlan


def build_history_section(history: Dict) -> CorporateStorySection:
    """企業の歩み（過去）セクションを構築"""
    
    ceo_transitions = history.get("major_events", [])
    culture_trends = history.get("culture_trends", {})
    evolution_trend = history.get("evolution_trend", 0.0)
    
    # ストーリー文生成
    content = "## 企業の歩み\n\n"
    
    if ceo_transitions:
        content += f"この企業は複数のリーダーシップ転換を経験しており、"
        content += "各段階で異なる経営スタイルと戦略的方向性が展開されてきました。\n\n"
    
    if culture_trends:
        dimensions = list(culture_trends.keys())
        content += f"企業文化は {dimensions[0]} を中心として進化し、"
        content += "組織の価値観と行動様式に深い影響を与えてきました。\n\n"
    
    if evolution_trend > 0:
        content += f"進化スコアは {evolution_trend:.2f} に達しており、"
        content += "企業が環境変化に適応し、継続的に進化していることを示しています。\n\n"
    
    content += "過去の経験は現在の組織基盤を形成し、"
    content += "将来の成長可能性の基礎となっています。"
    
    return CorporateStorySection(
        title="企業の歩み",
        content=content
    )


def build_current_state_section(
    culture: CultureProfile,
    environment: ExternalEnvironmentState,
    executive_team: Dict[str, AICeoPersona],
    evolution: EnterpriseEvolutionResult
) -> CorporateStorySection:
    """現在の姿セクションを構築"""
    
    content = "## 現在の姿\n\n"
    
    # 文化面
    content += "### 組織文化\n"
    content += f"現在の企業文化は、革新性と安定性のバランスを保ち、"
    content += f"進化スコア {evolution.evolution_score:.2f} という水準にあります。\n\n"
    
    # 経営チーム
    content += "### 経営チーム\n"
    roles = list(executive_team.keys())
    if roles:
        content += f"経営チームは {', '.join(roles)} で構成され、"
        content += "多様な専門性と視点を持つメンバーが統括しています。\n\n"
    
    # 環境
    content += "### 外部環境\n"
    pest = environment.pest
    content += f"外部環境は経済 {pest.economic:.2f}、"
    content += f"技術 {pest.technological:.2f}、"
    content += f"社会 {pest.social:.2f} の状況にあり、"
    content += "複数の機会と課題が存在します。\n\n"
    
    # 総評
    content += "企業は現在、安定した基盤の上に、"
    content += "次のステップへの準備ができた状態にあります。"
    
    return CorporateStorySection(
        title="現在の姿",
        content=content
    )


def build_scenario_section(scenarios: List[ScenarioResult]) -> CorporateStorySection:
    """未来の可能性（シナリオ）セクションを構築"""
    
    content = "## 未来の可能性\n\n"
    
    if not scenarios:
        content += "シナリオ分析はまだ実施されていません。\n"
        return CorporateStorySection(title="未来の可能性", content=content)
    
    # シナリオごとのストーリー
    scenario_stories = {
        "baseline": "ベースラインシナリオでは、現在の傾向が継続し、",
        "optimistic": "楽観シナリオでは、好況環境と技術革新が企業成長を加速させ、",
        "pessimistic": "悲観シナリオでは、外部環境の悪化が課題となりますが、",
        "tech_boom": "技術革新シナリオでは、イノベーション能力が最重要となり、",
        "recession": "不況シナリオでは、コスト構造と効率性が経営の鍵となります。"
    }
    
    for scenario in scenarios:
        scenario_type = scenario.scenario_type.value
        story = scenario_stories.get(scenario_type, f"{scenario_type}シナリオでは")
        evolution = scenario.projected_evolution_score
        revenue = scenario.projected_financials.get("revenue", 0)
        
        content += f"### {scenario_type.upper()}\n"
        content += f"{story}\n"
        content += f"進化スコア {evolution:.2f}、推定売上 {revenue:.1f} に到達する可能性があります。\n\n"
    
    content += "各シナリオは異なるチャレンジと機会をもたらし、"
    content += "企業の戦略選択に重要な示唆を与えます。"
    
    return CorporateStorySection(
        title="未来の可能性",
        content=content
    )


def build_optimization_section(plan: SelfOptimizationPlan) -> CorporateStorySection:
    """最適化の方向性セクションを構築"""
    
    content = "## 最適化の方向性\n\n"
    
    content += f"### 目的：{plan.objective.value.upper()}\n"
    content += f"選択されたシナリオ：{plan.selected_scenario.value}\n\n"
    
    # 戦略
    if plan.recommended_strategies:
        content += "### 推奨戦略\n"
        for i, strategy in enumerate(plan.recommended_strategies[:3], 1):
            content += f"{i}. **{strategy.description}** "
            content += f"(優先度: {strategy.priority}, 効果予測: {strategy.expected_impact:.1%})\n"
        content += "\n"
    
    # 文化シフト
    if plan.recommended_culture_shifts:
        content += "### 文化シフト\n"
        for shift in plan.recommended_culture_shifts[:3]:
            sign = "+" if shift.delta > 0 else ""
            content += f"- {shift.dimension}: {sign}{shift.delta:.2f}\n"
            content += f"  理由: {shift.rationale}\n"
        content += "\n"
    
    # リーダーシップ調整
    if plan.recommended_leadership_changes:
        content += "### リーダーシップ調整\n"
        for change in plan.recommended_leadership_changes[:3]:
            content += f"- {change.role}: {change.suggested_change}\n"
            content += f"  理由: {change.rationale}\n"
        content += "\n"
    
    content += f"期待される進化スコア: {plan.expected_evolution_score:.2f}"
    
    return CorporateStorySection(
        title="最適化の方向性",
        content=content
    )


def build_integrated_narrative_section(
    history: Dict,
    culture: CultureProfile,
    scenarios: List[ScenarioResult],
    plan: SelfOptimizationPlan,
    evolution: EnterpriseEvolutionResult
) -> CorporateStorySection:
    """統合ナラティブセクションを構築"""
    
    content = "## 企業の未来への道\n\n"
    
    # 過去の教訓
    content += "### 過去の教訓\n"
    content += "企業は複数の環境変化とリーダーシップ交代を乗り越えてきました。"
    content += "これらの経験から、組織の適応力と継続性の重要性を学んできています。\n\n"
    
    # 現在の強み
    content += "### 現在の強み\n"
    content += f"進化スコア {evolution.evolution_score:.2f} が示すように、"
    content += "企業は継続的な改善と学習を実現しています。"
    content += "多様な経営陣と柔軟な組織文化が、"
    content += "変化への対応力を高めています。\n\n"
    
    # 未来への方向性
    content += "### 未来への方向性\n"
    content += f"複数シナリオの分析結果、{plan.objective.value} を最大化する方向が最有望です。\n"
    content += f"選択されたシナリオは '{plan.selected_scenario.value}' であり、"
    content += f"期待される進化スコアは {plan.expected_evolution_score:.2f} に達します。\n\n"
    
    # 統合メッセージ
    content += "### 統合メッセージ\n"
    content += "企業は自ら進化し続ける『学習する組織』として、"
    content += "過去の成果と現在の強みを活かしながら、"
    content += "未来のチャレンジに主体的に対応していきます。\n"
    content += "複数の可能性の中から、最適な道を選択し、"
    content += "企業価値の継続的な向上を実現します。"
    
    return CorporateStorySection(
        title="企業の未来への道",
        content=content
    )


def generate_corporate_story(
    period: str,
    history: Dict,
    culture: CultureProfile,
    environment: ExternalEnvironmentState,
    executive_team: Dict[str, AICeoPersona],
    evolution: EnterpriseEvolutionResult,
    scenarios: List[ScenarioResult],
    optimization_plan: SelfOptimizationPlan
) -> CorporateStory:
    """企業の統合ストーリーを生成"""
    
    sections = [
        build_history_section(history),
        build_current_state_section(culture, environment, executive_team, evolution),
        build_scenario_section(scenarios),
        build_optimization_section(optimization_plan),
        build_integrated_narrative_section(history, culture, scenarios, optimization_plan, evolution)
    ]
    
    # サマリー作成
    summary = f"企業は過去の経験を踏まえ、現在の強みを活かしながら、"
    summary += f"未来に向けて {optimization_plan.objective.value} を目指す方向へ進化しています。"
    summary += f"期待される進化スコアは {optimization_plan.expected_evolution_score:.2f} です。"
    
    return CorporateStory(
        period=period,
        sections=sections,
        summary=summary
    )
