# 🚀 AI Executive System 移植プロジェクト - 実行ガイド

**作成日**: 2026-06-07  
**ステータス**: 実行準備完了  
**対象**: AI Executive System v1 → v2 完全移植

---

## 📌 プロジェクト概要

このドキュメントは、AI Executive System（企業人格OS）全体を GitHub 経由で新リポジトリへ完全移植するための **実行計画書** です。

### 移植対象（10ステップ全実装）

| ステップ | コンポーネント | 実装状況 |
|---------|------------|--------|
| AE | Corporate Consciousness (企業意識) | ✅ 完了 |
| AF | Consciousness Evolution (意識進化) | ✅ 完了 |
| AG | Narrative Intelligence (物語知能) | ✅ 完了 |
| AH | Corporate Memory (企業記憶) | ✅ 完了 |
| AI | Meta-Cognition (メタ認知) | ✅ 完了 |
| AJ | Scenario Simulation (シナリオシミュレーション) | ✅ 完了 |
| AK | Multi-Company Comparative Intelligence (多企業比較知能) | ✅ 完了 |
| AL | Strategy Engine 2.0 (戦略エンジン) | ✅ 完了 |
| AM | Enterprise Autopilot (企業自動操縦) | ✅ 完了 |
| AN | Executive Simulation Engine (幹部シミュレーション) | ✅ 完了 |

---

## 🎯 移植戦略：5 レイヤー構成

### レイヤー 1：コードベース移植
```
src/backend/app/
├── models/ (40+ ドメインモデル)
├── services/ (20+ ビジネスロジック)
├── routes/ (30+ API エンドポイント)
├── repositories/ (JSON 永続化)
└── main.py (FastAPI エントリポイント)
```

**成果物**: src/ ディレクトリ全体が新リポジトリに移植される

### レイヤー 2：テスト移植
```
tests/
├── test_corporate_memory_*.py
├── test_meta_cognition_*.py
├── test_scenario_simulation_*.py
├── test_multi_company_comparative_*.py
├── test_strategy_engine_v2_*.py
├── test_enterprise_autopilot_*.py
└── test_executive_simulation_*.py
```

**成功条件**: 40+ テスト全て PASS

### レイヤー 3：データ移植
```
data/
├── corporate_memory/ (企業記憶データ)
├── scenario_simulation/ (シナリオ結果)
├── multi_company_comparison/ (比較分析)
├── strategy_engine_v2/ (戦略出力)
├── enterprise_autopilot/ (自動化サイクル)
└── executive_simulation/ (シミュレーション ログ)
```

**対象**: テストデータ & サンプルデータ

### レイヤー 4：ドキュメント移植
```
docs/
├── *-overview.md (各ステップの説明)
├── executive-meeting-api.yaml
├── architecture/ (アーキテクチャドキュメント)
└── ... (30+ ドキュメント)
```

**対象**: 全ドキュメント & README 更新

### レイヤー 5：CI/CD 設定
```
.github/workflows/
└── test.yml (pytest 自動実行)
```

**対象**: GitHub Actions 設定

---

## 🚀 実行フロー（図解）

```
┌─────────────────────────────────────────────────┐
│   Phase 1: 環境準備                             │
│   - git / Python 確認                           │
│   - GitHub リポジトリ作成                       │
│   - develop ブランチ作成                        │
└──────────────────┬──────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────┐
│   Phase 2: コードベース移植                      │
│   - src/ をコピー                               │
│   - scripts/ をコピー                           │
│   - requirements.txt 同期                       │
│   - App インポートテスト                        │
└──────────────────┬──────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────┐
│   Phase 3: データ移植                           │
│   - data/ 全体をコピー                          │
│   - Corporate Memory テスト                     │
└──────────────────┬──────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────┐
│   Phase 4: テストスイート移植                   │
│   - tests/ をコピー                             │
│   - 依存関係インストール                        │
│   - pytest 全テスト実行 ✅ PASS                 │
└──────────────────┬──────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────┐
│   Phase 5: ドキュメント移植                     │
│   - docs/ をコピー                              │
│   - README 更新                                 │
└──────────────────┬──────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────┐
│   Phase 6: CI/CD 設定                           │
│   - GitHub Actions ワークフロー                 │
└──────────────────┬──────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────┐
│   Phase 7: 最終確認 & PR マージ                 │
│   - API 疎通確認                                │
│   - ダッシュボード確認                          │
│   - main へマージ                               │
└─────────────────────────────────────────────────┘
```

