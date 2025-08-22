# Python 3.11のスリムイメージを使用
FROM python:3.11-slim

# Poetryのインストール
RUN pip install poetry

# 作業ディレクトリを設定
WORKDIR /app

# Poetryの設定（仮想環境を作成しない）
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=0 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# pyproject.tomlとpoetry.lock（もしあれば）をコピー
COPY pyproject.toml poetry.lock* ./

# 依存関係をインストール（開発依存関係は除く）
RUN poetry install --only=main && rm -rf $POETRY_CACHE_DIR

# アプリケーションファイルをコピー
COPY . .

# ポート8000を公開
EXPOSE 8000

# 非rootユーザーを作成（セキュリティのため）
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# FastAPIサーバーを起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
