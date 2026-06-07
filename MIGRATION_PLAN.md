# 🚀 AI Executive System 完全移植計画 & 実行指示書

**バージョン**: 1.0  
**作成日**: 2026-06-07  
**対象**: AI Executive System (企業人格OS) 全体の新リポジトリへの完全移植

---

## 📋 目的

以下 10 ステップの完全実装を、新リポジトリ (`ai-executive-system-v2`) へ GitHub 経由で完全移植する：

| ステップ | コンポーネント | ステータス |
|---------|------------|---------|
| AE | Corporate Consciousness | ✅ 実装済 |
| AF | Consciousness Evolution | ✅ 実装済 |
| AG | Narrative Intelligence | ✅ 実装済 |
| AH | Corporate Memory | ✅ 実装済 |
| AI | Meta‑Cognition | ✅ 実装済 |
| AJ | Scenario Simulation | ✅ 実装済 |
| AK | Multi‑Company Comparative Intelligence | ✅ 実装済 |
| AL | Strategy Engine 2.0 | ✅ 実装済 |
| AM | Enterprise Autopilot | ✅ 実装済 |
| AN | Executive Simulation Engine | ✅ 実装済 |

---

## 🎯 移植の 5 レイヤー構成

### 1️⃣ コードベース移植
- `/src/backend/app/models/*` (40+ ドメインモデル)
- `/src/backend/app/services/*` (20+ ビジネスロジックサービス)
- `/src/backend/app/routes/*` (30+ API ルート)
- `/src/backend/app/repositories/*` (JSON 永続層)
- `/src/backend/app/dashboard/*` (ダッシュボード集約)
- `/src/backend/app/main.py` (FastAPI エントリポイント)

### 2️⃣ データ移植
- `/data/corporate_memory/*.json` (企業記憶)
- `/data/scenario_simulation/*.json` (シナリオ結果)
- `/data/multi_company_comparison/*.json` (比較分析)
- `/data/strategy_engine_v2/*.json` (戦略出力)
- `/data/enterprise_autopilot/*.json` (自動化サイクル)
- `/data/executive_simulation/*.json` (シミュレーション ログ)

### 3️⃣ テスト移植
- `tests/test_corporate_memory_*` (企業記憶テスト)
- `tests/test_meta_cognition_*` (メタ認知テスト)
- `tests/test_scenario_simulation_*` (シナリオテスト)
- `tests/test_multi_company_comparative_*` (比較分析テスト)
- `tests/test_strategy_engine_v2_*` (戦略エンジンテスト)
- `tests/test_enterprise_autopilot_*` (自動化テスト)
- `tests/test_executive_simulation_*` (シミュレーション テスト)

### 4️⃣ ドキュメント移植
- `docs/*` (全 Overview.md)
- `README.md` (プロジェクト説明)
- `architecture_docs/` (アーキテクチャドキュメント)

### 5️⃣ CI/CD & 実行環境
- `requirements.txt` (Python 依存関係)
- `.github/workflows/` (GitHub Actions)
- `pyproject.toml` (プロジェクト設定)
- `scripts/` (実行スクリプト)

---

## 🔧 GitHub 実行ステップ（Issue ベース）

### Issue 1：新リポジトリの作成

**タイトル**: `[Migration] 新リポジトリ ai-executive-system-v2 の作成`

**チェックリスト**:
- [ ] GitHub で `ai-executive-system-v2` リポジトリを作成
- [ ] リポジトリ概要：
  - **Description**: "AI Executive System v2 - Complete Migration of Corporate Consciousness Engine"
  - **Visibility**: Private (or Public)
- [ ] ブランチ保護設定：
  - `main` ブランチ：PR 必須
  - `develop` ブランチ：PR 推奨
- [ ] DEFAULT_BRANCH を `main` に設定
- [ ] `develop` ブランチを作成

**実行コマンド**:
```bash
# リポジトリ URL (後述)
```

---

### Issue 2：コードベースの移植

**タイトル**: `[Migration] コードベース全体を新リポジトリへ移植`

**移植対象**:
```
旧リポジトリ (ai-executive-system)
  ├─ src/backend/app/
  │   ├─ models/ (40+ 実装)
  │   ├─ services/ (20+ 実装)
  │   ├─ routes/ (30+ 実装)
  │   ├─ repositories/ (JSON 永続層)
  │   └─ main.py
  ├─ requirements.txt
  ├─ pyproject.toml
  └─ scripts/
```

**実行手順**:

