"""
URL関連のユーティリティ関数

このモジュールにはHTTPリクエストやURL操作に関する共通機能が含まれます。
取得方法と処理方法を分離した柔軟な設計：
- 取得方法: REQUEST (通常のHTTPリクエスト) / BROWSER (ヘッドレスブラウザ)
- 処理方法: RAW (そのまま返す) / MARKDOWN (html2textでマークダウン変換) / READABILITY (メインコンテンツ抽出)
"""

import logging
import requests
import html2text
from enum import Enum
from typing import Optional, Iterable

# ログ設定
logger = logging.getLogger(__name__)


class FetchMethod(Enum):
    """コンテンツ取得方法を定義するEnum"""
    REQUEST = "request"  # 通常のrequests.get
    BROWSER = "browser"  # ヘッドレスブラウザでJS実行


class ProcessMethod(Enum):
    """レスポンス処理方法を定義するEnum"""
    RAW = "raw"          # そのまま返す
    MARKDOWN = "markdown"  # html2textでマークダウンに変換
    READABILITY = "readability"  # readabilityでメインコンテンツを抽出


def get_url_content(
    url: str,
    fetch_method: FetchMethod = FetchMethod.REQUEST,
    process_method: ProcessMethod = ProcessMethod.RAW,
    timeout: int = 30,
    wait_for_js: int = 3000,
    headers: Optional[dict] = None,
    *,
    allow_redirects: bool = False,
    max_bytes: int = 2_000_000,
    max_chars: int = 1_000_000,
    allowed_content_types: Optional[Iterable[str]] = None,
) -> str:
    """
    指定されたURLからコンテンツを取得し、指定された方法で処理する

    Args:
        url (str): 取得したいURL
        fetch_method (FetchMethod): 取得方法の指定
        process_method (ProcessMethod): 処理方法の指定
        timeout (int): タイムアウト時間（秒）
        wait_for_js (int): ブラウザモード時のJS実行待機時間（ミリ秒）
        headers (dict, optional): カスタムHTTPヘッダー
        allow_redirects (bool): リダイレクトを許可するか（SSRF軽減のためデフォルトFalse）
        max_bytes (int): request取得時に読み込む最大バイト数（超過でエラー）
        max_chars (int): 返却テキストの最大文字数（超過分は切り捨て）
        allowed_content_types (Iterable[str], optional): 許可するContent-Typeのプレフィックス

    Returns:
        str: URLから取得・処理されたテキストコンテンツ

    Raises:
        requests.exceptions.RequestException: HTTP要求に失敗した場合
        ImportError: 必要なライブラリがインストールされていない場合
        Exception: その他のエラー
    """
    logger.info(
        f"URLコンテンツ取得開始: {url}, "
        f"fetch: {fetch_method.value}, process: {process_method.value}"
    )

    try:
        # Step 1: コンテンツ取得
        if fetch_method == FetchMethod.REQUEST:
            raw_content = _fetch_with_request(
                url,
                timeout,
                headers,
                allow_redirects=allow_redirects,
                max_bytes=max_bytes,
                allowed_content_types=allowed_content_types,
            )
        elif fetch_method == FetchMethod.BROWSER:
            raw_content = _fetch_with_browser(url, timeout, wait_for_js, headers)
        else:
            raise ValueError(f"未サポートのFetchMethod: {fetch_method}")

        # Step 2: コンテンツ処理
        if process_method == ProcessMethod.RAW:
            processed_content = _process_raw(raw_content)
        elif process_method == ProcessMethod.MARKDOWN:
            processed_content = _process_to_markdown(raw_content)
        elif process_method == ProcessMethod.READABILITY:
            processed_content = _process_with_readability(raw_content)
        else:
            raise ValueError(f"未サポートのProcessMethod: {process_method}")

        # サイズ制御（文字数）
        if processed_content and len(processed_content) > max_chars:
            processed_content = processed_content[:max_chars]

        logger.info(f"URLコンテンツ取得完了: {url}")
        return processed_content

    except Exception as e:
        logger.error(f"URLコンテンツ取得エラー: {url}, error: {str(e)}")
        raise


