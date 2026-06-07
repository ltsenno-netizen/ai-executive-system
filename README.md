# AI幹部システム

## プロジェクト概要

このプロジェクトは、管理職であるユーザーのマネジメント業務（メンバー管理・人材育成・予算/事業性管理）をAIが日次〜年次の運用レベルで代行する「AI幹部システム」を構築することを目的とする。最終的に、ユーザーが意思決定と戦略・課題設定に専念できる状態を実現する。

## 🎯 フェーズ0（仮想オフィス基盤）実装状況

### ✅ 実装済み機能

| 機能 | API エンドポイント | 説明 | ステータス |
|------|---|---|---|
| 💼 事業モデル | `GET /api/business/horipro` | えみプロ150億円モデルのPL構造 | ✅ 完成 |
| 🏢 組織構造 | `GET /api/organization/horipro` | 階層型組織構造データ | ✅ 完成 |
| 📈 戦略レイヤー | `GET /api/business/horipro/strategy` | 収益内訳・洞察・戦略的優先事項 | ✅ 完成 |
| 🎯 事業定義 | `GET /api/business/horipro/definition` | 収益マッピング・戦略課題・優先施策 | ✅ 完成 |

## 🎯 フェーズ0.5（タレントマネジメント部仮想オフィス）実装状況

### ✅ 実装済み機能

| 機能 | API エンドポイント | 説明 | ステータス |
|------|---|---|---|
| 🏗️ データモデル | - | UnitDefinition, TaskTemplate, IncidentScenario, MemberProfile, UnitState | ✅ 完成 |
| 📋 サンプルデータ | - | ユニット定義、タスクテンプレート、インシデントシナリオ | ✅ 完成 |
| ⚙️ サービス実装 | - | TalentManagementService（インバスケット生成、シミュレーション、割当） | ✅ 完成 |
| 🔌 APIルート | `GET /api/talent/units` | 全ユニット定義・インバスケット・メンバー管理・シミュレーション | ✅ 完成 |
| 📚 ドキュメント | - | 部門ミッション、RACIテンプレ、P&Lテンプレ、契約ワークフロー | ✅ 完成 |
| 🎫 Issuesテンプレ | - | 自動生成Issuesテンプレート（RACI定義、タスク作成等） | ✅ 完成 |

## 🎯 フェーズ1（AI秘書）実装状況

### ✅ 実装済み機能

| 機能 | API エンドポイント | 説明 | ステータス |
|------|---|---|---|
| 📊 週次レポート | `GET /api/weekly-report` | 今週のタスク状況を自動集計 | ✅ 完成 |
| 👥 1on1準備資料 | `GET /api/oneonone/{member_id}` | メンバーの1on1準備資料を自動生成 | ✅ 完成 |
| 📋 会議アジェンダ | `GET /api/agenda/weekly` | 会議の議題・リスク・決定事項を自動構成 | ✅ 完成 |
| 🎯 フォローアップ推奨 | `GET /api/recommendations/followup` | フォローすべき3名を自動推奨 | ✅ 完成 |
| 🧠 リーダーシップシミュレーション | `POST /api/leadership/start` | 次世代育成シナリオの対話型シミュレーション | ✅ 完成 |
| 🤖 Enterprise Autopilot | `POST /api/enterprise-autopilot/run` | 未来シナリオから戦略指示を生成し履歴化する周期型オーケストレーション | ✅ 実装 |
| 🏛️ Executive Simulation | `POST /api/executive-simulation/run` | AI 役員ロールによる経営会議をシミュレーションし合意戦略とコンセンサスを出力 | ✅ 実装 |

### 📁 プロジェクト構成

```
ai-executive-system/
├── .github/
│   └── copilot-instructions.md
├── docs/
│   ├── phase1-ai-secretary-spec.md       (更新済み)
│   ├── power-automate-integration.md     (新規)
│   └── phase0.5/
│       ├── talent_management_README.md   (Phase 0.5)
│       └── issues_template.md            (Phase 0.5)
├── src/backend/app/
│   ├── models/
│   │   ├── task.py
│   │   ├── member.py
│   │   ├── agenda.py
│   │   ├── recommendation.py
│   │   ├── business.py                    (Phase 0)
│   │   ├── organization.py               (Phase 0)
│   │   ├── business_strategy.py          (Phase 0)
│   │   └── talent_management.py          (Phase 0.5)
│   │   └── leadership/
│   │       └── simulation.py             (Phase 1.5)
│   ├── services/
│   │   ├── weekly_report_service.py
│   │   ├── oneonone_service.py
│   │   ├── agenda_service.py
│   │   ├── recommendation_service.py
│   │   ├── business_service.py           (Phase 0)
│   │   ├── organization_service.py       (Phase 0)
│   │   ├── business_strategy_service.py  (Phase 0)
│   │   └── talent_management_service.py  (Phase 0.5)
│   │   └── leadership/
│   │       └── simulation_service.py     (Phase 1.5)
│   ├── routes/
│   │   ├── weekly_report.py
│   │   ├── oneonone.py
│   │   ├── agenda.py
│   │   ├── recommendation.py
│   │   ├── business.py                   (Phase 0)
│   │   ├── organization.py              (Phase 0)
│   │   ├── business_strategy.py         (Phase 0)
│   │   ├── business_strategy_definition.py (Phase 0)
│   │   └── talent_management.py         (Phase 0.5)
│   │   └── leadership.py                 (Phase 1.5)
│   └── main.py                           (FastAPI)
├── data/samples/
│   ├── tasks.json
│   ├── members.json
│   ├── business_horipro.json            (Phase 0)
│   ├── organization_horipro.json        (Phase 0)
│   ├── business_strategy_horipro.json   (Phase 0)
│   ├── business_strategy_definition_horipro.json (Phase 0)
│   ├── talent_management_units.json     (Phase 0.5)
│   ├── talent_management_tasks.json     (Phase 0.5)
│   └── talent_management_incidents.json (Phase 0.5)
│   └── leadership_scenarios.json        (Phase 1.5)
├── config/
│   └── settings.example.yaml
├── scripts/
│   └── dev-start.bat
├── templates/
│   ├── raci/
│   │   └── talent_raci_template.md       (Phase 0.5)
│   ├── pl/
│   │   └── 案件P&L-template_talent.xlsx.md (Phase 0.5)
│   └── process/
│       └── contract_workflow.md          (Phase 0.5)
├── requirements.txt
└── README.md
```

