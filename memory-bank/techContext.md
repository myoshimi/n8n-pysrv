# Tech Context: 技術環境と制約

## 技術スタック

### コア技術

#### Python 3.11+

```toml
[tool.poetry.dependencies]
python = "^3.11"
```

**採用理由**:

- モダンな Python 機能の利用 (Pattern Matching, Structural Pattern Matching)
- パフォーマンス向上
- 型ヒントの改善
- エラーメッセージの品質向上

#### FastAPI 0.104.1

```toml
fastapi = "^0.104.1"
```

**採用理由**:

- 高性能 ASGI フレームワーク
- 自動 OpenAPI スキーマ生成
- Pydantic との完全統合
- 型安全な開発体験

#### Uvicorn + Standard Extras

```toml
uvicorn = {extras = ["standard"], version = "^0.24.0"}
```

**標準エクストラに含まれるもの**:

- `uvloop`: 高性能イベントループ
- `httptools`: 高速 HTTP パーサー
- `websockets`: WebSocket サポート
- `watchdog`: ファイル監視（開発時リロード）

#### Pydantic V2

```toml
pydantic = "^2.5.0"
```

**V2 の利点**:

- Rust ベースのコアによる高速化
- 改善された型検証
- より良いエラーメッセージ
- 後方互換性の向上

## 開発環境

### Poetry パッケージ管理

```toml
[tool.poetry]
name = "n8n-pysrv"
version = "1.0.0"
description = "FastAPIを使用したシンプルなAPIサーバー"
authors = ["myoshimi"]
readme = "README.md"
package-mode = false
```

**package-mode = false の意味**:

- アプリケーションとして扱う（ライブラリではない）
- `pip install -e .` での開発インストール不要
- よりシンプルな構成

### Docker 環境

#### Dockerfile 構成

```dockerfile
# マルチステージビルド対応想定
FROM python:3.11-slim

# Poetry インストール
RUN pip install poetry

# プロジェクトファイルコピー
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenv.create false \
    && poetry install --no-dev

# アプリケーションコピー
COPY . .

# サーバー起動
CMD ["python", "main.py"]
```

#### Docker Compose

```yaml
version: "3.8"
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app # 開発時のライブリロード
    environment:
      - ENV=development
```

### VSCode 開発環境

#### 推奨拡張機能

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.flake8",
    "ms-python.black-formatter",
    "bradlc.vscode-tailwindcss"
  ]
}
```

#### 設定

```json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true
}
```

## 依存関係管理

### プロダクション依存関係

- **FastAPI**: Web フレームワーク
- **Uvicorn**: ASGI サーバー
- **Pydantic**: データ検証・シリアライゼーション

### 開発依存関係（将来追加予定）

```toml
[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
black = "^23.0.0"
flake8 = "^6.0.0"
mypy = "^1.0.0"
```

### セキュリティ依存関係（将来追加予定）

```toml
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-multipart = "^0.0.6"
```

## 環境設定

### 環境変数管理

```bash
# env.example
PORT=8000
HOST=0.0.0.0
ENV=development
DEBUG=true

# 将来の拡張用
# DATABASE_URL=postgresql://...
# SECRET_KEY=your-secret-key
# CORS_ORIGINS=http://localhost:3000
```

### 設定管理パターン（将来実装）

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 8000
    host: str = "0.0.0.0"
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```

## デプロイメント考慮事項

### 現在のデプロイメント

- **Docker Compose**: シンプルな単一コンテナ
- **ポート**: 8000 (固定)
- **ホスト**: 0.0.0.0 (全インターフェース)

### プロダクション拡張（将来）

```yaml
# docker-compose.prod.yml
version: "3.8"
services:
  app:
    build: .
    restart: unless-stopped
    environment:
      - ENV=production
      - DEBUG=false
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.app.rule=Host(`api.example.com`)"
```

## パフォーマンス特性

### 現在の制約

- **In-Memory データ**: スケーラビリティなし
- **単一プロセス**: CPU バウンドタスクでボトルネック
- **基本的なエラーハンドリング**: 詳細な監視なし

### 最適化ポイント（将来）

```python
# 非同期データベースアクセス
import asyncpg
from databases import Database

# 接続プーリング
database = Database(
    "postgresql://user:pass@localhost/db",
    min_size=5,
    max_size=20
)

# キャッシング
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation(param: str) -> str:
    # 重い処理
    pass
```

## セキュリティ考慮事項

### 現在の状態

- **認証なし**: 全エンドポイントがパブリック
- **CORS 未設定**: 同一オリジンポリシーのみ
- **入力検証**: Pydantic による基本検証のみ

### セキュリティ強化パス（将来）

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://n8n.example.com"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# ホスト検証
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["api.example.com", "localhost"]
)
```

## 監視とログ

### 現在の監視

- **ヘルスチェック**: `/health` エンドポイント
- **基本ログ**: Uvicorn のデフォルトログ

### 監視強化（将来）

```python
import structlog
from prometheus_client import Counter, Histogram

# 構造化ログ
logger = structlog.get_logger()

# メトリクス
REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')

@app.middleware("http")
async def monitoring_middleware(request, call_next):
    with REQUEST_DURATION.time():
        response = await call_next(request)
        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    return response
```

## CI/CD パイプライン（将来）

### GitHub Actions 例

```yaml
name: CI/CD

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install Poetry
        run: pip install poetry
      - name: Install dependencies
        run: poetry install
      - name: Run tests
        run: poetry run pytest
      - name: Lint
        run: poetry run flake8 .
      - name: Type check
        run: poetry run mypy .
```

## 技術的制約と制限

### 現在の技術的制約

1. **データ永続化なし**: 再起動でデータ消失
2. **水平スケーリング不可**: 状態を持つ設計
3. **包括的テストなし**: 品質保証が限定的
4. **本格的監視なし**: プロダクション運用に不適

### 拡張時の考慮事項

1. **データベース選択**: PostgreSQL vs MongoDB vs Redis
2. **認証方式**: JWT vs OAuth2 vs API Key
3. **ログ管理**: ELK Stack vs 外部サービス
4. **監視**: Prometheus + Grafana vs DataDog vs New Relic

これらの制約は意図的に設けられており、MVP フェーズでの学習コスト削減と、将来の技術選択の柔軟性を保持するためのものである。
