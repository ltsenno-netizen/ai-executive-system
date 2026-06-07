# GitHub Issues テンプレート - AI Executive System 移植プロジェクト

## Issue 1：新リポジトリの作成

```markdown
# [Migration] 新リポジトリ ai-executive-system-v2 の作成

## 目的

AI Executive System の全 10 ステップ実装（AE～AN）を新リポジトリ `ai-executive-system-v2` で完全再構築する。

## 実行手順

### A. GitHub UI での操作

1. **GitHub にログイン** → https://github.com/new
2. **リポジトリ情報を入力**:
   - Repository name: `ai-executive-system-v2`
   - Description: "AI Executive System v2 - Complete Migration of Corporate Consciousness Engine"
   - Visibility: **Private** (変更可能)
   - Initialize with: `Add a README file` (チェック)
   
3. **Create repository** をクリック

### B. ローカル環境で設定

```bash
# リポジトリを clone
git clone git@github.com:YOUR_USERNAME/ai-executive-system-v2.git
cd ai-executive-system-v2

# develop ブランチを作成
git checkout -b develop
git push -u origin develop

# ブランチ保護設定（GitHub UI）
# Settings → Branches → Add rule:
# - Branch name: main
# - Require pull request reviews before merging: ✓
# - Require status checks to pass: ✓
```

## チェックリスト

- [ ] リポジトリが作成されている
- [ ] `develop` ブランチが作成されている
- [ ] `main` ブランチが保護されている
- [ ] README が存在する

## 関連 Issue

- Issue 2: コードベースの移植
```

---

## Issue 2：コードベースの移植

```markdown
# [Migration] コードベース全体を新リポジトリへ移植

## 目的

旧リポジトリ `ai-executive-system` から以下を新リポジトリへ移植：
- src/backend/app/ 全体
- requirements.txt / pyproject.toml
- scripts/

## 移植対象

```
src/backend/app/
├── models/ (40+ ドメインモデル)
├── services/ (20+ ビジネスロジック)
├── routes/ (30+ API ルート)
├── repositories/ (JSON 永続層)
├── dashboard/ (ダッシュボード)
└── main.py
```

## 実行手順

```bash
# Step 1: develop ブランチに切り替え
git checkout develop

# Step 2: 旧リポジトリからコードをコピー
cp -R ../ai-executive-system/src ./src
cp -R ../ai-executive-system/scripts ./scripts
cp ../ai-executive-system/requirements.txt .
cp ../ai-executive-system/pyproject.toml .

# Step 3: App インポートテスト
python -c "import sys; sys.path.insert(0, '.'); from src.backend.app.main import app; print('✅ App imported successfully')"

# Step 4: コミット & Push
git add src/ scripts/ requirements.txt pyproject.toml
git commit -m "feat: Migrate codebase (models/services/routes)"
git push origin develop

# Step 5: ルート登録を確認
python << 'EOF'
import sys
sys.path.insert(0, '.')
from src.backend.app.main import app

# ルート一覧を表示
routes = [
    (route.path, route.name)
    for route in app.routes
    if hasattr(route, 'path')
]
print(f"\n✅ Total Routes: {len(routes)}")
for path, name in routes[:10]:
    print(f"  {path} -> {name}")
print("  ...")
EOF
```

## 確認項目

- [ ] src/backend/app が正常にコピーされている
- [ ] main.py がインポート可能
- [ ] 全ルートが登録されている (30+ ルート)
- [ ] requirements.txt が完全
- [ ] IDE に Import Error がない

## 成功条件

✅ App が正常にインポートされる  
✅ 全ルート登録が完了  
✅ 依存関係が解決されている

## 関連 Issue

- Issue 1: 新リポジトリの作成 (前提)
- Issue 3: データ移植 (次)
```

---

## Issue 3：テストスイートの移植

```markdown
# [Migration] テストスイート全体を移植 & 実行確認

## 目的

40+ のテストスイートを完全に移植し、全テスト PASS を確認する。

## 移植対象

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

## 実行手順

```bash
# Step 1: テストスイートをコピー
cp -R ../ai-executive-system/tests ./tests

# Step 2: 依存関係をインストール
pip install -r requirements.txt

# Step 3: 全テスト実行（詳細）
python -m pytest tests/ -v --tb=short

# Step 4: 全テスト実行（簡潔）
python -m pytest tests/ -q

# Step 5: テスト結果をファイルに保存
python -m pytest tests/ -v --tb=short > test_results.txt 2>&1

# Step 6: コミット
git add tests/
git commit -m "feat: Migrate complete test suite (40+ tests)"
git push origin develop
```

## 確認項目

- [ ] 全テストがコピーされている
- [ ] 全テスト PASS (40+ テスト)
- [ ] エラーレート: 0%
- [ ] カバレッジ: 80%+

## 成功条件

```
✅ 40+ tests passed
✅ No errors
✅ Coverage >= 80%
```

## 関連 Issue

- Issue 2: コードベースの移植 (前提)
- Issue 4: データ移植 (並行)
```

---

## Issue 4：データ移植

```markdown
# [Migration] テストデータ & サンプルデータの移植

## 目的

corporate memory、シミュレーション結果など、必要なテストデータを移植する。

## 移植対象

```
data/
├── corporate_memory/ (企業記憶)
├── scenario_simulation/ (シナリオ結果)
├── multi_company_comparison/ (比較分析)
├── strategy_engine_v2/ (戦略出力)
├── enterprise_autopilot/ (自動化サイクル)
└── executive_simulation/ (シミュレーション ログ)
```

## 実行手順

```bash
# Step 1: data/ をコピー
cp -R ../ai-executive-system/data ./data

