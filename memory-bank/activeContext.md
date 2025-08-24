# Active Context: 現在の作業状況と次のステップ

## 現在の状況

### プロジェクトステータス

- **フェーズ**: Phase 1 - MVP 完成 + ツール基盤構築 ✅
- **最終更新**: 2025/08/23
- **現在の安定性**: 完全に動作する状態
- **デプロイメント**: Docker 環境で即座に起動可能

### 最近完了した作業

1. **基本 API 実装** (完了)

   - RESTful エンドポイント (CRUD + メッセージ処理)
   - Pydantic データモデル定義
   - 自動 API ドキュメント生成

2. **開発環境構築** (完了)

   - Poetry による依存関係管理
   - Docker + Docker Compose 設定
   - VSCode 開発環境設定

3. **N8N 統合対応** (完了)

   - 標準的な HTTP Request ノード対応
   - JSON 形式での双方向通信
   - ヘルスチェックエンドポイント

4. **ツール基盤構築** (2025/08/23 完了) ⭐ NEW

   - **関数モジュール化**: `get_url_content`を`tools/utils/url_utils.py`に移設
   - **Python パッケージ構造**: `tools/__init__.py`、`tools/utils/__init__.py`作成
   - **import path 問題解決**: `sys.path`動的修正で環境変数不要に
   - **コード品質向上**: PEP8 警告の適切な抑制（`# noqa: E402`）

5. **URL 処理機能拡張** (2025/08/23 完了) ⭐ NEW

   - **Readability 処理追加**: `ProcessMethod.READABILITY`で記事本文抽出
   - **`_process_with_readability()`実装**: readability-lxml 統合
   - **`get_readable_content()`便利関数**: 専用の簡単インターフェース
   - **CLI ツール対応**: `tools/getURLContent/main.py`で readability オプション追加
   - **完全なエラーハンドリング**: ライブラリ不足時のフォールバック機能
   - **柔軟な処理選択**: RAW/MARKDOWN/READABILITY の 3 つの処理方法

6. **メモリバンク構築** (進行中)
   - プロジェクト全体の文書化 ✅
   - 技術的意思決定の記録 ✅
   - 将来拡張パスの明確化 ✅

## 現在のフォーカス

### 🎯 新しい戦略方向: ツールエコシステム構築

#### ツール開発の新方針

**目的**: FastAPI サーバが提供するサービスに対応するコマンドラインツールの構築

```
tools/
├── __init__.py                    ✅ 完成
├── utils/                         ✅ 完成
│   ├── __init__.py               ✅ 完成
│   └── url_utils.py              ✅ 完成 (URL取得機能)
├── getURLContent/                 ✅ 完成
│   ├── main.py                   ✅ 完成 (リファクタリング済み)
│   └── README.md
└── [FastAPI service tools]/       🎯 計画中
    ├── itemManager/              ⏳ 計画中 (Item CRUD操作)
    ├── messageProcessor/         ⏳ 計画中 (メッセージ処理)
    └── healthChecker/           ⏳ 計画中 (ヘルスチェック)
```

#### 設計パターン（確立済み）

```python
#!/usr/bin/env python3

import sys
import os

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from tools.utils.url_utils import get_url_content  # noqa: E402

def main():
    """メイン関数"""
    # コマンドライン処理
    pass

if __name__ == "__main__":
    main()
```

**確立されたベストプラクティス**:

- `sys.path`動的修正による自己完結型 import
- 共通機能の`tools/utils/`への集約
- PEP8 準拠（必要に応じた例外明示）
- N8N API との対応関係明確化

### 重要な意思決定事項

#### 1. 次期実装するツール群

**優先度順（FastAPI エンドポイントとの対応）**:

