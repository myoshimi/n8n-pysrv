#!/usr/bin/env python3
"""
url_utils.pyの動作テスト
"""

import sys
import os

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from tools.utils.url_utils import get_url_content, FetchMethod, ProcessMethod  # noqa: E402

def test_basic_functionality():
    """基本機能のテスト"""

    # テスト用URL（軽量なページ）
    test_url = "https://httpbin.org/html"

    print("🧪 URL Utils テスト開始")
    print(f"テストURL: {test_url}")

    try:
        # 1. REQUEST + RAW (従来の方式)
        print("\n1️⃣ REQUEST + RAW テスト")
        content1 = get_url_content(test_url, FetchMethod.REQUEST, ProcessMethod.RAW)
        print(f"結果: {len(content1)} 文字取得")
        print(f"プレビュー: {content1[:100]}...")

        # 2. REQUEST + MARKDOWN (推奨)
        print("\n2️⃣ REQUEST + MARKDOWN テスト")
        content2 = get_url_content(test_url, FetchMethod.REQUEST, ProcessMethod.MARKDOWN)
        print(f"結果: {len(content2)} 文字取得")
        print(f"プレビュー: {content2[:200]}...")

        print("\n✅ 基本テスト完了！")

    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    test_basic_functionality()
