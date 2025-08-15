# LangChain CLI Agent

LangChainとClaude-3.5-Sonnetを使用したCLIベースのAIエージェントです。ユーザーとの対話を通じて、様々なツールを駆使してタスクを実行します。

## 機能

- 🌤️ **天気情報取得**: 指定した都市の天気情報を取得
- 🧮 **数式計算**: 複雑な数式の計算（三角関数、対数なども対応）
- 📝 **TODO管理**: TODOアイテムの作成と管理

## セットアップ

### 1. 依存関係のインストール

```bash
uv sync
```

### 2. 環境変数の設定

`.env.sample`をコピーして`.env`を作成し、必要なAPIキーを設定してください：

```bash
cp .env.sample .env
# .envファイルを編集して以下を設定
```

必要な環境変数：
- `ANTHROPIC_API_KEY`: Claude APIキー（必須）
- `AWS_ACCESS_KEY_ID`: AWS アクセスキー（Python実行機能で必要）
- `AWS_SECRET_ACCESS_KEY`: AWS シークレットキー（Python実行機能で必要）

### 3. 実行

```bash
# srcフォルダ内のmain.pyを実行
python src/main.py

# または、モジュールとして実行
python -m src.main
```

## 使用例

```
👤 あなた: 東京の天気を教えて
🤖 エージェント: 東京の天気情報:
   気温: 25°C
   天候: 晴れ
   湿度: 60%
   取得時刻: 2025-08-12 10:30:00

👤 あなた: sin(π/2) + cos(0)を計算して
🤖 エージェント: 計算結果: sin(pi/2) + cos(0) = 2.0

👤 あなた: プレゼン資料作成をTODOに追加して
🤖 エージェント: TODOアイテムを作成しました:
   ID: 20250812_103000
   タスク: プレゼン資料作成
   優先度: medium
   作成日時: 2025-08-12T10:30:00
```

## ツール一覧

### get_weather_info
- **機能**: 指定都市の天気情報取得
- **引数**: city (str) - 都市名
- **例**: "東京の天気教えて"

### calculate_math_expression
- **機能**: 数式の計算
- **引数**: expression (str) - 数式
- **例**: "2+3*4を計算して", "sqrt(16)を計算して"

### create_todo_item
- **機能**: TODOアイテムの作成
- **引数**: task (str), priority (str, optional)
- **例**: "プレゼン資料作成をTODOに追加して"

## 注意事項

- Anthropic APIキー（Claude API）が必要です
- 計算機能では安全のため使用可能な関数を制限しています
- TODOデータは`todo_list.json`に保存されます
- モデルはClaude-3.5-Sonnet（claude-3-5-sonnet-20241022）を使用