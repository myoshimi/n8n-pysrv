# N8N Python Server

FastAPI を使用した PythonAPI サーバーです。N8N ワークフローとの統合に適した RESTful API を提供します。

## 機能

- FastAPI ベースの RESTful API
- Swagger UI による自動 API 仕様書生成
- ヘルスチェックエンドポイント
- CRUD 操作対応のアイテム管理
- メッセージ処理エンドポイント
- Docker コンテナサポート

## API エンドポイント

- `GET /` - メインページ（HTML）
- `GET /health` - ヘルスチェック
- `GET /items` - 全アイテム取得
- `POST /items` - アイテム追加
- `GET /items/{item_id}` - 特定アイテム取得
- `PUT /items/{item_id}` - アイテム更新
- `DELETE /items/{item_id}` - アイテム削除
- `POST /message` - メッセージ処理
- `GET /docs` - Swagger UI（API 仕様書）

## Docker での実行方法

### 前提条件

- Docker
- Docker Compose

### 1. Docker Compose を使用（推奨）

```bash
# コンテナをビルドして起動
docker-compose up --build

# バックグラウンドで起動
docker-compose up -d --build

# ログを確認
docker-compose logs -f

# コンテナを停止
docker-compose down
```

### 2. Docker コマンドを直接使用

```bash
# イメージをビルド
docker build -t n8n-python-server .

# コンテナを起動
docker run -p 8000:8000 n8n-python-server
```

## ローカル開発での実行方法

### 前提条件

- Python 3.11 以上
- Poetry

### 1. Poetry のインストール（まだの場合）

```bash
# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# Windows PowerShell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

### 2. 依存関係のインストール

```bash
# プロジェクトルートで実行
poetry install
```

### 3. サーバー起動

```bash
# Poetry環境でPython直接実行
poetry run python main.py

# またはPoetry環境でuvicornコマンド
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Poetry shell（オプション）

```bash
# Poetry仮想環境に入る
poetry shell

# その後は通常のコマンドが使える
python main.py
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## アクセス方法

サーバー起動後、以下の URL でアクセスできます：

- **メインページ**: http://localhost:8000
- **API 仕様書**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **ヘルスチェック**: http://localhost:8000/health

## API 使用例

### ヘルスチェック

```bash
curl http://localhost:8000/health
```

### アイテム作成

```bash
curl -X POST "http://localhost:8000/items" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "サンプルアイテム",
    "description": "テスト用のアイテムです",
    "price": 1000.0,
    "is_available": true
  }'
```

### メッセージ送信

```bash
curl -X POST "http://localhost:8000/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello from N8N",
    "data": {"workflow_id": "12345", "execution_id": "67890"}
  }'
```

## N8N での使用

このサーバーは N8N ワークフローから以下のように使用できます：

1. **HTTP Request ノード**を使用して API エンドポイントを呼び出し
2. **Webhook**ノードでこのサーバーからのデータを受信
3. **Set**ノードでレスポンスデータを加工

### N8N 設定例

- **Method**: POST
- **URL**: `http://n8n-python-server:8000/message`
- **Body**: JSON 形式
- **Headers**: `Content-Type: application/json`

## 開発

### プロジェクト構造

```
n8n-pysrv/
├── main.py              # FastAPIアプリケーション
├── pyproject.toml       # Poetry設定・依存関係管理
├── poetry.lock          # 依存関係のロックファイル
├── Dockerfile          # Docker設定
├── docker-compose.yml  # Docker Compose設定
├── .dockerignore       # Dockerビルド除外ファイル
├── .gitignore          # Git除外ファイル
└── README.md           # このファイル
```

### 追加機能の実装

新しいエンドポイントを追加する場合は、`main.py`に新しい関数を追加してください：

```python
@app.post("/your-endpoint")
async def your_function():
    return {"message": "Your response"}
```

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。
