# Power Automate × AI秘書 連携ガイド

このドキュメントは、AI秘書の API を Microsoft Power Automate から自動実行し、  
毎日・毎週 Outlook メールで自動通知する方法を説明しています。

## 🎯 目的
AI秘書が提供する以下の機能を自動化して、Masaharu は **戦略と意思決定だけに集中** できる環境を実現する。

- 📊 週次レポート生成（毎週月曜 8:00）
- 📋 会議アジェンダ自動送信（会議前日）
- 👥 1on1準備資料生成（1on1前日）
- 🎯 フォローアップメンバー通知（毎朝 8:30）

---

## 📡 1. AI秘書 API 一覧

| 機能 | エンドポイント | メソッド | 説明 |
|------|---|---|---|
| 週次レポート | `/api/weekly-report` | GET | 今週のタスク状況を集計 |
| 会議アジェンダ | `/api/agenda/weekly` | GET | 会議アジェンダを自動生成 |
| 1on1準備資料 | `/api/oneonone/{member_id}` | GET | 特定メンバーの1on1準備資料 |
| フォローアップ推奨 | `/api/recommendations/followup` | GET | フォローすべき3名を推奨 |

### デプロイ環境に応じた URL

**ローカル開発環境:**
```
http://127.0.0.1:8000/api/...
```

**Azure にデプロイ済みの場合:**
```
https://your-ai-secretary.azurewebsites.net/api/...
```

**NgrokでExpose（ローカルをインターネット公開）:**
```
https://xxxxxxxx.ngrok.io/api/...
```

---

## 🟦 フロー① 週次レポート自動送信

### トリガー
- **種類**: スケジュール済みクラウドフロー
- **実行頻度**: 毎週 月曜日 午前 8:00

### ステップ構成

#### ステップ 1: HTTP GET リクエスト
```
アクション: HTTP

メソッド: GET
URI: http://127.0.0.1:8000/api/weekly-report
ヘッダー:
  Content-Type: application/json
```

#### ステップ 2: Outlook メール送信
```
アクション: Outlook メール送信（V2）

宛先: masaharu@company.com
件名: 【AI秘書】今週の週次レポート

本文:
```

```html
AI秘書より、今週のタスク状況レポートをお送りします。

📅 期間: @{body('HTTP')['data']['week_start']} 〜 @{body('HTTP')['data']['week_end']}

📊 タスク状況
- 総タスク数: @{body('HTTP')['data']['total_tasks']}
- 高優先度: @{body('HTTP')['data']['high_priority']} 件
- 中優先度: @{body('HTTP')['data']['medium_priority']} 件
- 低優先度: @{body('HTTP')['data']['low_priority']} 件

📝 サマリー
@{body('HTTP')['data']['summary']}

🔗 詳細データ:
@{json(body('HTTP')['data']['tasks'])}

---
このメールは AI秘書が自動生成しています。
```

---

## 🟦 フロー② 会議アジェンダ自動送信

### トリガー
- **種類**: Outlook カレンダーイベントトリガー
- **条件**: 明日カレンダーにイベントがある場合（時刻に応じてフィルタリング）

**代案**（より簡潔）: スケジュール + Power Automate Desktop で Outlook カレンダーを監視

### ステップ構成

#### ステップ 1: HTTP GET リクエスト
```
アクション: HTTP

メソッド: GET
URI: http://127.0.0.1:8000/api/agenda/weekly
ヘッダー:
  Content-Type: application/json
```

#### ステップ 2: Outlook メール送信
```
アクション: Outlook メール送信（V2）

宛先: @{triggerBody()['organizer']['emailAddress']['address']}
      （会議主催者、または固定で masaharu@company.com に送付）

件名: 【AI秘書】明日の会議アジェンダ

本文:
```

```html
明日の会議のアジェンダを AI秘書が自動生成しました。

📅 開催日時: @{body('HTTP')['data']['date']}

📋 アジェンダ
@{join(body('HTTP')['data']['topics'], '<br/>')}

⚠️ リスク・懸念点
@{join(body('HTTP')['data']['risks'], '<br/>')}

✅ 決定すべき事項
@{join(body('HTTP')['data']['decisions'], '<br/>')}

---
このメールは AI秘書が自動生成しています。
```

---

## 🟦 フロー③ 1on1準備資料自動生成

### トリガー
- **種類**: Outlook カレンダーイベントトリガー
- **条件**: 1on1予定（カレンダーオプションで「1on1」タグ付け）の前日 18:00

### ステップ構成

#### ステップ 1: 1on1予定からメンバーID抽出
```
アクション: 変数の初期化

メンバーID を Outlook イベントの「コメント」から抽出
（例：イベント詳細に "member_id: 1" と記載）
```

#### ステップ 2: HTTP GET リクエスト
```
アクション: HTTP

メソッド: GET
URI: http://127.0.0.1:8000/api/oneonone/@{variables('member_id')}
ヘッダー:
  Content-Type: application/json
```

#### ステップ 3: Outlook メール送信
```
アクション: Outlook メール送信（V2）

宛次: masaharu@company.com

件名: 【AI秘書】1on1準備資料（@{body('HTTP')['data']['member']['name']}）

本文:
```

