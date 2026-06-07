# Company History Overview

## 概要

企業の歴史生成システムは、月次・四半期・年次の結果を「歴史」として蓄積し、CEO/経営チーム交代・文化変化・外部環境ショック・進化スコアをタイムライン化します。また、年次レポートを自動生成し、ダッシュボードから企業の歴史を俯瞰できるようにします。

## アーキテクチャ

### モデル構造

#### LeadershipEvent
- CEOおよび経営チームの交代イベントを記録
- イベントタイプ: "ceo_succession" | "executive_succession"
- 変更前後の担当者情報と理由を保持

#### CultureSnapshot / EnvironmentSnapshot / EvolutionSnapshot
- 各期間の文化・環境・進化状態のスナップショット
- タイムライン分析に使用

#### AnnualReport
- 年次財務集計（売上・利益合計）
- 主要イベント（交代・ショックなど）
- 文化トレンド（前年比変化）
- 進化スコアトレンド
- Markdownレポートファイルパス

#### CompanyHistory
- 全リーダーシップイベントのタイムライン
- 全年次レポートのコレクション

### エンジン層 (CompanyHistoryEngine)

#### build_leadership_timeline()
- CEO SuccessionとExecutive Team Successionの履歴からイベントタイムラインを構築
- 時系列でソートして返却

#### build_annual_report()
- 指定年の月次結果を集計して年次レポートを生成
- 財務データ集計、イベント抽出、文化トレンド計算
- Markdownレポートを自動生成して保存

#### render_annual_report_markdown()
- 年次レポートのMarkdownコンテンツを生成
- 財務サマリ、主要イベント、文化トレンド、進化スコアを含む

### サービス層 (CompanyHistoryService)

#### generate_annual_history(year)
- 指定年の年次歴史を生成・保存
- 各種履歴データを収集してエンジンに渡す

#### generate_timeline()
- 完全な企業タイムラインを構築
- 全イベントとレポートを統合

#### get_latest_annual_report() / get_annual_report(year)
- 年次レポートの取得メソッド

### API層

#### GET /api/history/annual/latest
- 最新の年次レポートを取得

#### GET /api/history/annual/{year}
- 指定年の年次レポートを取得

#### GET /api/history/timeline
- 完全な企業タイムラインを取得

## ダッシュボード統合

### AnnualHistorySummary
- ダッシュボード表示用の年次歴史サマリー
- 年、財務データ、進化トレンド、主要イベント（5件まで）

### ExecutiveDashboard 拡張
- `latest_annual_history` フィールドを追加
- 最新の年次レポートをサマリー形式で表示

## データ永続化

### ディレクトリ構造
```
data/
├── history/
│   ├── 2024/
│   │   └── annual_report.json
│   └── 2025/
│       └── annual_report.json
└── reports/
    └── annual/
        ├── 2024.md
        └── 2025.md
```

### 保存形式
- 年次レポート: JSON (CompanyHistoryService)
- Markdownレポート: MDファイル (CompanyHistoryEngine)

## 使用例

### 年次レポート生成
```python
from company_history_service import CompanyHistoryService

service = CompanyHistoryService()
report = service.generate_annual_history(2024)
print(f"Generated report for {report.year}")
```

### タイムライン取得
```python
timeline = service.generate_timeline()
for event in timeline.leadership_events:
    print(f"{event.period}: {event.event_type}")
```

### API使用
```bash
# 最新年次レポート
GET /api/history/annual/latest

# 指定年レポート
GET /api/history/annual/2024

# 完全タイムライン
GET /api/history/timeline
```

## ダッシュボード表示例

```
最新年次レポート (2024年)
─────────────────────────
売上合計: ¥2,200,000
営業利益: ¥220,000
進化トレンド: +0.75

主要イベント:
- CEO交代: Jane Smith → John Doe
- 重大ショック: 市場変動による影響
- 新製品発売成功
```

このシステムにより、ユーザーは企業の長期的な進化を俯瞰し、戦略的意思決定に活用することができます。