## システム構成の概要

システムは3レイヤ構造を採用：
- **インターフェースレイヤー**: Web UI（シンプルな指示入力・出力表示）。
- **オーケストレーションレイヤー**: PythonベースのAI機能（フェーズ1: AI秘書、将来的に育成・予算エージェント）。
- **データ連携レイヤー**: 手動入力＋ローカルファイル（将来的にAPI連携）。

## フェーズ1の位置づけ

フェーズ1（AI秘書）は、日常業務支援のPoCとして、スケジュール管理、タスク管理、ドキュメント生成などを提供。ローカル完結で実装し、将来的拡張を前提とする。

## 🚀 クイックスタート

### セットアップ

```bash
# 1. 依存パッケージをインストール
pip install -r requirements.txt

# 2. サーバを起動
python -m src.backend.app.main
```

### API テスト

```bash
# 週次レポート取得
curl http://127.0.0.1:8000/api/weekly-report

# メンバーID 1 の1on1準備資料
curl http://127.0.0.1:8000/api/oneonone/1

# 会議アジェンダ取得
curl http://127.0.0.1:8000/api/agenda/weekly

# フォローアップメンバー推奨
curl http://127.0.0.1:8000/api/recommendations/followup
```

## 📚 ドキュメント

- [Phase 1 AI Secretary Spec](docs/phase1-ai-secretary-spec.md) - フェーズ1の仕様書 (更新)
- [Power Automate Integration Guide](docs/power-automate-integration.md) - Outlook自動送信ガイド (新規)
- [Phase 1 会社経営モデル](docs/phase1/company_operating_model.md) - 年間PL・季節性・キャッシュフロー設計
- [Phase 2.5 会社×オペレーション統合](docs/phase2/company_operations_integration.md) - PL とオペレーションの一括シミュレーション
- [Phase 3 中期戦略モデル](docs/phase3/midterm_strategy_model.md) - 中期戦略とギャップ分析
- [Phase 4 オペレーション課題モデル](docs/phase4/operational_issues_model.md) - 課題検知と改善タスク生成
- [Phase 5 AI改善ループ](docs/phase5/improvement_cycle_model.md) - 課題検知から優先度最適化までの継続改善
- [Phase 6 Executive Dashboard](docs/phase6/executive_dashboard.md) - 経営ダッシュボード API
- [AI Board Governance Layer](docs/ai_board_governance.md) - AI CEO の意思決定を取締役会視点でレビュー
- [Phase 8 External Environment Model](docs/phase8/external_environment_model.md) - 外部環境と市場トレンドモデル
- [Phase 9 Corporate Fundamentals Model](docs/phase9/corporate_fundamentals_model.md) - 企業ファンダメンタルズと事業影響モデル
- [Final Integration & Operation Guide](docs/final/system_overview.md) - システム全体と運用ガイド
- [Phase1〜4 経営モデル構築ロードマップ](docs/phase1-4_company_operating_model_roadmap.md) - 経営シミュレーションの全体設計図
- Vision & Goals（準備中）
- Scope and Phases（準備中）
- Backlog（準備中）

## 🔄 次のステップ

### Phase 1.5（4月予定）
- [ ] Power Automate 連携実装（毎朝・毎週自動実行）
- [ ] Outlook メール自動送信テスト
- [ ] メッセージドラフト生成機能

### Phase 2（5月以降）
- [ ] LLM（OpenAI）連携による品質向上
- [ ] 人材育成エージェント基盤構築
- [ ] 育成計画自動生成

## 💡 AI秘書の働き方

```
毎朝 8:30
  ↓
フォローすべき3名をメール通知
  ↓
毎週月曜 8:00
  ↓
週次レポートをメール送付
  ↓
会議前日 18:00
  ↓
会議アジェンダを自動生成・送付
  ↓
1on1 前日 18:00
  ↓
メンバー別準備資料を生成・送付
```

すべて Power Automate で自動化可能。詳細は [Power Automate Integration Guide](docs/power-automate-integration.md) を参照。

## 貢献

リードアーキテクト兼実装エンジニアとして、GitHub Copilotと連携して開発を進める。