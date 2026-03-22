# AI幹部システム

## プロジェクト概要

このプロジェクトは、管理職であるユーザーのマネジメント業務（メンバー管理・人材育成・予算/事業性管理）をAIが日次〜年次の運用レベルで代行する「AI幹部システム」を構築することを目的とする。最終的に、ユーザーが意思決定と戦略・課題設定に専念できる状態を実現する。

## 🎯 フェーズ1（AI秘書）実装状況

### ✅ 実装済み機能

| 機能 | API エンドポイント | 説明 | ステータス |
|------|---|---|---|
| 📊 週次レポート | `GET /api/weekly-report` | 今週のタスク状況を自動集計 | ✅ 完成 |
| 👥 1on1準備資料 | `GET /api/oneonone/{member_id}` | メンバーの1on1準備資料を自動生成 | ✅ 完成 |
| 📋 会議アジェンダ | `GET /api/agenda/weekly` | 会議の議題・リスク・決定事項を自動構成 | ✅ 完成 |
| 🎯 フォローアップ推奨 | `GET /api/recommendations/followup` | フォローすべき3名を自動推奨 | ✅ 完成 |

### 📁 プロジェクト構成

```
ai-executive-system/
├── .github/
│   └── copilot-instructions.md
├── docs/
│   ├── phase1-ai-secretary-spec.md       (更新済み)
│   └── power-automate-integration.md     (新規)
├── src/backend/app/
│   ├── models/
│   │   ├── task.py
│   │   ├── member.py
│   │   ├── agenda.py
│   │   └── recommendation.py
│   ├── services/
│   │   ├── weekly_report_service.py
│   │   ├── oneonone_service.py
│   │   ├── agenda_service.py
│   │   └── recommendation_service.py
│   ├── routes/
│   │   ├── weekly_report.py
│   │   ├── oneonone.py
│   │   ├── agenda.py
│   │   └── recommendation.py
│   └── main.py                           (FastAPI)
├── data/samples/
│   ├── tasks.json
│   └── members.json
├── config/
│   └── settings.example.yaml
├── scripts/
│   └── dev-start.bat
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
- Vision & Goals（準備中）
- Scope and Phases（準備中）
- Roadmap（準備中）
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