```bash
# Step 1: 新リポジトリを clone
git clone git@github.com:YOUR_USERNAME/ai-executive-system-v2.git
cd ai-executive-system-v2

# Step 2: develop ブランチに切り替え
git checkout develop

# Step 3: 旧リポジトリからコードベースをコピー
cp -R ../ai-executive-system/src ./src
cp ../ai-executive-system/requirements.txt .
cp ../ai-executive-system/pyproject.toml .
cp -R ../ai-executive-system/scripts ./scripts

# Step 4: コミット & push
git add src/ requirements.txt pyproject.toml scripts/
git commit -m "feat: Initial migration of codebase (models/services/routes)"
git push origin develop

# Step 5: コード品質チェック
cd src/backend/app
python -m py_compile main.py
python -c "import sys; sys.path.insert(0, '../../..'); from src.backend.app.main import app; print('✅ App imported successfully')"
```

**確認項目**:
- [ ] `src/backend/app/main.py` が正常にインポートされる
- [ ] 全ルートが登録されている (check `app.routes`)
- [ ] `requirements.txt` が完全
- [ ] IDE に Import Error がない

---

### Issue 3：データ移植（必要な場合のみ）

**タイトル**: `[Migration] テストデータ & サンプルデータの移植`

**移植対象**:
```
data/
  ├─ corporate_memory/
  ├─ scenario_simulation/
  ├─ multi_company_comparison/
  ├─ strategy_engine_v2/
  ├─ enterprise_autopilot/
  └─ executive_simulation/
```

**実行手順**:

```bash
# Step 1: data/ ディレクトリ構造をコピー
mkdir -p data
cp -R ../ai-executive-system/data/* ./data/

# Step 2: ID 衝突チェック & 再生成（必要に応じて）
python scripts/check_data_migrations.py

# Step 3: Corporate Memory 読み込みテスト
python -c "
from src.backend.app.services.corporate_memory_repository import CorporateMemoryRepository
repo = CorporateMemoryRepository()
memories = repo.list_all()
print(f'✅ Loaded {len(memories)} corporate memories')
"

# Step 4: コミット
git add data/
git commit -m "feat: Migrate test and sample data"
git push origin develop
```

**確認項目**:
- [ ] JSON ファイルが正常にロードされる
- [ ] Corporate Memory に記録が存在する
- [ ] ID 衝突がない

---

### Issue 4：テストスイートの移植

**タイトル**: `[Migration] テストスイート全体を移植 & 実行確認`

**移植対象**:
```
tests/
  ├─ test_corporate_memory_*
  ├─ test_meta_cognition_*
  ├─ test_scenario_simulation_*
  ├─ test_multi_company_comparative_*
  ├─ test_strategy_engine_v2_*
  ├─ test_enterprise_autopilot_*
  └─ test_executive_simulation_*
```

**実行手順**:

```bash
# Step 1: テストファイルをコピー
cp -R ../ai-executive-system/tests ./tests

# Step 2: 依存関係をインストール
pip install -r requirements.txt

# Step 3: 全テスト実行
python -m pytest tests/ -v --tb=short 2>&1 | tee pytest_results.txt

# Step 4: テスト結果の概要を取得
python -m pytest tests/ -q

# Step 5: コミット
git add tests/
git commit -m "feat: Migrate complete test suite (40+ tests)"
git push origin develop
```

**成功条件**:
- [ ] **全テスト PASS** (40+ テスト)
- [ ] エラーレート: 0%
- [ ] カバレッジ: 80%+

**想定テスト数**: 40+ テスト

---

### Issue 5：ドキュメント移植

**タイトル**: `[Migration] ドキュメント全体を新リポジトリへ移植`

**移植対象**:
```
docs/
  ├─ corporate-memory-overview.md
  ├─ meta-cognition-overview.md
  ├─ scenario-simulation-overview.md
  ├─ multi-company-comparative-overview.md
  ├─ strategy-engine-v2-overview.md
  ├─ enterprise-autopilot-overview.md
  ├─ executive-simulation-overview.md
  ├─ emergency-playbook-overview.md
  └─ ... (他 30+ ファイル)
```

**実行手順**:

```bash
# Step 1: ドキュメントをコピー
cp -R ../ai-executive-system/docs ./docs

# Step 2: README を新しいリポジトリ向けに更新
cat > README.md << 'EOF'
# AI Executive System v2

**企業人格 OS 完全実装版** - Corporate Consciousness Engine

## 概要

このシステムは、以下 10 ステップの完全実装を含む企業人格 AI プラットフォームです：

- **AE**: Corporate Consciousness (企業意識)
- **AF**: Consciousness Evolution (意識進化)
- **AG**: Narrative Intelligence (物語知能)
- **AH**: Corporate Memory (企業記憶)
- **AI**: Meta-Cognition (メタ認知)
- **AJ**: Scenario Simulation (シナリオシミュレーション)
- **AK**: Multi-Company Comparative Intelligence (多企業比較知能)
- **AL**: Strategy Engine 2.0 (戦略エンジン)
- **AM**: Enterprise Autopilot (企業自動操縦)
- **AN**: Executive Simulation Engine (幹部シミュレーションエンジン)

## クイックスタート

```bash
# 依存関係をインストール
pip install -r requirements.txt