def _fetch_with_request(
    url: str,
    timeout: int,
    headers: Optional[dict] = None,
    *,
    allow_redirects: bool = False,
    max_bytes: int = 2_000_000,
    allowed_content_types: Optional[Iterable[str]] = None,
) -> str:
    """
    通常のHTTPリクエストでコンテンツを取得

    Args:
        url (str): 取得したいURL
        timeout (int): タイムアウト時間（秒）
        headers (dict, optional): カスタムHTTPヘッダー

    Returns:
        str: HTMLコンテンツ

    Raises:
        requests.exceptions.RequestException: HTTP要求に失敗した場合
    """
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    if headers:
        default_headers.update(headers)

    logger.debug(f"HTTP REQUEST: {url}")
    # 許可するContent-Type（プレフィックス）
    allowed_types = list(allowed_content_types) if allowed_content_types else [
        "text/",
        "application/xhtml",
        "application/xml",
    ]

    with requests.get(
        url,
        timeout=timeout,
        headers=default_headers,
        stream=True,
        allow_redirects=allow_redirects,
    ) as response:
        response.raise_for_status()

        ctype = response.headers.get("Content-Type", "").lower()
        if not any(ctype.startswith(prefix) for prefix in allowed_types):
            raise ValueError(f"不許可のContent-Typeです: {ctype}")

        # バイト単位で読み込み制限
        total = 0
        chunks: list[bytes] = []
        for chunk in response.iter_content(chunk_size=8192):
            if not chunk:
                continue
            total += len(chunk)
            if total > max_bytes:
                raise ValueError("取得サイズが上限を超えました")
            chunks.append(chunk)

        raw_bytes = b"".join(chunks)
        # 文字エンコーディング推定
        encoding = response.encoding or response.apparent_encoding or "utf-8"
        return raw_bytes.decode(encoding, errors="replace")


