# URL Content Getter

指定された URL からコンテンツを取得する Python プログラムです。
取得方法と処理方法を分離した柔軟な設計を採用しています。

## 機能

新しい設計により、以下の組み合わせが可能です：

### 取得方法 (Fetch Method)

- **request** (デフォルト): 通常の HTTP リクエスト
- **browser**: ヘッドレスブラウザで JavaScript 実行後のコンテンツを取得

### 処理方法 (Process Method)

- **raw** (デフォルト): そのまま返す
- **markdown**: html2text でマークダウンに変換

## 使用方法

```bash
# Poetry環境での実行（推奨）
poetry run python main.py <URL> [fetch_method] [process_method]

# 仮想環境を直接使用する場合
python main.py <URL> [fetch_method] [process_method]
```

### 例

```bash
# 基本的な使用（REQUEST + RAW）
python main.py https://example.com

# HTTPリクエスト + マークダウン変換（推奨）
python main.py https://example.com request markdown

# ヘッドレスブラウザ + マークダウン変換（SPA対応）
python main.py https://example.com browser markdown

# ブラウザでHTMLそのまま取得
python main.py https://example.com browser raw

# 使用方法を表示
python main.py
```

## 利用可能な組み合わせ

| 取得方法 | 処理方法 | 用途                             |
| -------- | -------- | -------------------------------- |
| request  | raw      | 軽量、高速、HTML そのまま        |
| request  | markdown | 軽量、構造化、読みやすい（推奨） |
| browser  | raw      | JS 対応、HTML そのまま           |
| browser  | markdown | JS 対応、構造化（SPA 推奨）      |

## 必要な依存関係

- Python 3.11+
- requests ライブラリ
- html2text (markdown 処理用)
- playwright (browser 取得用)

依存関係は既に poetry で管理されているため、プロジェクトルートで以下を実行：

```bash
poetry install
poetry run playwright install  # browser モード使用時のブラウザインストール
```

## 出力例

### REQUEST + MARKDOWN モード

```
URLからコンテンツを取得中: https://example.com
取得方法: request
処理方法: markdown

🌍 HTTPリクエスト送信中...
📝 html2textでマークダウン変換を実行...

==================================================
取得したコンテンツ:
取得: request, 処理: markdown
==================================================
# Example Domain

This domain is for use in illustrative examples in documents...

==================================================
コンテンツ長: 512 文字
```

## エラーハンドリング

- 無効な URL
- ネットワーク接続エラー
- HTTP エラー（404, 500 など）
- コマンドライン引数の不正
- 依存関係の不足

## テスト

動作テストを実行：

```bash
python test_url_utils.py
```

## プログラム的な使用

```python
from tools.utils.url_utils import get_url_content, FetchMethod, ProcessMethod

# 基本的な使用
content = get_url_content("https://example.com")

# 推奨設定（HTTPリクエスト + マークダウン変換）
markdown_content = get_url_content(
    "https://example.com",
    fetch_method=FetchMethod.REQUEST,
    process_method=ProcessMethod.MARKDOWN
)

# SPA対応（ブラウザ + マークダウン変換）
spa_content = get_url_content(
    "https://spa-example.com",
    fetch_method=FetchMethod.BROWSER,
    process_method=ProcessMethod.MARKDOWN
)
```

## 設計の利点

- **柔軟性**: 取得方法と処理方法を独立して選択可能
- **拡張性**: 新しい取得方法や処理方法を容易に追加可能
- **保守性**: 機能が分離されているため、個別にメンテナンス可能
- **型安全性**: Enum による型安全な設定
