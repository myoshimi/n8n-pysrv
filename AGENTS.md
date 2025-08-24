# Repository Guidelines

## メッセージ応答

- プロの IT ソフトウェアエンジニアとして正しく考え、応答する
- 日本語で応答する

## ツールの使用

- 必ず serena を 使用してコードベースを理解する
- 必ず sequential-thinking を使用して順序立てて考える
- searxngmcp を使用した Web 検索で調査する
- Context7 によるベストプラクティスを調査する
- fetch を使用して情報を取得する
- playwright を使用してブラウザ操作を行う

## Project Structure & Module Organization

- `main.py`: FastAPI アプリ本体（エンドポイント、Pydantic モデル、開発用`uvicorn.run`）。
- `pyproject.toml`/`poetry.lock`: Poetry による依存管理（Python 3.11）。
- `Dockerfile`/`docker-compose.yml`: コンテナ実行・開発用の設定。
- `env.example`: 環境変数のサンプル（`PORT`）。`.env` を作成して利用。
- `.vscode/`: 推奨エディタ設定。テストは未導入。将来的には `tests/` 配下に `test_*.py` を配置。

## Build, Test, and Development Commands

- 依存インストール: `poetry install`
- 開発サーバ: `poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
- 直接実行: `python main.py`
- Docker: `docker-compose up -d --build`（`PORT` は `.env` で設定）
- 依存追加: `poetry add <package>`（開発用は `-G dev`）
- テスト（導入後）: `poetry run pytest`

## Coding Style & Naming Conventions

- PEP 8 準拠、インデントは 4 スペース、型ヒントを必須化。
- 命名: 変数/関数は`snake_case`、クラスは`PascalCase`、API パスは複数形名詞（例: `/items`）。
- FastAPI: 入出力は Pydantic モデルで明示。公開関数/エンドポイントには簡潔な docstring。
- ツール推奨（任意導入）: Black/ruff/isort。
  - 例: `poetry run black . && poetry run ruff check . && poetry run isort .`

## Testing Guidelines

- フレームワークは`pytest`を推奨。構成は `tests/`、ファイルは `test_*.py`。
- FastAPI の`TestClient`でエンドポイントを検証。主要経路・エラー系・スキーマ整合をカバー。
- 変更時は新旧挙動の比較テストを追加し、回帰を防止。

## Commit & Pull Request Guidelines

- コミットは短く命令形で要点を明示（例: `Add health endpoint`）。現状は短文中心。規模が大きい変更は Conventional Commits を推奨。
- PR 要件: 目的/背景、変更点、影響範囲、動作確認手順（例: `curl` コマンド）、関連 Issue リンク。
- 互換性に影響する API 変更時は `README.md` を更新。ローカルでリンタ/テストを通過してから提出。

## Security & Configuration Tips

- 機密はコミットしない。`.env` を使用し、`env.example` を最新化。
- Docker は非 root 実行。入力値は Pydantic で検証し、外部データを盲信しない。
- `PORT` で公開ポートを制御（Compose の`"${PORT}:8000"`）。
