import json
import os
from typing import List, Dict, Any
from datetime import datetime
from ..models.recommendation import MemberRecommendation, FollowUpRecommendation

class RecommendationService:
    def __init__(self):
        self.members_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../data/samples/members.json'))

    def load_members(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.members_path):
            return []
        with open(self.members_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data

    def _calculate_follow_up_score(self, member: Dict[str, Any]) -> float:
        """メンバーをフォローアップするべき度を点数化（高いほど優先度高）"""
        score = 0.0
        
        # 課題の数で加点（課題が多いほど支援が必要）
        challenges = member.get('challenges', [])
        score += len(challenges) * 2.0
        
        # 最近のタスクで加点（タスクが少ないと関心が薄い可能性）
        recent_tasks = member.get('recent_tasks', [])
        if len(recent_tasks) == 0:
            score += 2.0
        elif len(recent_tasks) == 1:
            score += 1.0
        
        # ロールで加点（新しいロール、変化の可能性）
        role = member.get('role', '')
        if 'リーダー' in role and '新' in member.get('notes', ''):
            score += 2.5
        elif '新人' in role or '新' in role:
            score += 2.0
        
        # 強みで調整（強みが十分に活かされているかの推定）
        strengths = member.get('strengths', [])
        if len(strengths) < 2:
            score += 0.5
        
        return score

    def get_followup_members(self, top_n: int = 3) -> FollowUpRecommendation:
        """フォローアップすべきメンバーTop Nを返す"""
        members = self.load_members()
        
        # スコアを計算
        scored_members = []
        for member in members:
            score = self._calculate_follow_up_score(member)
            scored_members.append((member, score))
        
        # スコア順でソート
        scored_members.sort(key=lambda x: x[1], reverse=True)
        
        # Top Nを取得
        top_members = scored_members[:top_n]
        
        # RecommendationList の作成
        recommendations = []
        for member, score in top_members:
            recommendation = self._create_recommendation(member, score)
            recommendations.append(recommendation)
        
        # 日付の設定
        today = datetime.now().strftime("%Y-%m-%d")
        
        summary = f"今週フォローアップが必要なメンバーは{len(recommendations)}名です。優先度順にあなたの声かけをお勧めします。"
        
        return FollowUpRecommendation(
            date=today,
            members=recommendations,
            summary=summary
        )
    
    def _create_recommendation(self, member: Dict[str, Any], score: float) -> MemberRecommendation:
        """スコアに基づき、推奨情報を生成"""
        # 優先度の決定
        if score >= 4.0:
            priority = "high"
        elif score >= 2.0:
            priority = "medium"
        else:
            priority = "low"
        
        # 理由の生成
        reason_parts = []
        challenges = member.get('challenges', [])
        if challenges:
            reason_parts.append(f"課題あり（{', '.join(challenges[:2])}）")
        
        recent_tasks = member.get('recent_tasks', [])
        if len(recent_tasks) == 0:
            reason_parts.append("最近のタスクがない")
        
        role = member.get('role', '')
        if 'リーダー' in role or '新' in role:
            reason_parts.append(f"新しい役割（{role}）")
        
        reason = "、".join(reason_parts) if reason_parts else "定期的なチェックイン必要"
        
        # 提案アクションの生成
        suggested_action = self._generate_suggested_action(member, challenges)
        
        return MemberRecommendation(
            member_id=member.get('id'),
            name=member.get('name'),
            role=member.get('role'),
            priority=priority,
            reason=reason,
            suggested_action=suggested_action
        )
    
    def _generate_suggested_action(self, member: Dict[str, Any], challenges: List[str]) -> str:
        """メンバーに対する具体的なアクションを提案"""
        role = member.get('role', '')
        recent_tasks = member.get('recent_tasks', [])
        
        if '新' in role or '新人' in role:
            return "進捗確認と具体的なサポート方法の相談"
        elif 'リーダー' in role:
            return "チームビルディングの課題を深掘りしながらサポート"
        elif len(recent_tasks) == 0:
            return "最近の業務内容と本人の課題感をヒアリング"
        elif challenges:
            first_challenge = challenges[0]
            return f"'{first_challenge}'の改善に向けた具体的な支援を検討"
        else:
            return "定期的な1on1でのチェックイン"