def _fetch_with_browser(
    url: str,
    timeout: int,
    wait_for_js: int,
    headers: Optional[dict] = None
) -> str:
    """
    ヘッドレスブラウザでJavaScript実行後のコンテンツを取得

    Args:
        url (str): 取得したいURL
        timeout (int): タイムアウト時間（秒）
        wait_for_js (int): JavaScript実行待機時間（ミリ秒）
        headers (dict, optional): カスタムHTTPヘッダー

    Returns:
        str: レンダリング後のHTMLコンテンツ

    Raises:
        ImportError: playwrightがインストールされていない場合
        Exception: ブラウザ操作エラー
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise ImportError(
            "playwrightライブラリがインストールされていません。"
            "インストールするには: pip install playwright && playwright install"
        )

    logger.debug(f"BROWSER REQUEST: {url}")

    with sync_playwright() as p:
        # ブラウザ起動（ヘッドレスモード、AutomationControlled無効化）
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )

        # コンテキスト（実ブラウザに近い環境）
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="ja-JP",
            timezone_id="Asia/Tokyo",
            viewport={"width": 1280, "height": 800},
        )

        try:
            page = context.new_page()

            # webdriverフラグを隠す
            page.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
            )

            # カスタムヘッダー設定
            if headers:
                page.set_extra_http_headers(headers)

            # ページに移動（まずはDOM読み込みまで）
            page.goto(url, timeout=timeout * 1000, wait_until="domcontentloaded")

            # 同意/コンセント系があれば可能ならクリック（失敗しても無視）
            try:
                candidates = [
                    "text=同意して続行",
                    "text=同意して進む",
                    "text=同意する",
                    "button:has-text('同意')",
                    "#consent-accept-button",
                ]
                for sel in candidates:
                    locator = page.locator(sel)
                    if locator.first.count() > 0:
                        try:
                            locator.first.click(timeout=1000)
                            break
                        except Exception:
                            continue
            except Exception:
                pass

            # ネットワークのアイドル化を待機してから、さらに待機
            try:
                page.wait_for_load_state("networkidle", timeout=timeout * 1000)
            except Exception:
                # 一部サイトではnetworkidleに到達しないため無視
                pass
            page.wait_for_timeout(wait_for_js)

            # ページの完全なHTMLコンテンツを取得
            html_content = page.content()
            return html_content

        finally:
            context.close()
            browser.close()


def _process_raw(content: str) -> str:
    """
    コンテンツをそのまま返す（何も処理しない）

    Args:
        content (str): 処理するコンテンツ

    Returns:
        str: そのままのコンテンツ
    """
    return content


def _process_to_markdown(content: str) -> str:
    """
    HTMLコンテンツをマークダウン形式に変換

    Args:
        content (str): HTMLコンテンツ

    Returns:
        str: マークダウン形式のテキスト

    Raises:
        ImportError: html2textがインストールされていない場合
    """
    try:
        # html2textの設定
        h = html2text.HTML2Text()
        h.ignore_links = False  # リンクを保持
        h.ignore_images = False  # 画像を保持
        h.body_width = 0  # 行幅制限なし
        h.unicode_snob = True  # Unicode文字を適切に処理
        h.escape_snob = True  # エスケープ文字を適切に処理

        # HTMLをマークダウンに変換
        markdown_content = h.handle(content)

        logger.debug("HTMLコンテンツをマークダウンに変換完了")
        return markdown_content.strip()

    except Exception as e:
        logger.error(f"マークダウン変換エラー: {str(e)}")
        # フォールバック: 簡易的にHTMLタグを除去
        import re
        clean_text = re.sub(r'<[^<]+?>', '', content)
        return clean_text.strip()


def _process_with_readability(content: str) -> str:
    """
    readabilityライブラリでHTMLコンテンツからメインコンテンツを抽出

    Args:
        content (str): HTMLコンテンツ

    Returns:
        str: 抽出されたメインコンテンツ（プレーンテキスト）

    Raises:
        ImportError: readabilityライブラリがインストールされていない場合
    """
    try:
        from readability import Document
    except ImportError:
        logger.warning(
            "readabilityライブラリがインストールされていません。"
            "インストールするには: pip install readability-lxml"
        )
        # フォールバック: マークダウン変換を使用
        logger.info("フォールバック: マークダウン変換を使用します")
        return _process_to_markdown(content)

    try:
        # readabilityでドキュメント処理
        doc = Document(content)

        # タイトルと本文を取得
        title = doc.title()
        summary_html = doc.summary()

        # HTMLからプレーンテキストに変換
        h = html2text.HTML2Text()
        h.ignore_links = True  # リンクは無視（読みやすさ重視）
        h.ignore_images = True  # 画像は無視
        h.body_width = 0  # 行幅制限なし
        h.unicode_snob = True
        h.escape_snob = True

        # タイトルと本文を結合
        full_content = f"# {title}\n\n{summary_html}" if title else summary_html
        readable_content = h.handle(full_content)

        logger.debug("readabilityでメインコンテンツ抽出完了")
        text = readable_content.strip()

        # きわめて短い結果の場合はマークダウン変換にフォールバック
        if len(text) < 200:
            logger.info("readability結果が短いためmarkdownへフォールバックします")
            return _process_to_markdown(content)
        return text

    except Exception as e:
        logger.error(f"readability処理エラー: {str(e)}")
        # フォールバック: マークダウン変換を使用
        logger.info("フォールバック: マークダウン変換を使用します")
        return _process_to_markdown(content)


# 後方互換性のためのヘルパー関数（必要に応じて）
def get_plain_content(url: str, timeout: int = 30, headers: Optional[dict] = None) -> str:
    """通常のHTTPリクエストでプレーンテキストを取得（後方互換性）"""
    return get_url_content(url, FetchMethod.REQUEST, ProcessMethod.RAW, timeout, headers=headers)


def get_browser_content_as_markdown(
    url: str,
    timeout: int = 30,
    wait_for_js: int = 3000,
    headers: Optional[dict] = None
) -> str:
    """ブラウザでコンテンツを取得してマークダウンに変換（推奨用法）"""
    return get_url_content(
        url,
        FetchMethod.BROWSER,
        ProcessMethod.MARKDOWN,
        timeout,
        wait_for_js,
        headers
    )


def get_readable_content(
    url: str,
    fetch_method: FetchMethod = FetchMethod.REQUEST,
    timeout: int = 30,
    wait_for_js: int = 3000,
    headers: Optional[dict] = None
) -> str:
    """
    readabilityでメインコンテンツを抽出（記事本文取得に最適）

    Args:
        url (str): 取得したいURL
        fetch_method (FetchMethod): 取得方法の指定
        timeout (int): タイムアウト時間（秒）
        wait_for_js (int): ブラウザモード時のJS実行待機時間（ミリ秒）
        headers (dict, optional): カスタムHTTPヘッダー

    Returns:
        str: 抽出されたメインコンテンツ
    """
    return get_url_content(
        url,
        fetch_method,
        ProcessMethod.READABILITY,
        timeout,
        wait_for_js,
        headers
    )
