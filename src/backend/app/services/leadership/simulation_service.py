import json
import os
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ...models.leadership.simulation import (
    VirtualTeamMember, VirtualProject, TroubleScenario,
    MemberReaction, LeadershipDecision, SimulationResult,
    LeadershipEvaluation
)

class LeadershipSimulationService:
    """AIリーダーシップシミュレーションサービス"""

    def __init__(self):
        self.data_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/samples')
        )
        self.scenarios_path = os.path.join(self.data_path, 'leadership_scenarios.json')
        self.team_templates_path = os.path.join(self.data_path, 'team_templates.json')
        self.project_templates_path = os.path.join(self.data_path, 'project_templates.json')

    def load_scenarios(self) -> List[Dict[str, Any]]:
        """トラブルシナリオを読み込み"""
        if not os.path.exists(self.scenarios_path):
            return self._create_default_scenarios()
        with open(self.scenarios_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_team_templates(self) -> List[Dict[str, Any]]:
        """チームテンプレートを読み込み"""
        if not os.path.exists(self.team_templates_path):
            return self._create_default_team_templates()
        with open(self.team_templates_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_project_templates(self) -> List[Dict[str, Any]]:
        """プロジェクトテンプレートを読み込み"""
        if not os.path.exists(self.project_templates_path):
            return self._create_default_project_templates()
        with open(self.project_templates_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def create_simulation(self, user_id: str, difficulty: str = "medium") -> SimulationResult:
        """新しいシミュレーションを作成"""
        # プロジェクト選択
        projects = self.load_project_templates()
        if not projects:
            projects = self._create_default_project_templates()
        project_candidates = [p for p in projects if p.get('difficulty', 'medium') == difficulty]
        if not project_candidates:
            project_candidates = projects
        project_data = random.choice(project_candidates)
        project_dict = dict(project_data)
        project_dict['project_id'] = f"proj_{int(datetime.now().timestamp())}"
        project_dict.setdefault('complexity', difficulty)
        project_dict.setdefault('risk_level', 'medium')
        project_dict.setdefault('milestones', [])
        project = VirtualProject(**project_dict)

        # チーム作成
        team_templates = self.load_team_templates()
        if not team_templates:
            team_templates = self._create_default_team_templates()
        team_size = min(len(team_templates), random.randint(4, 7))
        if team_size < 1:
            team_size = 1
        team_data = random.sample(team_templates, team_size)
        team = []
        for i, member_data in enumerate(team_data):
            member_dict = dict(member_data)
            member_dict['member_id'] = f"member_{i+1}"
            # skillsをdict形式に変換
            if 'skills' in member_dict and isinstance(member_dict['skills'], list):
                skills_dict = {}
                for skill in member_dict['skills']:
                    # スキルレベルを推定（経験年数に基づく）
                    level = min(1.0, member_dict.get('experience_years', 3) / 10.0)
                    skills_dict[skill] = level
                member_dict['skills'] = skills_dict
            # 不足フィールドを追加
            member_dict.setdefault('stress_tolerance', 0.7)
            member_dict.setdefault('communication_style', 'バランス型')
            team.append(VirtualTeamMember(**member_dict))

        # シナリオ選択
        scenarios_data = self.load_scenarios()
        num_scenarios = random.randint(3, 5)
        selected_scenarios = random.sample(scenarios_data, num_scenarios)
        scenarios = []
        for scenario_data in selected_scenarios:
            scenario_dict = dict(scenario_data)
            scenario_dict.setdefault('type', scenario_dict.get('category', 'general'))
            scenario_dict.setdefault('severity', 'major')
            scenario_dict.setdefault('impact', 'チーム生産性への影響')
            scenario_dict.setdefault('possible_responses', scenario_dict.get('possible_decisions', []))
            scenario_dict.setdefault('correct_approach', scenario_dict.get('optimal_decision', ''))
            scenarios.append(TroubleScenario(**scenario_dict))

        simulation = SimulationResult(
            simulation_id=f"sim_{user_id}_{int(datetime.now().timestamp())}",
            user_id=user_id,
            project=project,
            team=team,
            scenarios=scenarios,
            decisions=[],
            final_score=0.0,
            feedback={},
            completed_at=datetime.now()
        )

        return simulation

    def get_next_scenario(self, simulation: SimulationResult) -> Optional[TroubleScenario]:
        """次のトラブルシナリオを取得"""
        decided_scenarios = {d.scenario_id for d in simulation.decisions}
        remaining = [s for s in simulation.scenarios if s.scenario_id not in decided_scenarios]
        return remaining[0] if remaining else None

    def generate_member_reactions(self, scenario: TroubleScenario, team: List[VirtualTeamMember]) -> List[MemberReaction]:
        """メンバーの反応を生成"""
        reactions = []
        for member in team:
            reaction = self._generate_member_reaction(member, scenario)
            reactions.append(reaction)
        return reactions

    def _generate_member_reaction(self, member: VirtualTeamMember, scenario: TroubleScenario) -> MemberReaction:
        """個別のメンバー反応を生成"""
        # パーソナリティに基づいて反応を生成
        personality_factors = {
            "内向的": {"response_style": "慎重", "emotional_intensity": 0.3},
            "外向的": {"response_style": "積極的", "emotional_intensity": 0.8},
            "協調的": {"response_style": "チーム指向", "emotional_intensity": 0.5},
            "競争的": {"response_style": "個人指向", "emotional_intensity": 0.7}
        }

        personality = member.personality.split('/')[0]  # 最初の特性を使用
        factors = personality_factors.get(personality, {"response_style": "中立的", "emotional_intensity": 0.5})

        # シナリオタイプに基づいて反応を調整
        scenario_type = getattr(scenario, 'type', getattr(scenario, 'category', 'general'))
        if scenario_type == "technical" or "技術" in scenario.description:
            # 技術スキルを持つメンバーはポジティブ
            has_tech_skill = any("Python" in skill or "JavaScript" in skill or "開発" in skill for skill in member.skills.keys())
            if has_tech_skill:
                reaction_type = "positive"
                response = f"{member.name}は技術的な問題に自信を持って対応できると提案しています。"
            else:
                reaction_type = "negative"
                response = f"{member.name}は技術的な複雑さに不安を感じています。"

        elif scenario_type == "interpersonal" or "対立" in scenario.description:
            if member.personality == "協調的":
                reaction_type = "positive"
                response = f"{member.name}はチームの調和を重視した解決策を提案しています。"
            else:
                reaction_type = "neutral"
                response = f"{member.name}は人間関係の問題に慎重に対応しています。"

        else:
            reaction_type = "neutral"
            response = f"{member.name}は状況を観察しています。"

        return MemberReaction(
            member_id=member.member_id,
            reaction_type=reaction_type,
            response=response,
            emotional_state="落ち着いている" if factors["emotional_intensity"] < 0.6 else "緊張している",
            suggested_action=self._generate_suggested_action(member, scenario)
        )

    def _generate_suggested_action(self, member: VirtualTeamMember, scenario: TroubleScenario) -> str:
        """メンバーの提案行動を生成"""
        actions = [
            "専門家の助けを借りる",
            "チームミーティングを開催する",
            "期限を延長する",
            "リソースを再配分する",
            "コミュニケーションを改善する"
        ]
        return random.choice(actions)

    def evaluate_decision(self, decision: LeadershipDecision, scenario: TroubleScenario,
                         team: List[VirtualTeamMember]) -> LeadershipEvaluation:
        """判断を評価"""
        # 正解度を計算
        correctness_score = self._calculate_correctness(decision.chosen_action, scenario.correct_approach)

        # チーム影響を評価
        team_impact_score = self._assess_team_impact(decision, team, scenario)

        # リーダーシップスタイルを評価
        leadership_score = self._assess_leadership_style(decision, scenario)

        total_score = (correctness_score * 0.4 + team_impact_score * 0.4 + leadership_score * 0.2)

        evaluation = LeadershipEvaluation(
            evaluation_id=f"eval_{decision.decision_id}",
            simulation_id="",  # 後で設定
            evaluated_by="AI",
            scores={
                "correctness": correctness_score,
                "team_impact": team_impact_score,
                "leadership": leadership_score,
                "overall": total_score
            },
            strengths=self._identify_strengths(decision, scenario),
            weaknesses=self._identify_weaknesses(decision, scenario),
            recommendations=self._generate_recommendations(decision, scenario),
            leadership_style_assessment=self._assess_leadership_style_detailed(decision),
            development_areas=self._identify_development_areas(decision, scenario)
        )

        return evaluation

    def _calculate_correctness(self, chosen_action: str, correct_approach: str) -> float:
        """正解度の計算"""
        if chosen_action.lower() in correct_approach.lower():
            return 1.0
        elif any(word in chosen_action.lower() for word in correct_approach.lower().split()):
            return 0.7
        else:
            return 0.3

    def _assess_team_impact(self, decision: LeadershipDecision, team: List[VirtualTeamMember],
                           scenario: TroubleScenario) -> float:
        """チームへの影響を評価"""
        # チームのスキルとシナリオの適合度を計算
        scenario_type = getattr(scenario, 'type', 'general')
        relevant_skills = [skill for member in team for skill in member.skills.keys() 
                          if scenario_type.lower() in skill.lower() or skill.lower() in scenario.description.lower()]
        team_expertise = len(relevant_skills) / len(team) if team else 0
        return min(1.0, team_expertise + 0.3)  # 最低0.3

    def _assess_leadership_style(self, decision: LeadershipDecision, scenario: TroubleScenario) -> float:
        """リーダーシップスタイルを評価"""
        reasoning_length = len(decision.reasoning.split())
        if reasoning_length > 50:
            return 0.9  # 詳細な考察
        elif reasoning_length > 20:
            return 0.7  # 適切な考察
        else:
            return 0.4  # 不十分

    def _identify_strengths(self, decision: LeadershipDecision, scenario: TroubleScenario) -> List[str]:
        """強みを特定"""
        strengths = []
        if len(decision.reasoning) > 100:
            strengths.append("詳細な状況分析力")
        if "チーム" in decision.chosen_action:
            strengths.append("チーム指向のアプローチ")
        if "長期" in decision.reasoning:
            strengths.append("戦略的思考力")
        return strengths or ["状況判断力"]

    def _identify_weaknesses(self, decision: LeadershipDecision, scenario: TroubleScenario) -> List[str]:
        """弱みを特定"""
        weaknesses = []
        if len(decision.reasoning) < 30:
            weaknesses.append("判断の根拠が不十分")
        if "自分" in decision.chosen_action:
            weaknesses.append("チーム参加意識が低い")
        return weaknesses or ["さらなる経験が必要"]

    def _generate_recommendations(self, decision: LeadershipDecision, scenario: TroubleScenario) -> List[str]:
        """改善 recommendations を生成"""
        recommendations = [
            "チームメンバーとのコミュニケーションを強化する",
            "リスク評価のプロセスを確立する",
            "意思決定の基準を明確にする",
            "フィードバックの収集を習慣化する"
        ]
        return random.sample(recommendations, 2)

    def _assess_leadership_style_detailed(self, decision: LeadershipDecision) -> str:
        """詳細なリーダーシップスタイル評価"""
        styles = [
            "民主的リーダーシップ: チーム参加を重視",
            "権威的リーダーシップ: 迅速な意思決定",
            "変革的リーダーシップ: イノベーション志向",
            "取引的リーダーシップ: 目標達成重視"
        ]
        return random.choice(styles)

    def _identify_development_areas(self, decision: LeadershipDecision, scenario: TroubleScenario) -> List[str]:
        """成長領域を特定"""
        areas = [
            "危機管理能力",
            "チームビルディング",
            "戦略的計画立案",
            "コミュニケーションスキル",
            "意思決定力"
        ]
        return random.sample(areas, 3)

    def _create_default_scenarios(self) -> List[Dict[str, Any]]:
        """デフォルトのトラブルシナリオを作成"""
        return [
            {
                "scenario_id": "tech_001",
                "type": "technical",
                "severity": "major",
                "description": "主要な技術コンポーネントで予期せぬバグが発生し、プロジェクトの進捗が止まっている。",
                "impact": "プロジェクト全体の遅延リスク",
                "possible_responses": ["専門家を投入", "コードレビュー", "期限延長"],
                "correct_approach": "専門家を投入し、並行してコードレビューを実施"
            },
            {
                "scenario_id": "inter_001",
                "type": "interpersonal",
                "severity": "minor",
                "description": "チームメンバー間で意見対立が発生し、会議が非生産的になっている。",
                "impact": "チームモチベーションの低下",
                "possible_responses": ["個別面談", "ファシリテーター導入", "ルール設定"],
                "correct_approach": "個別面談で問題を解決し、チームルールを明確化"
            },
            {
                "scenario_id": "resource_001",
                "type": "resource",
                "severity": "critical",
                "description": "重要なリソース（人材）が突然離脱し、プロジェクト継続が危ぶまれる。",
                "impact": "プロジェクトの中止リスク",
                "possible_responses": ["代替人材確保", "スコープ縮小", "パートナー活用"],
                "correct_approach": "代替人材を緊急確保し、パートナー企業と連携"
            }
        ]

    def _create_default_team_templates(self) -> List[Dict[str, Any]]:
        """デフォルトのチームメンバーテンプレートを作成"""
        return [
            {
                "member_id": "mem_001",
                "name": "田中太郎",
                "role": "シニア開発者",
                "personality": "内向的/協調的",
                "skills": {"技術": 0.9, "リーダーシップ": 0.6, "コミュニケーション": 0.7},
                "leadership_style": "支援的",
                "stress_tolerance": 0.8,
                "communication_style": "協調的"
            },
            {
                "member_id": "mem_002",
                "name": "佐藤花子",
                "role": "プロジェクトマネージャー",
                "personality": "外向的/競争的",
                "skills": {"マネジメント": 0.8, "技術": 0.5, "リーダーシップ": 0.9},
                "leadership_style": "権威的",
                "stress_tolerance": 0.6,
                "communication_style": "直接的"
            },
            {
                "member_id": "mem_003",
                "name": "鈴木次郎",
                "role": "QAエンジニア",
                "personality": "内向的/協調的",
                "skills": {"品質管理": 0.9, "技術": 0.7, "分析": 0.8},
                "leadership_style": "民主的",
                "stress_tolerance": 0.7,
                "communication_style": "慎重"
            }
        ]

    def _create_default_project_templates(self) -> List[Dict[str, Any]]:
        """デフォルトのプロジェクトテンプレートを作成"""
        return [
            {
                "project_id": "proj_001",
                "name": "クラウド移行プロジェクト",
                "description": "レガシーシステムをクラウドに移行するプロジェクト",
                "duration_weeks": 12,
                "complexity": "high",
                "risk_level": "high",
                "objectives": ["コスト削減", "スケーラビリティ向上", "運用効率化"],
                "milestones": [
                    {"week": 4, "description": "要件定義完了"},
                    {"week": 8, "description": "PoC完了"},
                    {"week": 12, "description": "移行完了"}
                ],
                "difficulty": "medium"
            },
            {
                "project_id": "proj_002",
                "name": "モバイルアプリ開発",
                "description": "新規モバイルアプリケーションの開発",
                "duration_weeks": 8,
                "complexity": "medium",
                "risk_level": "medium",
                "objectives": ["ユーザー体験向上", "市場シェア拡大"],
                "milestones": [
                    {"week": 2, "description": "設計完了"},
                    {"week": 5, "description": "MVPリリース"},
                    {"week": 8, "description": "正式リリース"}
                ],
                "difficulty": "easy"
            }
        ]