# Step 2: ID 衝突チェック（該当する場合）
# 新しい環境では通常 ID 衝突はないが、確認推奨

# Step 3: Corporate Memory 読み込みテスト
python << 'EOF'
import sys
sys.path.insert(0, '.')
from src.backend.app.services.corporate_memory_repository import CorporateMemoryRepository

repo = CorporateMemoryRepository()
memories = repo.list_all()
print(f"✅ Loaded {len(memories)} corporate memories")
EOF

# Step 4: コミット
git add data/
git commit -m "feat: Migrate test and sample data"
git push origin develop
```

## 確認項目

- [ ] data/ が完全にコピーされている
- [ ] JSON ファイルが正常にロードされる
- [ ] Corporate Memory に記録が存在する
- [ ] ID 衝突がない

## 関連 Issue

- Issue 3: テストスイートの移植 (並行)
- Issue 5: ドキュメント移植 (次)
```

---

## Issue 5：ドキュメント移植

```markdown
# [Migration] ドキュメント全体を新リポジトリへ移植

## 目的

30+ のドキュメントファイルを新リポジトリへ移植し、README を更新する。

## 移植対象

```
docs/
├── corporate-memory-overview.md
├── meta-cognition-overview.md
├── scenario-simulation-overview.md
├── multi-company-comparative-overview.md
├── strategy-engine-v2-overview.md
├── enterprise-autopilot-overview.md
├── executive-simulation-overview.md
├── phase1/ phase2/ ... phase12/ (アーキテクチャ)
└── ... (30+ ファイル)
```

## 実行手順

```bash
# Step 1: docs/ をコピー
cp -R ../ai-executive-system/docs ./docs

# Step 2: README を新しいリポジトリ向けに更新
# (下記のテンプレートを参照)

# Step 3: コミット
git add docs/ README.md
git commit -m "docs: Migrate complete documentation suite"
git push origin develop
```

## README テンプレート

```markdown
# AI Executive System v2

**企業人格 OS 完全実装版** - Corporate Consciousness Engine

## 概要

以下 10 ステップの完全実装を含む企業人格 AI プラットフォーム：

- **AE**: Corporate Consciousness
- **AF**: Consciousness Evolution
- **AG**: Narrative Intelligence
- **AH**: Corporate Memory
- **AI**: Meta-Cognition
- **AJ**: Scenario Simulation
- **AK**: Multi-Company Comparative Intelligence
- **AL**: Strategy Engine 2.0
- **AM**: Enterprise Autopilot
- **AN**: Executive Simulation Engine

## クイックスタート

\`\`\`bash
pip install -r requirements.txt
uvicorn src.backend.app.main:app --reload --port 12000
\`\`\`

## テスト

\`\`\`bash
pytest tests/ -q
\`\`\`

## 移植完了

✅ Codebase Migration  
✅ Test Suite (40+ tests)  
✅ Documentation  
✅ CI/CD (GitHub Actions)

---
**Release**: 2026-06-07 | **Status**: Production Ready
```

## 確認項目

- [ ] docs/ が完全にコピーされている
- [ ] README が新リポジトリ向けに更新されている
- [ ] すべてのリンクが正常に機能する

## 関連 Issue

- Issue 4: データ移植 (前提)
- Issue 6: CI/CD 設定 (次)
```

---

## Issue 6：GitHub Actions CI/CD 設定

```markdown
# [Migration] GitHub Actions 自動テスト設定

## 目的

GitHub Actions を設定し、push 時に自動的にテストが実行される仕組みを構築する。

## 実行手順

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
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: pytest-results
          path: test-results.json
EOF

# Step 3: コミット
git add .github/
git commit -m "ci: Add GitHub Actions pytest workflow"
git push origin develop
```

## 確認項目

- [ ] .github/workflows/test.yml が作成されている
- [ ] push 時にワークフローが自動実行される
- [ ] テスト結果が GitHub に表示される

## 次のステップ

- [ ] PR を作成（develop → main）
- [ ] GitHub Actions が自動実行される
- [ ] テストが PASS したら merge

## 関連 Issue

- Issue 5: ドキュメント移植 (前提)
- PR を作成して main にマージ (最終ステップ)
```

---

## 最終 PR：Complete Migration

```markdown
# Complete Migration of AI Executive System v2

## 説明

全 10 ステップ（AE～AN）の完全実装を旧リポジトリから新リポジトリへ移植した。

## 変更内容

- ✅ コードベース（models / services / routes）
- ✅ テストスイート（40+ テスト）
- ✅ ドキュメント（30+ ファイル）
- ✅ データ（corporate memory, シミュレーション結果）
- ✅ CI/CD（GitHub Actions）

## テスト結果

```
✅ 40+ tests passed
✅ All API endpoints responding
✅ Dashboard summary aggregating
✅ Corporate memory persistence working
```

## チェックリスト

- [x] コードベースが完全に移植された
- [x] 全テスト PASS (40+ テスト)
- [x] ドキュメント更新完了
- [x] GitHub Actions 設定完了
- [x] データ移植完了

## リリースノート

**Version**: 2.0  
**Status**: Production Ready  
**Date**: 2026-06-07

---

Closes: Issue 1, Issue 2, Issue 3, Issue 4, Issue 5, Issue 6
```