```html
@{body('HTTP')['data']['member']['name']} さんとの1on1準備資料です。

👤 メンバー情報
- 名前: @{body('HTTP')['data']['member']['name']}
- 役職: @{body('HTTP')['data']['member']['role']}
- メモ: @{body('HTTP')['data']['member']['notes']}

📌 最近のタスク
@{join(body('HTTP')['data']['recent_tasks'][].title, '<br/>')}

💪 強み
@{join(body('HTTP')['data']['member']['strengths'], '<br/>')}

⚠️ 課題
@{join(body('HTTP')['data']['member']['challenges'], '<br/>')}

💬 話題候補
@{join(body('HTTP')['data']['summary']['topics'], '<br/>')}

✅ 次のアクション案
@{join(body('HTTP')['data']['summary']['next_actions'], '<br/>')}

---
このメールは AI秘書が自動生成しています。
```

---

## 🟦 フロー④ フォローすべきメンバー 3名 自動通知

### トリガー
- **種類**: スケジュール済みクラウドフロー
- **実行頻度**: 毎日 午前 8:30

### ステップ構成

#### ステップ 1: HTTP GET リクエスト
```
アクション: HTTP

メソッド: GET
URI: http://127.0.0.1:8000/api/recommendations/followup
ヘッダー:
  Content-Type: application/json
```

#### ステップ 2: Outlook メール送信
```
アクション: Outlook メール送信（V2）

宛先: masaharu@company.com

件名: 【AI秘書】今日フォローすべきメンバートップ3

本文:
```

```html
AI秘書より、本日フォローアップが必要なメンバーをお知らせします。

📅 日付: @{body('HTTP')['data']['date']}

🎯 フォローすべきメンバーTop 3

@{body('HTTP')['data']['members'][0]['name']} （@{body('HTTP')['data']['members'][0]['role']}）
  優先度: @{body('HTTP')['data']['members'][0]['priority']}
  理由: @{body('HTTP')['data']['members'][0]['reason']}
  推奨アクション: @{body('HTTP')['data']['members'][0]['suggested_action']}

@{body('HTTP')['data']['members'][1]['name']} （@{body('HTTP')['data']['members'][1]['role']}）
  優先度: @{body('HTTP')['data']['members'][1]['priority']}
  理由: @{body('HTTP')['data']['members'][1]['reason']}
  推奨アクション: @{body('HTTP')['data']['members'][1]['suggested_action']}

@{body('HTTP')['data']['members'][2]['name']} （@{body('HTTP')['data']['members'][2]['role']}）
  優先度: @{body('HTTP')['data']['members'][2]['priority']}
  理由: @{body('HTTP')['data']['members'][2]['reason']}
  推奨アクション: @{body('HTTP')['data']['members'][2]['suggested_action']}

📋 サマリー
@{body('HTTP')['data']['summary']}

---
このメールは AI秘書が自動生成しています。
```

---

## 🔧 3. Power Automate Desktop で ngrok を使った場合の設定

ローカル環境では外部からのアクセスが制限されるため、 **ngrok** を使う方法：

### ngrok インストール & 起動
```bash
# ngrok をインストール
choco install ngrok

# FastAPI サーバを起動（ターミナル1）
python -m src.backend.app.main

# 別のターミナル2で ngrok を起動
ngrok http 8000
```

### 出力例
```
ngrok by @inconshreveable                     (Ctrl+C to quit)

Session Status                online
Account                       your-account@gmail.com
Version                       3.0.0
Region                        jp (Tokyo)
Forwarding                    https://1234abcd-5678.jp.ngrok.io -> http://localhost:8000
```

### Power Automate での URL 設定
```
https://1234abcd-5678.jp.ngrok.io/api/weekly-report
```

---

## 📊 API レスポンス例

### 週次レポート
```json
{
  "message": "Weekly report generated",
  "data": {
    "week_start": "2026-03-17",
    "week_end": "2026-03-23",
    "total_tasks": 2,
    "high_priority": 1,
    "medium_priority": 1,
    "low_priority": 0,
    "tasks": [...],
    "summary": "今週のタスク状況です。高優先度のタスクに注力してください。"
  }
}
```

### フォローアップ推奨
```json
{
  "message": "Follow-up members recommended",
  "data": {
    "date": "2026-03-22",
    "members": [
      {
        "member_id": 3,
        "name": "鈴木次郎",
        "role": "新メインプロジェクトリーダー",
        "priority": "high",
        "reason": "課題あり、新しい役割",
        "suggested_action": "進捗確認と具体的なサポート方法の相談"
      },
      ...
    ],
    "summary": "今週フォローアップが必要なメンバーは3名です..."
  }
}
```

---

## 🎁 まとめ

この Power Automate 連携が完成すると：

✅ **毎朝 8:30** → フォローすべきメンバーが届く  
✅ **毎週月曜 8:00** → 週次レポートが届く  
✅ **会議前日 18:00** → アジェンダが届く  
✅ **1on1 前日 18:00** → 準備資料が届く  

**あなたの AI秘書が、完全自動で働く状態になります。**

---

## 📞 トラブルシューティング

### Power Automate で HTTP エラー 404
- ローカル環境で `http://127.0.0.1:8000/...` を使用している場合、Power Automate Cloud から直接アクセスできない
- **解決**: ngrok を使って expose する、または Azure にデプロイ

### メール本文に JSON が空で表示される
- `body('HTTP')['data']` の参照不正
- **解決**: HTTP レスポンスの JSON 構造を確認し、正しいパスを指定

### Outlook カレンダーイベントからメンバーID を抽出できない
- イベント「コメント」に member_id が記載されていない
- **解決**: 1on1 イベント作成時に、必ず「コメント欄」に `member_id: 1` と記載する

---

**このドキュメントは定期的に更新されます。最新版は GitHub リポジトリをご確認ください。**