# 開発サーバーを起動
uvicorn src.backend.app.main:app --reload --port 12000

# API ドキュメント
# http://localhost:12000/docs
```

## テスト実行

```bash
pytest tests/ -q
```

## ドキュメント

- [詳細アーキテクチャ](docs/)
- [API リファレンス](docs/executive-meeting-api.yaml)
- [ビジネス戦略概要](docs/strategy-engine-2.0-overview.md)

## 移植完了

✅ **Migration Status**: 完全移植 (v2 Initial Release)
- Codebase: ✅ 完全移植
- Tests: ✅ 全 40+ テスト PASS
- Data: ✅ 移植完了
- Docs: ✅ 完全移植

---

**リリース日**: 2026-06-07  
**バージョン**: 2.0
EOF

# Step 3: パス修正を実行
python scripts/fix_doc_paths.py

# Step 4: コミット
git add docs/ README.md
git commit -m "docs: Migrate complete documentation suite"
git push origin develop
```

**確認項目**:
- [ ] 全 Overview.md がコピーされている
- [ ] README が新リポジトリに対応
- [ ] パス修正が完了

---

### Issue 6：CI/CD 設定（GitHub Actions）

**タイトル**: `[Migration] GitHub Actions 自動テスト設定`

**実行手順**:

```bash
# Step 1: .github/workflows/ ディレクトリを作成
mkdir -p .github/workflows

# Step 2: pytest 自動テストワークフローを作成
cat > .github/workflows/test.yml << 'EOF'
name: pytest

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: python -m pytest tests/ -v --tb=short
EOF

# Step 3: コミット
git add .github/
git commit -m "ci: Add GitHub Actions pytest workflow"
git push origin develop
```

---

## 💻 実行コマンド群（ターミナルで順番に実行）

### Phase 1：環境準備

```bash
# 1. 新リポジトリを clone
git clone git@github.com:YOUR_USERNAME/ai-executive-system-v2.git
cd ai-executive-system-v2

# 2. develop ブランチに切り替え
git checkout develop

# 3. 現在の状態を確認
git status
git branch -a
```

### Phase 2：コードベース移植

```bash
# 1. src, scripts をコピー
cp -R ../ai-executive-system/src ./src
cp -R ../ai-executive-system/scripts ./scripts
cp ../ai-executive-system/requirements.txt .
cp ../ai-executive-system/pyproject.toml .

# 2. App が正常にインポートされるか確認
python -c "import sys; sys.path.insert(0, '.'); from src.backend.app.main import app; print('✅ App imported')"

# 3. コミット
git add src/ scripts/ requirements.txt pyproject.toml
git commit -m "feat: Migrate codebase (models/services/routes)"
git push origin develop
```

### Phase 3：データ移植

```bash
# 1. data/ をコピー
cp -R ../ai-executive-system/data ./data

# 2. Corporate Memory テスト
python -c "
from src.backend.app.services.corporate_memory_repository import CorporateMemoryRepository
repo = CorporateMemoryRepository()
print(f'✅ Loaded {len(repo.list_all())} memories')
"

# 3. コミット
git add data/
git commit -m "feat: Migrate test data"
git push origin develop
```

### Phase 4：テスト実行

```bash
# 1. 依存関係をインストール
pip install -r requirements.txt

# 2. 全テスト実行
python -m pytest tests/ -q

# 3. 詳細テスト結果
python -m pytest tests/ -v --tb=short

# 4. テスト結果を保存
python -m pytest tests/ -v > test_results.log
```

### Phase 5：ドキュメント移植

```bash
# 1. docs をコピー
cp -R ../ai-executive-system/docs ./docs

# 2. README を更新
# (上記の Issue 5 参照)

# 3. コミット
git add docs/ README.md
git commit -m "docs: Migrate complete documentation"
git push origin develop
```

### Phase 6：CI/CD 設定

```bash
# 1. GitHub Actions ワークフロー作成
mkdir -p .github/workflows
# (上記の Issue 6 参照)

# 2. コミット
git add .github/
git commit -m "ci: Add GitHub Actions workflows"
git push origin develop
```

### Phase 7：PR 作成 & main へマージ

