import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..models.development import DevelopmentPlan, DevelopmentMilestone
from ..models.member import Member
from ..models.task import Task

class DevelopmentService:
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

    def generate_development_plan(self, member_id: int) -> Optional[DevelopmentPlan]:
        members = self.load_members()
        if member_id not in members:
            return None
        
        member = members[member_id]
        
        # 現在のレベルと目標レベルの判定
        current_level, target_level = self._assess_levels(member)
        
        # 計画期間の設定（3-6ヶ月）
        plan_duration = self._determine_plan_duration(member)
        
        # マイルストーンの生成
        milestones = self._generate_milestones(member, plan_duration)
        
        # 全体目標の設定
        overall_objectives = self._generate_overall_objectives(member, target_level)
        
        # 成功指標の設定
        success_metrics = self._generate_success_metrics(member, target_level)
        
        plan = DevelopmentPlan(
            member_id=member.id,
            member_name=member.name,
            role=member.role,
            current_level=current_level,
            target_level=target_level,
            plan_duration_months=plan_duration,
            milestones=milestones,
            overall_objectives=overall_objectives,
            success_metrics=success_metrics,
            created_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        return plan
    
    def _assess_levels(self, member: Member) -> tuple[str, str]:
        """メンバーの現在のレベルと目標レベルを判定"""
        role = member.role
        
        if '次代マネージャー候補' in role:
            return '中堅レベル', 'マネージャーレベル'
        elif 'リーダー' in role and '新' in role:
            return '中堅レベル', 'リーダーレベル'
        elif '新人' in role or '新' in role:
            return '新人レベル', '中堅レベル'
        else:
            return '中堅レベル', '上級レベル'
    
    def _determine_plan_duration(self, member: Member) -> int:
        """育成計画の期間を決定（3-6ヶ月）"""
        role = member.role
        
        if '新人' in role or '新' in role:
            return 3  # 新人は3ヶ月で中堅化
        elif '次代マネージャー候補' in role:
            return 6  # マネージャー候補は6ヶ月
        elif 'リーダー' in role and '新' in role:
            return 4  # 新リーダーは4ヶ月
        else:
            return 4  # デフォルト4ヶ月
    
    def _generate_milestones(self, member: Member, duration: int) -> List[DevelopmentMilestone]:
        """月ごとのマイルストーンを生成"""
        milestones = []
        role = member.role
        challenges = member.challenges or []
        strengths = member.strengths or []
        
        for month in range(1, duration + 1):
            if '次代マネージャー候補' in role:
                milestone = self._generate_manager_candidate_milestone(month, challenges, strengths)
            elif 'リーダー' in role and '新' in role:
                milestone = self._generate_new_leader_milestone(month, challenges, strengths)
            elif '新人' in role or '新' in role:
                milestone = self._generate_newcomer_milestone(month, challenges, strengths)
            else:
                milestone = self._generate_general_milestone(month, challenges, strengths)
            
            milestones.append(milestone)
        
        return milestones
    
    def _generate_manager_candidate_milestone(self, month: int, challenges: List[str], strengths: List[str]) -> DevelopmentMilestone:
        """マネージャー候補のマイルストーン生成"""
        milestones_data = {
            1: {
                'title': '業務棚卸しと判断基準の明確化',
                'description': '現在の業務範囲を整理し、意思決定の基準を確立する',
                'objectives': ['業務の棚卸し完了', '判断基準の文書化'],
                'activities': ['業務フロー図作成', '判断基準ワークショップ'],
                'evaluation': ['業務棚卸しレポート提出', '判断基準ドキュメント承認']
            },
            2: {
                'title': '会議ファシリテーション訓練',
                'description': '会議の進行・合意形成スキルを習得する',
                'objectives': ['ファシリテーション基礎習得', '会議進行の実践'],
                'activities': ['ファシリテーション研修参加', '小規模会議のリード'],
                'evaluation': ['研修参加証明', '会議フィードバック評価']
            },
            3: {
                'title': '小規模プロジェクトのリード',
                'description': '小さなプロジェクトをリードし、マネジメント経験を積む',
                'objectives': ['プロジェクト計画立案', 'チームマネジメント実施'],
                'activities': ['プロジェクト計画作成', '週次進捗管理'],
                'evaluation': ['プロジェクト完了', 'チームメンバーからの評価']
            },
            4: {
                'title': 'メンバー育成の実践',
                'description': '部下の育成・指導を実践する',
                'objectives': ['育成計画作成', '定期的な1on1実施'],
                'activities': ['育成計画策定', '月次1on1ミーティング'],
                'evaluation': ['育成計画承認', 'メンバーの成長指標向上']
            },
            5: {
                'title': '管理職試験の模擬ケース',
                'description': '管理職試験に向けたケーススタディを実施',
                'objectives': ['ケース分析能力向上', 'プレゼンテーションスキル習得'],
                'activities': ['模擬ケース演習', 'プレゼンテーション練習'],
                'evaluation': ['ケース分析レポート', 'プレゼンテーション評価']
            },
            6: {
                'title': '業務委譲の実践',
                'description': '一部業務を委譲し、マネジメント業務に集中',
                'objectives': ['委譲業務の特定', '委譲プロセスの確立'],
                'activities': ['業務委譲計画作成', '委譲業務のフォローアップ'],
                'evaluation': ['委譲業務の安定稼働', '本人のマネジメント業務比率向上']
            }
        }
        
        data = milestones_data.get(month, milestones_data[1])
        return DevelopmentMilestone(
            month=month,
            title=data['title'],
            description=data['description'],
            objectives=data['objectives'],
            activities=data['activities'],
            evaluation_criteria=data['evaluation']
        )
    
    def _generate_new_leader_milestone(self, month: int, challenges: List[str], strengths: List[str]) -> DevelopmentMilestone:
        """新リーダーのマイルストーン生成"""
        milestones_data = {
            1: {
                'title': 'チーム理解と関係構築',
                'description': 'チームメンバーの状況を把握し、信頼関係を築く',
                'objectives': ['全メンバーとの個別面談完了', 'チームの強み・課題把握'],
                'activities': ['1on1面談実施', 'チームミーティング参加'],
                'evaluation': ['面談記録提出', 'チーム理解レポート作成']
            },
            2: {
                'title': '業務プロセス整理',
                'description': 'チームの業務プロセスを整理・改善する',
                'objectives': ['現状業務プロセスの可視化', '改善点の特定'],
                'activities': ['プロセスフロー図作成', '改善提案策定'],
                'evaluation': ['プロセス図承認', '改善提案評価']
            },
            3: {
                'title': 'チーム目標設定と合意形成',
                'description': 'チーム目標を設定し、メンバーの合意を得る',
                'objectives': ['チーム目標の策定', 'メンバー合意の獲得'],
                'activities': ['目標設定ワークショップ', '合意形成ミーティング'],
                'evaluation': ['目標文書承認', '合意度調査結果']
            },
            4: {
                'title': 'リーダーシップの実践',
                'description': '日常業務でのリーダーシップを発揮する',
                'objectives': ['リーダーシップ行動の実践', 'チームパフォーマンス向上'],
                'activities': ['日次業務でのリード', 'チームミーティング主催'],
                'evaluation': ['行動観察フィードバック', 'チームパフォーマンス指標']
            }
        }
        
        data = milestones_data.get(month, milestones_data[1])
        return DevelopmentMilestone(
            month=month,
            title=data['title'],
            description=data['description'],
            objectives=data['objectives'],
            activities=data['activities'],
            evaluation_criteria=data['evaluation']
        )
    
    def _generate_newcomer_milestone(self, month: int, challenges: List[str], strengths: List[str]) -> DevelopmentMilestone:
        """新人のマイルストーン生成"""
        milestones_data = {
            1: {
                'title': '業務基礎習得',
                'description': '担当業務の基礎知識・スキルを習得する',
                'objectives': ['業務マニュアル理解', '基本業務の遂行'],
                'activities': ['研修参加', 'OJT実施'],
                'evaluation': ['基礎テスト合格', '基本業務完了率90%以上']
            },
            2: {
                'title': '業務実践とフィードバック',
                'description': '実際の業務を通じてスキルを磨く',
                'objectives': ['担当業務の独力遂行', 'フィードバックの積極的活用'],
                'activities': ['業務遂行', '定期フィードバック面談'],
                'evaluation': ['業務品質評価', 'フィードバック活用度']
            },
            3: {
                'title': '自律的業務遂行',
                'description': '指導なしで業務を遂行できるようになる',
                'objectives': ['業務の自律的遂行', '品質基準の達成'],
                'activities': ['独立業務遂行', '品質管理'],
                'evaluation': ['業務完了率95%以上', '品質評価基準達成']
            }
        }
        
        data = milestones_data.get(month, milestones_data[1])
        return DevelopmentMilestone(
            month=month,
            title=data['title'],
            description=data['description'],
            objectives=data['objectives'],
            activities=data['activities'],
            evaluation_criteria=data['evaluation']
        )
    
    def _generate_general_milestone(self, month: int, challenges: List[str], strengths: List[str]) -> DevelopmentMilestone:
        """一般的なマイルストーン生成"""
        return DevelopmentMilestone(
            month=month,
            title=f'第{month}ヶ月：継続的なスキル向上',
            description='既存スキルの深化と新しい挑戦',
            objectives=['スキル向上目標の達成', '業務貢献度の向上'],
            activities=['スキル研修参加', '業務改善提案'],
            evaluation_criteria=['研修参加証明', '業務評価向上']
        )
    
    def _generate_overall_objectives(self, member: Member, target_level: str) -> List[str]:
        """全体目標の生成"""
        role = member.role
        
        if '次代マネージャー候補' in role:
            return [
                '管理職としての判断力・決断力を身につける',
                'チームマネジメントスキルを習得する',
                '組織貢献度の高い人材となる'
            ]
        elif 'リーダー' in role and '新' in role:
            return [
                'チームリーダーとしての責任を果たす',
                'メンバーの成長を促す環境を整える',
                'チームパフォーマンスを向上させる'
            ]
        elif '新人' in role or '新' in role:
            return [
                '担当業務の専門性を高める',
                '組織の一員としての自覚を持つ',
                '早期戦力化を実現する'
            ]
        else:
            return [
                '現在のスキルをさらに向上させる',
                'チーム貢献度の高い人材となる',
                'リーダーシップを発揮する機会を増やす'
            ]
    
    def _generate_success_metrics(self, member: Member, target_level: str) -> List[str]:
        """成功指標の生成"""
        role = member.role
        
        if '次代マネージャー候補' in role:
            return [
                '管理職試験合格',
                'チームマネジメント業務の遂行',
                '部下育成実績の向上',
                'プロジェクトリード経験の蓄積'
            ]
        elif 'リーダー' in role and '新' in role:
            return [
                'チーム目標達成率',
                'メンバー満足度調査結果',
                'チームパフォーマンス指標向上',
                'リーダーシップ評価スコア'
            ]
        elif '新人' in role or '新' in role:
            return [
                '業務遂行品質評価',
                '業務完了率',
                'フィードバック活用度',
                '自立業務遂行期間の短縮'
            ]
        else:
            return [
                '業務評価スコアの向上',
                'チーム貢献度の定量化',
                'スキル習得度の評価',
                'リーダーシップ発揮機会の増加'
            ]