---

## 💻 実行方法

### 前提条件

- [ ] GitHub アカウント
- [ ] git インストール
- [ ] Python 3.11 以上
- [ ] SSH キー設定 (GitHub)

### 方法 A：自動スクリプト実行（推奨）

#### Windows (PowerShell):

```powershell
# スクリプトを実行
powershell -ExecutionPolicy Bypass -File scripts/migrate.ps1

# または GitHub ユーザー名を指定
powershell -ExecutionPolicy Bypass -File scripts/migrate.ps1 -GitHubUsername YOUR_USERNAME
```

#### macOS / Linux (Bash):

```bash
# スクリプトを実行
bash scripts/migrate.sh YOUR_USERNAME
```

**所要時間**: 約 10-15 分

---

### 方法 B：手動実行（ステップバイステップ）

#### Step 1: 環境準備

```bash
# GitHub にリポジトリを作成
# https://github.com/new
# 名前: ai-executive-system-v2
# Visibility: Private

# ローカルに clone
git clone git@github.com:YOUR_USERNAME/ai-executive-system-v2.git
cd ai-executive-system-v2

# develop ブランチを作成
git checkout -b develop
git push -u origin develop
```

#### Step 2: コードベース移植

```bash
# src / scripts / 依存ファイルをコピー
cp -r ../ai-executive-system/src ./src
cp -r ../ai-executive-system/scripts ./scripts
cp ../ai-executive-system/requirements.txt .
cp ../ai-executive-system/pyproject.toml .

# App インポート確認
python -c "import sys; sys.path.insert(0, '.'); from src.backend.app.main import app; print('✅ OK')"

# コミット
git add src/ scripts/ requirements.txt pyproject.toml
git commit -m "feat: Migrate codebase"
git push origin develop
```

#### Step 3: データ移植

```bash
cp -r ../ai-executive-system/data ./data

git add data/
git commit -m "feat: Migrate data"
git push origin develop
```

#### Step 4: テスト移植

```bash
cp -r ../ai-executive-system/tests ./tests

pip install -r requirements.txt
python -m pytest tests/ -q  # 全テスト PASS を確認

git add tests/
git commit -m "feat: Migrate tests"
git push origin develop
```

#### Step 5: ドキュメント移植

```bash
cp -r ../ai-executive-system/docs ./docs

# README 更新（MIGRATION_PLAN.md の Issue 5 参照）

git add docs/ README.md
git commit -m "docs: Migrate documentation"
git push origin develop
```

#### Step 6: CI/CD 設定

```bash
mkdir -p .github/workflows

# test.yml を作成（MIGRATION_PLAN.md の Issue 6 参照）

git add .github/
git commit -m "ci: Add GitHub Actions"
git push origin develop
```

#### Step 7: PR 作成

```bash
# GitHub UI で PR を作成
# develop → main
# レビュー後に merge
```

---

## ✅ 最終チェックリスト

移植完了後、以下を確認：

### API 動作確認

```bash
# FastAPI を起動
python -m uvicorn src.backend.app.main:app --reload --port 12000 &

# API テスト
curl -X POST http://localhost:12000/api/meta-cognition/run
curl -X POST http://localhost:12000/api/scenarios/run/BASELINE
curl -X POST http://localhost:12000/api/strategy/v2/run/BASELINE
curl -X POST http://localhost:12000/api/enterprise-autopilot/run
curl -X POST http://localhost:12000/api/executive-simulation/run
```

### ダッシュボード確認

```bash
curl http://localhost:12000/api/dashboard/summary
```

### テスト確認

```bash
pytest tests/ -q

# 期待結果: 40+ passed
```

### 最終チェックリスト

- [ ] 全 API が 200 を返す
- [ ] ダッシュボード summary が全項目を返す
- [ ] Autopilot が 1 サイクル正常に動く
- [ ] Executive Simulation が動作する
- [ ] Corporate Memory に記録される
- [ ] **全テスト PASS (40+ テスト)**
- [ ] README が新環境に対応
- [ ] GitHub Actions テストが自動実行

---

## 📂 ファイル構成

移植プロジェクトに含まれるドキュメント：