```bash
# 1. develop から PR を作成（GitHub UI または gh CLI）
gh pr create --base main --head develop --title "feat: Complete migration of AI Executive System" --body "Migration of all 10 steps (AE-AN) from v1"

# 2. PR マージ（自動テストが PASS した後）
gh pr merge --auto --squash
```

---

## ✅ 移植後の動作確認

### 1️⃣ FastAPI 起動テスト

```bash
cd ai-executive-system-v2
python -m uvicorn src.backend.app.main:app --reload --port 12000 &
sleep 3
```

### 2️⃣ API 疎通確認

```bash
# Meta-Cognition
curl -X POST http://localhost:12000/api/meta-cognition/run -H "Content-Type: application/json"

# Scenario Simulation
curl -X POST http://localhost:12000/api/scenarios/run/BASELINE -H "Content-Type: application/json"

# Strategy Engine v2
curl -X POST http://localhost:12000/api/strategy/v2/run/BASELINE -H "Content-Type: application/json"

# Enterprise Autopilot
curl -X POST http://localhost:12000/api/enterprise-autopilot/run -H "Content-Type: application/json"

# Executive Simulation
curl -X POST http://localhost:12000/api/executive-simulation/run -H "Content-Type: application/json"
```

### 3️⃣ ダッシュボード概要確認

```bash
curl http://localhost:12000/api/dashboard/summary
```

### 4️⃣ テスト実行

```bash
python -m pytest tests/ -q
```

---

## 📊 最終チェックリスト

| 項目 | チェック |
|-----|--------|
| 全 API が 200 を返す | [ ] |
| ダッシュボード summary が全項目を返す | [ ] |
| Autopilot が 1 サイクル正常に動く | [ ] |
| Executive Simulation が動作する | [ ] |
| Corporate Memory に記録される | [ ] |
| 全テスト PASS (40+ テスト) | [ ] |
| README が新環境に対応 | [ ] |
| GitHub Actions テストが自動実行される | [ ] |

---

## 🚀 移植後のアクション

### オプション 1：CI/CD 強化
- [ ] flake8 / black / mypy を追加
- [ ] Code coverage レポート設定
- [ ] Dependabot 設定

### オプション 2：運用モード設定
- [ ] Autopilot スケジューラー実装
- [ ] 定期実行ジョブ設定
- [ ] モニタリング & アラート設定

### オプション 3：Executive Simulation 強化
- [ ] 役員個性モデル実装
- [ ] シミュレーション結果分析
- [ ] 意思決定支援ダッシュボード

---

## 📞 トラブルシューティング

### Import Error が発生する場合

```bash
# PYTHONPATH を確認
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -c "from src.backend.app.main import app"
```

### テストが失敗する場合

```bash
# 依存関係を再インストール
pip install --force-reinstall -r requirements.txt

# キャッシュをクリア
find . -type d -name __pycache__ -exec rm -rf {} +
pytest --cache-clear tests/
```

### データ移植後に ID 衝突がある場合

```python
# scripts/regenerate_data_ids.py で UUID を再生成
python scripts/regenerate_data_ids.py
```

---

## 📝 付録：コマンドシートまとめ

**移植全体を 1 つのスクリプトで実行** (オプション):

```bash
#!/bin/bash
# migrate.sh

set -e

echo "🚀 AI Executive System Migration Started"

# Phase 1: Setup
git clone git@github.com:YOUR_USERNAME/ai-executive-system-v2.git
cd ai-executive-system-v2
git checkout develop

# Phase 2: Code
cp -R ../ai-executive-system/src ./src
cp -R ../ai-executive-system/scripts ./scripts
cp ../ai-executive-system/requirements.txt .
cp ../ai-executable-system/pyproject.toml .
git add src/ scripts/ requirements.txt pyproject.toml
git commit -m "feat: Migrate codebase"
git push origin develop

# Phase 3: Data
cp -R ../ai-executive-system/data ./data
git add data/
git commit -m "feat: Migrate data"
git push origin develop

# Phase 4: Tests
cp -R ../ai-executive-system/tests ./tests
pip install -r requirements.txt
python -m pytest tests/ -q
git add tests/
git commit -m "feat: Migrate tests"
git push origin develop

# Phase 5: Docs
cp -R ../ai-executive-system/docs ./docs
git add docs/
git commit -m "docs: Migrate documentation"
git push origin develop

# Phase 6: CI/CD
mkdir -p .github/workflows
# (GitHub Actions ワークフロー作成)
git add .github/
git commit -m "ci: Add GitHub Actions"
git push origin develop

echo "✅ Migration Complete!"
```

---

**バージョン**: 1.0  
**最終更新**: 2026-06-07  
**ステータス**: 実行準備完了
