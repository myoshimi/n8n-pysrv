# N8N Python Server

FastAPIを使用したPythonAPIサーバーです。N8Nワークフローとの統合に適したRESTful APIを提供します。

## 機能

- FastAPIベースのRESTful API
- Swagger UIによる自動API仕様書生成
- ヘルスチェックエンドポイント
- CRUD操作対応のアイテム管理
- メッセージ処理エンドポイント
- Dockerコンテナサポート

## API エンドポイント

- `GET /` - メインページ（HTML）
- `GET /health` - ヘルスチェック
- `GET /items` - 全アイテム取得
- `POST /items` - アイテム追加
- `GET /items/{item_id}` - 特定アイテム取得
- `PUT /items/{item_id}` - アイテム更新
- `DELETE /items/{item_id}` - アイテム削除
- `POST /message` - メッセージ処理
- `GET /docs` - Swagger UI（API仕様書）

## Dockerでの実行方法

### 前提条件

- Docker
- Docker Compose

### 1. Docker Composeを使用（推奨）

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

### 2. Dockerコマンドを直接使用

```bash
# イメージをビルド
docker build -t n8n-python-server .

# コンテナを起動
docker run -p 8000:8000 n8n-python-server
```

## ローカル開発での実行方法

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. サーバー起動

```bash
# Python直接実行
python main.py

# またはuvicornコマンド
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## アクセス方法

サーバー起動後、以下のURLでアクセスできます：

- **メインページ**: http://localhost:8000
- **API仕様書**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **ヘルスチェック**: http://localhost:8000/health

## API使用例

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

## N8Nでの使用

このサーバーはN8Nワークフローから以下のように使用できます：

1. **HTTP Requestノード**を使用してAPIエンドポイントを呼び出し
2. **Webhook**ノードでこのサーバーからのデータを受信
3. **Set**ノードでレスポンスデータを加工

### N8N設定例

- **Method**: POST
- **URL**: `http://n8n-python-server:8000/message`
- **Body**: JSON形式
- **Headers**: `Content-Type: application/json`

## 開発

### プロジェクト構造

```
n8n-pysrv/
├── main.py              # FastAPIアプリケーション
├── requirements.txt     # Python依存関係
├── Dockerfile          # Docker設定
├── docker-compose.yml  # Docker Compose設定
├── .dockerignore       # Dockerビルド除外ファイル
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

このプロジェクトはMITライセンスの下で公開されています。
