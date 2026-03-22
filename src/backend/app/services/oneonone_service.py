import json
import os
from typing import Dict, Any, Optional
from ..models.member import Member
from ..models.task import Task

class OneOnOneService:
    def __init__(self):
        self.members_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../data/samples/members.json'))

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

    def prepare_oneonone(self, member_id: int) -> Optional[Dict[str, Any]]:
        members = self.load_members()
        if member_id not in members:
            return None
        
        member = members[member_id]
        
        # 要約生成（簡易）
        summary = {
            "strengths": member.strengths or [],
            "challenges": member.challenges or [],
            "topics": self._generate_topics(member),
            "next_actions": self._generate_next_actions(member)
        }
        
        return {
            "member": member.dict(),
            "recent_tasks": [task.dict() for task in member.recent_tasks],
            "summary": summary
        }
    
    def _generate_topics(self, member: Member) -> list:
        # テンプレベースの話題候補
        topics = []
        if member.recent_tasks:
            topics.append(f"{member.name}さんの最近のタスク状況について")
        if member.strengths:
            topics.append(f"{member.name}さんの強みを活かした業務について")
        if member.challenges:
            topics.append(f"{member.name}さんの課題解決支援について")
        topics.append(f"{member.name}さんのキャリアプランについて")
        topics.append("チーム全体の改善点について")
        return topics
    
    def _generate_next_actions(self, member: Member) -> list:
        # 次アクション案生成
        actions = []
        if member.challenges:
            for challenge in member.challenges:
                actions.append(f"{challenge}の改善に向けたトレーニングを実施")
        if member.strengths:
            actions.append(f"{member.name}さんの強みを活かしたプロジェクトへのアサイン")
        actions.append("次回の1on1で進捗を確認")
        return actions