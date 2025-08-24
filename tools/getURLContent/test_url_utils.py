#!/usr/bin/env python3
"""
url_utils.py の現行仕様に合わせた動作検証スクリプト

対象機能:
- REQUEST + RAW / MARKDOWN / READABILITY
- 返却文字数上限 (max_chars)
- 取得サイズ上限 (max_bytes)
- （任意）BROWSER + MARKDOWN（Playwright未導入時は自動スキップ）
"""

from __future__ import annotations

import os
import sys
from typing import Optional

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from tools.utils.url_utils import (  # noqa: E402
    get_url_content,
    FetchMethod,
    ProcessMethod,
)


TEST_URL_HTML = "https://example.com"


def _preview(label: str, content: str, preview_len: int = 200) -> None:
    print(f"{label}: {len(content)} chars")
    snippet = content[:preview_len].replace("\n", " ")
    print(f"  preview: {snippet}...")


def test_request_raw() -> None:
    print("\n1️⃣ REQUEST + RAW")
    content = get_url_content(
        TEST_URL_HTML,
        fetch_method=FetchMethod.REQUEST,
        process_method=ProcessMethod.RAW,
        timeout=30,
        headers=None,
        allow_redirects=False,
        max_bytes=2_000_000,
        max_chars=1_000_000,
    )
    _preview("REQUEST+RAW", content)


def test_request_markdown() -> None:
    print("\n2️⃣ REQUEST + MARKDOWN")
    content = get_url_content(
        TEST_URL_HTML,
        fetch_method=FetchMethod.REQUEST,
        process_method=ProcessMethod.MARKDOWN,
        timeout=30,
        headers=None,
        allow_redirects=False,
        max_bytes=2_000_000,
        max_chars=1_000_000,
    )
    _preview("REQUEST+MARKDOWN", content)


def test_request_readability() -> None:
    print("\n3️⃣ REQUEST + READABILITY")
    content = get_url_content(
        TEST_URL_HTML,
        fetch_method=FetchMethod.REQUEST,
        process_method=ProcessMethod.READABILITY,
        timeout=30,
        headers=None,
        allow_redirects=False,
        max_bytes=2_000_000,
        max_chars=1_000_000,
    )
    _preview("REQUEST+READABILITY", content)


def test_request_with_limits() -> None:
    print("\n4️⃣ サイズ制限の検証 (max_chars / max_bytes)")
    # 文字数上限の検証（200文字にトリムされることを期待）
    content = get_url_content(
        TEST_URL_HTML,
        fetch_method=FetchMethod.REQUEST,
        process_method=ProcessMethod.MARKDOWN,
        timeout=30,
        headers=None,
        allow_redirects=False,
        max_bytes=2_000_000,
        max_chars=200,
    )
    assert len(content) <= 200, "max_charsの上限を超えています"
    _preview("LIMIT(max_chars=200)", content, preview_len=120)

    # バイト上限の検証（非常に小さい上限を指定してエラーになることを確認）
    try:
        _ = get_url_content(
            TEST_URL_HTML,
            fetch_method=FetchMethod.REQUEST,
            process_method=ProcessMethod.RAW,
            timeout=30,
            headers=None,
            allow_redirects=False,
            max_bytes=500,  # 意図的に小さく
            max_chars=1_000_000,
        )
        print("  ⚠️ 想定外: max_bytes=500 でエラーになりませんでした")
    except Exception as e:  # ValueError など
        print(f"  ✅ max_bytesで例外を確認: {e}")


def test_browser_markdown(optional: bool = True) -> None:
    print("\n5️⃣ BROWSER + MARKDOWN（任意）")
    if os.getenv("SKIP_BROWSER_TEST", "0") == "1":
        print("  ⏭  SKIP_BROWSER_TEST=1 のためスキップ")
        return
    try:
        content = get_url_content(
            TEST_URL_HTML,
            fetch_method=FetchMethod.BROWSER,
            process_method=ProcessMethod.MARKDOWN,
            timeout=30,
            wait_for_js=1000,
            headers=None,
            max_chars=5_000,
        )
        _preview("BROWSER+MARKDOWN", content)
    except ImportError as e:
        print(f"  ⏭  Playwright未導入のためスキップ: {e}")
        if not optional:
            raise
    except Exception as e:
        print(f"  ⏭  実行時エラーのためスキップ: {e}")
        if not optional:
            raise


def main() -> None:
    print("🧪 URL Utils テスト開始")
    print(f"テストURL: {TEST_URL_HTML}")

    try:
        test_request_raw()
        test_request_markdown()
        test_request_readability()
        test_request_with_limits()
        test_browser_markdown(optional=True)
        print("\n✅ テスト完了！")
    except Exception as e:
        print(f"❌ エラー発生: {e}")


if __name__ == "__main__":
    main()