```
ai-executive-system/
├── MIGRATION_PLAN.md (← メイン移植計画)
├── GITHUB_ISSUES_TEMPLATES.md (← Issue テンプレート)
├── MIGRATION_GUIDE.md (← このファイル)
├── scripts/
│   ├── migrate.ps1 (← Windows 自動スクリプト)
│   └── migrate.sh (← Bash 自動スクリプト)
└── ...
```

---

## 🆘 トラブルシューティング

### 問題 1: Clone 失敗

```
fatal: Could not read from remote repository
```

**解決**:
```bash
# SSH キーを確認
ssh -T git@github.com

# キーがない場合は生成
ssh-keygen -t ed25519 -C "your-email@example.com"

# GitHub に公開鍵を追加
# https://github.com/settings/keys
```

### 問題 2: Import エラー

```
ModuleNotFoundError: No module named 'src'
```

**解決**:
```bash
# PYTHONPATH を設定
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# または Python パスに . を追加
python -c "import sys; sys.path.insert(0, '.'); from src.backend.app.main import app"
```

### 問題 3: テスト失敗

```
ERROR: not found: tests/test_*.py
```

**解決**:
```bash
# 依存関係を再インストール
pip install --force-reinstall -r requirements.txt

# キャッシュをクリア
find . -type d -name __pycache__ -exec rm -rf {} +
pytest --cache-clear tests/
```

---

## 📞 サポート情報

| 項目 | 情報 |
|-----|-----|
| 移植スクリプト | scripts/migrate.ps1 (Windows) / migrate.sh (Bash) |
| 移植計画 | MIGRATION_PLAN.md |
| Issue テンプレート | GITHUB_ISSUES_TEMPLATES.md |
| 所要時間 | 約 10-15 分（自動スクリプト） |
| テスト数 | 40+ |

---

## 🎉 移植完了後のアクション

### オプション 1：CI/CD 強化

```bash
# linting ツールを追加
pip install flake8 black mypy

# GitHub Actions に追加
# .github/workflows/lint.yml
```

### オプション 2：運用モード設定

```bash
# Autopilot スケジューラーを実装
python scripts/run_market_scenarios.py

# 定期実行ジョブを設定
# (cron / GitHub Actions Scheduled Events)
```

### オプション 3：Executive Simulation 強化

```bash
# 役員個性モデルを実装
# src/backend/app/services/executive_personality_engine.py

# シミュレーション結果分析を追加
# src/backend/app/services/simulation_analytics_engine.py
```

---

## 📝 チェックリスト

移植プロジェクト全体のチェックリスト：

```markdown
## 移植前準備
- [ ] GitHub リポジトリ ai-executive-system-v2 作成
- [ ] SSH キー設定確認
- [ ] Python 3.11+ インストール確認
- [ ] git インストール確認

## 移植実行
- [ ] 自動スクリプト実行 OR 手動ステップ実行
- [ ] Phase 1-6 すべて完了
- [ ] コミット & push 確認

## 最終確認
- [ ] 全 API が 200 を返す
- [ ] ダッシュボード summary が全項目を返す
- [ ] Autopilot が 1 サイクル正常に動く
- [ ] Executive Simulation が動作する
- [ ] Corporate Memory に記録される
- [ ] 全テスト PASS (40+ テスト)
- [ ] README が新環境に対応
- [ ] GitHub Actions テストが自動実行

## 移植後アクション
- [ ] PR を作成
- [ ] GitHub Actions テストが自動実行
- [ ] レビュー & merge
- [ ] main ブランチがリリース版

## オプション
- [ ] CI/CD 強化 (flake8, black, mypy)
- [ ] 運用モード設定（スケジューラー）
- [ ] Executive Simulation 強化
```

---

## 📊 移植パフォーマンス

| フェーズ | 内容 | 所要時間 |
|---------|------|--------|
| Phase 1 | 環境準備 | 2-3 分 |
| Phase 2 | コードベース移植 | 1-2 分 |
| Phase 3 | データ移植 | 30 秒 |
| Phase 4 | テスト移植 & 実行 | 5-7 分 |
| Phase 5 | ドキュメント移植 | 1 分 |
| Phase 6 | CI/CD 設定 | 1 分 |
| Phase 7 | 最終確認 | 2 分 |
| **合計** | **全フェーズ** | **12-16 分** |

---

**バージョン**: 1.0  
**最終更新**: 2026-06-07  
**ステータス**: 実行準備完了  
**次のアクション**: 自動スクリプト実行 OR 手動ステップ実行