1. **itemManager/** (高優先度)

   - 対応 API: `/items/*` (CRUD 操作)
   - 機能: アイテムの作成・取得・更新・削除
   - CLI 例: `python tools/itemManager/main.py create "Test Item" --price 100`

2. **messageProcessor/** (中優先度)

   - 対応 API: `/message`
   - 機能: 汎用メッセージ処理・送信
   - CLI 例: `python tools/messageProcessor/main.py send "Hello World" --data '{"key": "value"}'`

3. **healthChecker/** (低優先度)
   - 対応 API: `/health`
   - 機能: サーバー状態の監視・診断
   - CLI 例: `python tools/healthChecker/main.py check --server localhost:8000`

#### 2. ツール間共通機能の拡張

**`tools/utils/`への追加予定**:

- `api_client.py`: FastAPI サーバーとの通信共通機能
- `config_utils.py`: 設定管理（サーバー URL、認証情報等）
- `cli_utils.py`: コマンドライン処理の共通機能

#### 3. テスト・品質保証戦略

**ツール固有のテスト**:

- 各ツールディレクトリに`test_main.py`配置
- FastAPI サーバー連携の統合テスト
- コマンドライン引数処理のテスト

### アクティブな技術課題

#### FastAPI サーバー連携パターン

```python
# tools/utils/api_client.py (実装予定)
import requests
from typing import Dict, Any, Optional

class FastAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')

    def get(self, endpoint: str) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}{endpoint}")
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(f"{self.base_url}{endpoint}", json=data)
        response.raise_for_status()
        return response.json()
```

#### コマンドライン設計パターン

```python
# 標準的なCLI構造（argparse使用）
import argparse

def create_parser():
    parser = argparse.ArgumentParser(description='Item Manager CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # create サブコマンド
    create_parser = subparsers.add_parser('create', help='Create new item')
    create_parser.add_argument('name', help='Item name')
    create_parser.add_argument('--price', type=float, help='Item price')

    return parser
```

## 次のステップ (優先度順)

### Phase 1.5: ツールエコシステム完成 (新規追加フェーズ)

#### 1. itemManager ツール実装 (高優先度)

**目標**: FastAPI の Item CRUD 操作をコマンドラインから実行

**作業項目**:

- [ ] `tools/itemManager/main.py` 実装
- [ ] argparse による充実した CLI
- [ ] FastAPI サーバー連携機能
- [ ] エラーハンドリングと分かりやすいメッセージ
- [ ] 使用例ドキュメント作成

**推定工数**: 1 日

#### 2. API 共通ライブラリ実装 (中優先度)

**目標**: ツール間で共通利用する API 通信機能

**作業項目**:

- [ ] `tools/utils/api_client.py` 実装
- [ ] 設定管理機能（`tools/utils/config_utils.py`）
- [ ] CLI 共通機能（`tools/utils/cli_utils.py`）
- [ ] 既存ツールでの共通ライブラリ活用

**推定工数**: 0.5 日

#### 3. messageProcessor & healthChecker 実装

**推定工数**: 各 0.5 日

### Phase 2: 実用性強化 (既存計画)

#### データ永続化 (進捗: 0%)

**現在の制約**: In-memory データ、再起動で消失
**必要作業**:

- [ ] PostgreSQL 統合設計
- [ ] SQLAlchemy モデル定義
- [ ] データベースマイグレーション
- [ ] Docker Compose での DB コンテナ追加
- [ ] 環境変数での接続設定

**推定工数**: 2-3 日

#### 認証・セキュリティ (進捗: 0%)

**現在の制約**: 認証なし、全エンドポイントパブリック
**必要作業**:

- [ ] API Key 認証実装
- [ ] 環境変数での認証情報管理
- [ ] セキュリティヘッダー追加
- [ ] CORS 設定強化
- [ ] N8N からの認証設定ドキュメント
- [ ] **ツール群での認証対応** ⭐ 新規

**推定工数**: 1-2 日

## N8N 統合の現在の状況

### 動作確認済みパターン

```javascript
// N8N HTTP Request Node 設定例
{
  "method": "POST",
  "url": "http://n8n-python-server:8000/items",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "name": "{{ $json.item_name }}",
    "price": {{ $json.price }},
    "is_available": true
  }
}
```

### 新しい展開: ツールによる N8N 統合テスト

**計画中の活用方法**:

```bash
# N8N ワークフローのテストをコマンドラインから実行
python tools/itemManager/main.py create "Test Item" --server n8n-python-server:8000
python tools/healthChecker/main.py monitor --interval 30 --alerts
```

## 技術的負債と改善項目

### 既知の制限事項

1. **データ永続化なし**: 最優先で解決必要
2. **エラーハンドリング基本レベル**: 段階的改善
3. **セキュリティ対策なし**: Phase 2 で対応
4. **包括的テストなし**: 開発速度に影響

### 新しいリファクタリング候補

```python
# 現在のモノリシック構造
# main.py に全てのロジック

# 将来の構造化
# app/
# ├── models/       # データモデル
# ├── routers/      # エンドポイント分割
# ├── services/     # ビジネスロジック
# ├── core/         # 設定・共通機能
# └── tests/        # テストコード
#
# tools/
# ├── utils/        # 共通ユーティリティ ✅ 完成
# ├── itemManager/  # Item管理ツール ⏳ 計画中
# ├── messageProcessor/ # メッセージ処理ツール ⏳ 計画中
# └── healthChecker/    # 監視ツール ⏳ 計画中
```

## ツール開発のベストプラクティス（確立済み）

### 1. 自己完結型 import パターン

```python
# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from tools.utils.url_utils import get_url_content  # noqa: E402
```

### 2. コマンドライン設計指針

- **argparse 使用**: 標準的で多機能
- **サブコマンド構造**: `create`, `get`, `update`, `delete` 等
- **明確なヘルプメッセージ**: `--help` で使い方が分かる
- **エラーメッセージ**: 初心者にも分かりやすい

### 3. FastAPI サーバー統合

- **設定可能なサーバー URL**: デフォルト `localhost:8000`
- **エラーハンドリング**: HTTP ステータスコードに応じた処理
- **JSON レスポンス**: N8N 互換形式での出力

## コミュニティ・エコシステム連携

### 想定する貢献方向

1. **N8N Community**: ツール統合事例とベストプラクティス共有
2. **FastAPI Community**: CLI ツール統合パターンの標準化
3. **Docker Hub**: 公式イメージ公開（ツール付き）
4. **GitHub Template**: 再利用可能なテンプレート化

### ドキュメント強化予定

- [ ] ツール使用チュートリアル ⭐ 新規
- [ ] N8N 統合 + ツール連携ガイド ⭐ 新規
- [ ] コマンドライン操作マニュアル ⭐ 新規
- [ ] デプロイメントガイド
- [ ] カスタマイゼーション方法
- [ ] トラブルシューティング

---

**現在の状況要約**: MVP として完全に機能する状態 + ツール基盤構築完了。次は FastAPI サービスと連携するツール群の実装フェーズ。コマンドラインからの簡単なテスト・操作環境の実現を目指す。
