import json
import os
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..models.development import (
    AssessmentCase, AssessmentAnswer, AssessmentFeedback, 
    AssessmentPractice
)
from ..models.member import Member
from ..models.task import Task

class AssessmentService:
    def __init__(self):
        self.cases_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../data/samples/assessment_cases.json'))
        self.practice_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../data/samples/assessment_practice.json'))
        self.members_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../data/samples/members.json'))

    def load_cases(self) -> Dict[str, AssessmentCase]:
        if not os.path.exists(self.cases_path):
            return {}
        with open(self.cases_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        cases = {}
        for item in data:
            case = AssessmentCase(**item)
            cases[case.id] = case
        return cases

    def save_cases(self, cases: Dict[str, AssessmentCase]):
        data = [case.dict() for case in cases.values()]
        os.makedirs(os.path.dirname(self.cases_path), exist_ok=True)
        with open(self.cases_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_practice_data(self) -> Dict[int, AssessmentPractice]:
        if not os.path.exists(self.practice_path):
            return {}
        with open(self.practice_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        practices = {}
        for item in data:
            practice = AssessmentPractice(**item)
            practices[practice.member_id] = practice
        return practices

    def save_practice_data(self, practices: Dict[int, AssessmentPractice]):
        data = [practice.dict() for practice in practices.values()]
        os.makedirs(os.path.dirname(self.practice_path), exist_ok=True)
        with open(self.practice_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_members(self) -> Dict[int, Member]:
        if not os.path.exists(self.members_path):
            return {}
        with open(self.members_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        members = {}
        for item in data:
            # recent_tasksをTaskオブジェクトに変換
            recent_tasks = [Task(**t) for t in item.get('recent_tasks', [])]
            item['recent_tasks'] = recent_tasks
            member = Member(**item)
            members[member.id] = member
        return members

    def generate_case(self, member_id: int, difficulty: str = "intermediate") -> Optional[AssessmentCase]:
        """メンバーのプロフィールに基づいてケースを生成"""
        members = self.load_members()
        if member_id not in members:
            return None
        
        member = members[member_id]
        
        # メンバーのロールと強み・課題に基づいてケースを生成
        case = self._create_personalized_case(member, difficulty)
        
        # ケースを保存
        cases = self.load_cases()
        cases[case.id] = case
        self.save_cases(cases)
        
        return case

    def evaluate_answer(self, case_id: str, member_id: int, answer_text: str) -> Optional[AssessmentFeedback]:
        """回答を評価し、フィードバックを生成"""
        cases = self.load_cases()
        members = self.load_members()
        
        if case_id not in cases or member_id not in members:
            return None
        
        case = cases[case_id]
        member = members[member_id]
        
        # 回答を保存
        answer = AssessmentAnswer(
            case_id=case_id,
            member_id=member_id,
            member_name=member.name,
            answer_text=answer_text,
            approach_analysis=self._analyze_answer_approach(answer_text, case),
            submitted_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # フィードバックを生成
        feedback = self._generate_feedback(answer, case, member)
        
        # 練習データを更新
        self._update_practice_progress(member_id, feedback)
        
        return feedback

    def get_recommended_cases(self, member_id: int) -> List[AssessmentCase]:
        """メンバーの成長段階に合ったおすすめケースを取得"""
        members = self.load_members()
        if member_id not in members:
            return []
        
        member = members[member_id]
        cases = list(self.load_cases().values())
        
        # メンバーのレベルに合ったケースをフィルタリング
        recommended = []
        member_level = self._assess_member_level(member)
        
        for case in cases:
            if self._is_case_suitable(case, member_level, member):
                recommended.append(case)
        
        # 最大5件まで
        return recommended[:5]

    def get_practice_progress(self, member_id: int) -> Optional[AssessmentPractice]:
        """メンバーのアセスメント練習進捗を取得"""
        practices = self.load_practice_data()
        return practices.get(member_id)

    def _create_personalized_case(self, member: Member, difficulty: str) -> AssessmentCase:
        """メンバーのプロフィールに基づいてケースを生成"""
        role = member.role
        strengths = member.strengths or []
        challenges = member.challenges or []
        
        # ロールに応じたケースタイプを決定
        if '次代マネージャー候補' in role:
            case = self._generate_manager_candidate_case(difficulty, strengths, challenges)
        elif 'リーダー' in role and '新' in role:
            case = self._generate_new_leader_case(difficulty, strengths, challenges)
        else:
            case = self._generate_general_case(difficulty, strengths, challenges)
        
        return case

    def _generate_manager_candidate_case(self, difficulty: str, strengths: List[str], challenges: List[str]) -> AssessmentCase:
        """マネージャー候補向けケース生成"""
        cases = {
            "intermediate": {
                "title": "組織変革プロジェクトの推進",
                "scenario": "あなたは部長として、デジタルトランスフォーメーションを推進するプロジェクトのリーダーです。社内の抵抗が強く、プロジェクトが遅延しています。",
                "context": "全社的なDXプロジェクトを担当。予算は限定的で、社内理解も不十分。経営層の期待は高いが、現場の協力が得られない。",
                "challenge": "プロジェクトを軌道に乗せ、6ヶ月以内に具体的な成果を出さなければなりません。どのように対応しますか？",
                "evaluation_criteria": [
                    "課題の構造化と優先順位付け",
                    "ステークホルダー管理",
                    "リスク管理と代替案の検討",
                    "チームモチベーションの維持"
                ],
                "key_competencies": ["戦略的思考", "リーダーシップ", "変化管理", "コミュニケーション"]
            }
        }
        
        data = cases.get(difficulty, cases["intermediate"])
        return AssessmentCase(
            id=str(uuid.uuid4()),
            title=data["title"],
            scenario=data["scenario"],
            context=data["context"],
            challenge=data["challenge"],
            role="部長",
            difficulty_level=difficulty,
            evaluation_criteria=data["evaluation_criteria"],
            key_competencies=data["key_competencies"],
            estimated_time=45,
            created_date=datetime.now().strftime("%Y-%m-%d")
        )

    def _generate_new_leader_case(self, difficulty: str, strengths: List[str], challenges: List[str]) -> AssessmentCase:
        """新リーダー向けケース生成"""
        cases = {
            "intermediate": {
                "title": "チームパフォーマンスの改善",
                "scenario": "あなたは新任の課長として、業績不振のチームを引き継ぎました。メンバーのモチベーションが低く、目標達成が危ぶまれています。",
                "context": "前任者が異動し、チームは不安定。目標は厳しく設定されているが、メンバーのスキルや経験にばらつきがある。",
                "challenge": "3ヶ月でチームパフォーマンスを20%向上させる必要があります。具体的な行動計画を立ててください。",
                "evaluation_criteria": [
                    "現状分析の正確性",
                    "メンバーの状況把握",
                    "具体的な改善策の提案",
                    "実施計画の現実性"
                ],
                "key_competencies": ["状況把握力", "チームマネジメント", "計画立案", "実行力"]
            }
        }
        
        data = cases.get(difficulty, cases["intermediate"])
        return AssessmentCase(
            id=str(uuid.uuid4()),
            title=data["title"],
            scenario=data["scenario"],
            context=data["context"],
            challenge=data["challenge"],
            role="課長",
            difficulty_level=difficulty,
            evaluation_criteria=data["evaluation_criteria"],
            key_competencies=data["key_competencies"],
            estimated_time=35,
            created_date=datetime.now().strftime("%Y-%m-%d")
        )

    def _generate_general_case(self, difficulty: str, strengths: List[str], challenges: List[str]) -> AssessmentCase:
        """一般的なケース生成"""
        cases = {
            "intermediate": {
                "title": "部門間調整の難題",
                "scenario": "あなたは主任として、2つの部門間の調整業務を担当しています。双方の要求が対立し、期限が迫っています。",
                "context": "営業部門と開発部門の調整役。営業は機能追加を急ぎ、開発は品質確保を優先。双方の言い分はもっともだが、妥協点が見つからない。",
                "challenge": "双方が納得できる解決策を見出し、プロジェクトを前進させる必要があります。どのように対応しますか？",
                "evaluation_criteria": [
                    "双方の立場の理解",
                    "妥協点の探求",
                    "合意形成の手法",
                    "関係性の維持"
                ],
                "key_competencies": ["調整力", "コミュニケーション", "問題解決", "関係構築"]
            }
        }
        
        data = cases.get(difficulty, cases["intermediate"])
        return AssessmentCase(
            id=str(uuid.uuid4()),
            title=data["title"],
            scenario=data["scenario"],
            context=data["context"],
            challenge=data["challenge"],
            role="主任",
            difficulty_level=difficulty,
            evaluation_criteria=data["evaluation_criteria"],
            key_competencies=data["key_competencies"],
            estimated_time=30,
            created_date=datetime.now().strftime("%Y-%m-%d")
        )

    def _analyze_answer_approach(self, answer_text: str, case: AssessmentCase) -> str:
        """回答のアプローチを分析"""
        analysis = []
        
        # 構造化された回答か
        if "まず" in answer_text or "最初に" in answer_text or "ステップ" in answer_text:
            analysis.append("回答が構造化されている")
        
        # ステークホルダー考慮
        if "関係者" in answer_text or "メンバー" in answer_text or "チーム" in answer_text:
            analysis.append("ステークホルダーの考慮が見られる")
        
        # 具体的な行動
        if "実施する" in answer_text or "行う" in answer_text or "対策" in answer_text:
            analysis.append("具体的な行動計画が示されている")
        
        # リスク考慮
        if "リスク" in answer_text or "問題" in answer_text or "課題" in answer_text:
            analysis.append("リスクや課題の考慮が見られる")
        
        return "、".join(analysis) if analysis else "回答の構造化が必要"

    def _generate_feedback(self, answer: AssessmentAnswer, case: AssessmentCase, member: Member) -> AssessmentFeedback:
        """フィードバックを生成"""
        # スコア計算（簡易版）
        overall_score = self._calculate_score(answer, case, member)
        
        # コンピテンシー別スコア
        competency_scores = {}
        for competency in case.key_competencies:
            competency_scores[competency] = self._score_competency(answer, competency)
        
        # 強み・改善点の分析
        strengths, improvement_areas = self._analyze_answer_quality(answer, case)
        
        # 詳細フィードバック
        detailed_feedback = self._create_detailed_feedback(answer, case, overall_score)
        
        # 推奨アクション
        recommended_actions = self._generate_recommended_actions(improvement_areas, case)
        
        # 模範回答例
        sample_better_answer = self._create_sample_answer(case)
        
        return AssessmentFeedback(
            answer_id=str(uuid.uuid4()),
            case_id=case.id,
            member_id=member.id,
            overall_score=overall_score,
            competency_scores=competency_scores,
            strengths=strengths,
            improvement_areas=improvement_areas,
            detailed_feedback=detailed_feedback,
            recommended_actions=recommended_actions,
            sample_better_answer=sample_better_answer,
            created_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    def _calculate_score(self, answer: AssessmentAnswer, case: AssessmentCase, member: Member) -> int:
        """全体スコアを計算"""
        base_score = 60  # 基礎点
        
        # 回答の長さによる調整
        if len(answer.answer_text) > 500:
            base_score += 10
        elif len(answer.answer_text) < 200:
            base_score -= 10
        
        # アプローチ分析による調整
        if "構造化" in answer.approach_analysis:
            base_score += 15
        if "ステークホルダー" in answer.approach_analysis:
            base_score += 10
        if "具体的な行動" in answer.approach_analysis:
            base_score += 10
        if "リスク" in answer.approach_analysis:
            base_score += 5
        
        return min(100, max(0, base_score))

    def _score_competency(self, answer: AssessmentAnswer, competency: str) -> int:
        """各コンピテンシーのスコアを計算"""
        base_score = 50
        
        # コンピテンシー別のキーワードチェック
        keyword_map = {
            "戦略的思考": ["全体像", "優先順位", "長期視点", "戦略"],
            "リーダーシップ": ["リード", "決断", "責任", "チーム"],
            "コミュニケーション": ["説明", "共有", "対話", "合意"],
            "変化管理": ["抵抗", "理解", "説得", "変化"],
            "問題解決": ["分析", "解決", "代替案", "改善"],
            "チームマネジメント": ["メンバー", "育成", "モチベーション", "目標"]
        }
        
        keywords = keyword_map.get(competency, [])
        matched_keywords = sum(1 for keyword in keywords if keyword in answer.answer_text)
        
        base_score += matched_keywords * 10
        
        return min(100, max(0, base_score))

    def _analyze_answer_quality(self, answer: AssessmentAnswer, case: AssessmentCase) -> tuple[List[str], List[str]]:
        """回答の質を分析"""
        strengths = []
        improvement_areas = []
        
        # 強みの判定
        if len(answer.answer_text) > 400:
            strengths.append("回答が詳細で具体的")
        if "ステップ" in answer.answer_text or "段階" in answer.answer_text:
            strengths.append("手順が明確に示されている")
        if "リスク" in answer.answer_text:
            strengths.append("リスク考慮がなされている")
        
        # 改善点の判定
        if len(answer.answer_text) < 300:
            improvement_areas.append("より具体的な内容の追加が必要")
        if "数値" not in answer.answer_text and "目標" not in answer.answer_text:
            improvement_areas.append("定量的な目標設定を検討する")
        if "フォロー" not in answer.answer_text and "確認" not in answer.answer_text:
            improvement_areas.append("進捗確認とフォローアップの検討が必要")
        
        return strengths, improvement_areas

    def _create_detailed_feedback(self, answer: AssessmentAnswer, case: AssessmentCase, score: int) -> str:
        """詳細フィードバックを作成"""
        feedback_parts = []
        
        if score >= 80:
            feedback_parts.append("優れた回答です。論理的思考と実践的なアプローチが光っています。")
        elif score >= 70:
            feedback_parts.append("良い回答です。基本的な考え方は適切ですが、より深い洞察が加わるとより良くなります。")
        elif score >= 60:
            feedback_parts.append("基本的な考え方は理解できますが、より具体的な行動計画が必要です。")
        else:
            feedback_parts.append("回答の構造化と具体性に課題があります。基本的なフレームワークから見直しましょう。")
        
        # 評価基準に基づく具体的なフィードバック
        feedback_parts.append("\n\n評価ポイント:")
        for criterion in case.evaluation_criteria[:3]:
            if any(keyword in answer.answer_text for keyword in ["実施", "対策", "計画", "確認"]):
                feedback_parts.append(f"・{criterion}: 適切に考慮されています")
            else:
                feedback_parts.append(f"・{criterion}: さらなる検討が必要です")
        
        return "\n".join(feedback_parts)

    def _generate_recommended_actions(self, improvement_areas: List[str], case: AssessmentCase) -> List[str]:
        """推奨アクションを生成"""
        actions = []
        
        for area in improvement_areas:
            if "具体的な内容" in area:
                actions.append("回答の具体例を増やして記述する練習をする")
            elif "定量的な目標" in area:
                actions.append("目標設定時に数値目標を必ず含める")
            elif "フォローアップ" in area:
                actions.append("行動計画に必ず確認・フォロー手順を追加する")
        
        # コンピテンシー別推奨
        for competency in case.key_competencies[:2]:
            actions.append(f"{competency}に関するケーススタディを追加で練習する")
        
        return actions[:4]  # 最大4件

    def _create_sample_answer(self, case: AssessmentCase) -> str:
        """模範回答例を作成"""
        if "組織変革" in case.title:
            return """1. まず、プロジェクトの現状を正確に把握するため、関係者ヒアリングを実施
2. 経営層の期待と現場の懸念を整理し、ギャップを明確化
3. 短期的な成功事例を作成し、抵抗を減らす
4. 段階的な導入計画を策定し、定期的な進捗確認を行う"""
        elif "チームパフォーマンス" in case.title:
            return """1. 個別面談でメンバーの状況と課題を把握
2. チーム全体の目標を再設定し、メンバーの役割を明確化
3. スキルギャップを特定し、トレーニング計画を立案
4. 週次ミーティングで進捗確認とフィードバックを実施"""
        else:
            return """1. 双方の立場と要求を整理し、共通理解を図る
2. 妥協点を模索し、win-winの解決策を検討
3. 具体的な行動計画と期限を設定
4. 定期的なフォローアップで関係性を維持"""

    def _assess_member_level(self, member: Member) -> str:
        """メンバーのレベルを判定"""
        role = member.role
        if '次代マネージャー候補' in role:
            return 'advanced'
        elif 'リーダー' in role and '新' in role:
            return 'intermediate'
        else:
            return 'basic'

    def _is_case_suitable(self, case: AssessmentCase, member_level: str, member: Member) -> bool:
        """ケースがメンバーに適しているか判定"""
        # レベルの適合性
        level_match = (
            (member_level == 'basic' and case.difficulty_level in ['basic', 'intermediate']) or
            (member_level == 'intermediate' and case.difficulty_level in ['intermediate']) or
            (member_level == 'advanced' and case.difficulty_level in ['intermediate', 'advanced'])
        )
        
        # ロールの適合性（より柔軟なマッチング）
        member_role = member.role
        case_role = case.role
        
        role_match = (
            ('マネージャー' in member_role and '部長' in case_role) or
            ('リーダー' in member_role and '課長' in case_role) or
            ('新' in member_role and '主任' in case_role) or
            (case_role in member_role)  # 完全一致
        )
        
        return level_match and role_match

    def _update_practice_progress(self, member_id: int, feedback: AssessmentFeedback):
        """練習進捗を更新"""
        practices = self.load_practice_data()
        
        if member_id not in practices:
            # 新規作成
            members = self.load_members()
            member = members.get(member_id)
            if not member:
                return
            
            practice = AssessmentPractice(
                member_id=member_id,
                member_name=member.name,
                role=member.role,
                target_role="管理職",
                practice_sessions=[],
                overall_progress={comp: 0 for comp in feedback.competency_scores.keys()},
                recommended_cases=[],
                last_practice_date=datetime.now().strftime("%Y-%m-%d")
            )
            practices[member_id] = practice
        
        practice = practices[member_id]
        
        # セッションを追加
        session = {
            "date": feedback.created_date,
            "case_id": feedback.case_id,
            "score": feedback.overall_score,
            "competency_scores": feedback.competency_scores
        }
        practice.practice_sessions.append(session)
        
        # 全体進捗を更新
        for comp, score in feedback.competency_scores.items():
            if comp in practice.overall_progress:
                # 移動平均的な更新
                current = practice.overall_progress[comp]
                practice.overall_progress[comp] = int((current + score) / 2)
            else:
                practice.overall_progress[comp] = score
        
        practice.last_practice_date = feedback.created_date
        
        self.save_practice_data(practices)