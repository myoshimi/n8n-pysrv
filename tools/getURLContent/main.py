#!/usr/bin/env python3

import sys
import os

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from tools.utils.url_utils import get_url_content, FetchMethod, ProcessMethod  # noqa: E402


def main():
    """メイン関数"""
    # コマンドライン引数のチェック
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print("使用方法: python main.py <URL> [fetch_method] [process_method]")
        print()
        print("fetch_method:")
        print("  request (default) - 通常のHTTPリクエスト")
        print("  browser           - ヘッドレスブラウザでJS実行")
        print()
        print("process_method:")
        print("  raw (default)     - そのまま返す")
        print("  markdown          - html2textでマークダウンに変換")
        print("  readability       - readabilityでメインコンテンツを抽出")
        print()
        print("例:")
        print("  python main.py https://example.com")
        print("  python main.py https://example.com request markdown")
        print("  python main.py https://example.com browser markdown")
        print("  python main.py https://example.com request readability")
        sys.exit(1)

    url = sys.argv[1]
    fetch_method_str = sys.argv[2].lower() if len(sys.argv) >= 3 else "request"
    process_method_str = sys.argv[3].lower() if len(sys.argv) >= 4 else "raw"

    # FetchMethodの変換
    fetch_method_map = {
        "request": FetchMethod.REQUEST,
        "browser": FetchMethod.BROWSER
    }

    # ProcessMethodの変換
    process_method_map = {
        "raw": ProcessMethod.RAW,
        "markdown": ProcessMethod.MARKDOWN,
        "readability": ProcessMethod.READABILITY
    }

    if fetch_method_str not in fetch_method_map:
        print(f"エラー: 不正なfetch_method '{fetch_method_str}'")
        print("利用可能な値: request, browser")
        sys.exit(1)

    if process_method_str not in process_method_map:
        print(f"エラー: 不正なprocess_method '{process_method_str}'")
        print("利用可能な値: raw, markdown, readability")
        sys.exit(1)

    fetch_method = fetch_method_map[fetch_method_str]
    process_method = process_method_map[process_method_str]

    try:
        print(f"URLからコンテンツを取得中: {url}")
        print(f"取得方法: {fetch_method.value}")
        print(f"処理方法: {process_method.value}")
        print()

        if fetch_method == FetchMethod.BROWSER:
            print("🌐 ヘッドレスブラウザを起動中...")
        else:
            print("🌍 HTTPリクエスト送信中...")

        if process_method == ProcessMethod.MARKDOWN:
            print("📝 html2textでマークダウン変換を実行...")
        elif process_method == ProcessMethod.READABILITY:
            print("📰 readabilityでメインコンテンツ抽出を実行...")

        content = get_url_content(
            url,
            fetch_method=fetch_method,
            process_method=process_method
        )

        print("\n" + "="*50)
        print("取得したコンテンツ:")
        print(f"取得: {fetch_method.value}, 処理: {process_method.value}")
        print("="*50)
        print(content)
        print("\n" + "="*50)
        print(f"コンテンツ長: {len(content)} 文字")

    except ImportError as e:
        print(f"❌ 必要なライブラリがインストールされていません: {e}")
        print("\n📦 依存関係をインストールしてください:")
        print("poetry install")
        if fetch_method == FetchMethod.BROWSER:
            print("playwright install  # ブラウザモード使用時")
        sys.exit(1)
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
