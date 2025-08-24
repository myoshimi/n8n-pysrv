import os
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, HttpUrl, Field
import uvicorn

from tools.utils.url_utils import (
    get_url_content,
    FetchMethod,
    ProcessMethod,
)

# 標準ライブラリ
import socket
import ipaddress
from urllib.parse import urlparse

# FastAPIアプリケーションのインスタンス作成
app = FastAPI(
    title="N8N Python Server",
    description="FastAPIを使用したシンプルなAPIサーバー",
    version="1.0.0"
)

# データモデルの定義（サンプル）
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool = True

class Message(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None

# サンプルデータ
items_db = []

# ルート（メインページ）
@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>N8N Python Server</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            .endpoint { background: #f4f4f4; padding: 10px; margin: 10px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>N8N Python Server</h1>
        <p>FastAPIを使用したAPIサーバーが正常に動作しています。</p>

        <h2>利用可能なエンドポイント：</h2>
        <div class="endpoint"><strong>GET /</strong> - このページ</div>
        <div class="endpoint"><strong>GET /health</strong> - ヘルスチェック</div>
        <div class="endpoint"><strong>GET /items</strong> - 全アイテム取得</div>
        <div class="endpoint"><strong>POST /items</strong> - アイテム追加</div>
        <div class="endpoint"><strong>GET /items/{item_id}</strong> - 特定アイテム取得</div>
        <div class="endpoint"><strong>PUT /items/{item_id}</strong> - アイテム更新</div>
        <div class="endpoint"><strong>DELETE /items/{item_id}</strong> - アイテム削除</div>
        <div class="endpoint"><strong>POST /url-contents</strong> - URLコンテンツの取得（request/browser × raw/markdown/readability）</div>
        <div class="endpoint"><strong>GET /docs</strong> - Swagger UI（API仕様書）</div>

        <p><a href="/docs">API仕様書を見る</a></p>
    </body>
    </html>
    """
    return html_content

# ヘルスチェックエンドポイント
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Server is running"}

# 全アイテム取得
@app.get("/items")
async def get_items():
    return {"items": items_db, "count": len(items_db)}

# アイテム追加
@app.post("/items")
async def create_item(item: Item):
    item_dict = item.dict()
    item_dict["id"] = len(items_db) + 1
    items_db.append(item_dict)
    return {"message": "Item created successfully", "item": item_dict}

# 特定アイテム取得
@app.get("/items/{item_id}")
async def get_item(item_id: int):
    for item in items_db:
        if item["id"] == item_id:
            return item
    return {"error": "Item not found"}, 404

# アイテム更新
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    for i, existing_item in enumerate(items_db):
        if existing_item["id"] == item_id:
            item_dict = item.dict()
            item_dict["id"] = item_id
            items_db[i] = item_dict
            return {"message": "Item updated successfully", "item": item_dict}
    return {"error": "Item not found"}, 404

# アイテム削除
@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    for i, item in enumerate(items_db):
        if item["id"] == item_id:
            deleted_item = items_db.pop(i)
            return {"message": "Item deleted successfully", "item": deleted_item}
    return {"error": "Item not found"}, 404

# メッセージエンドポイント（汎用）
@app.post("/message")
async def send_message(message: Message):
    return {
        "received_message": message.message,
        "received_data": message.data,
        "response": "Message received successfully",
        "timestamp": "2025-01-22T01:23:31Z"
    }


# URL取得API 用のPydanticモデル
class UrlFetchRequest(BaseModel):
    """URLコンテンツ取得のリクエストモデル"""
    url: HttpUrl
    fetch_method: FetchMethod = Field(default=FetchMethod.REQUEST, description="コンテンツの取得方法")
    process_method: ProcessMethod = Field(default=ProcessMethod.RAW, description="コンテンツの処理方法")
    timeout: int = Field(default=30, ge=1, le=600, description="リクエストのタイムアウト（秒）")
    wait_for_js: int = Field(default=3000, ge=0, le=60000, description="browser取得時のJS待機（ミリ秒）")
    headers: Optional[Dict[str, str]] = Field(default=None, description="追加のHTTPヘッダー")
    allow_redirects: bool = Field(default=False, description="リダイレクトを許可するか（SSRF軽減のためデフォルトFalse）")
    max_bytes: int = Field(default=int(os.getenv("URL_FETCH_MAX_BYTES", "2000000")), ge=10_000, le=50_000_000, description="取得する最大バイト数（request取得時）")
    max_chars: int = Field(default=int(os.getenv("URL_FETCH_MAX_CHARS", "1000000")), ge=10_000, le=10_000_000, description="返却文字数の上限（超過分は切り捨て）")


class UrlFetchResponse(BaseModel):
    """URLコンテンツ取得のレスポンスモデル"""
    url: HttpUrl
    fetch_method: FetchMethod
    process_method: ProcessMethod
    content: str
    length: int


def _sanitize_headers(headers: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
    if not headers:
        return None
    # セキュリティ上の理由から危険なヘッダーは除外
    blocked = {"host", "content-length", "transfer-encoding", "connection"}
    clean: Dict[str, str] = {}
    for k, v in headers.items():
        lk = k.lower().strip()
        if lk in blocked:
            continue
        clean[lk] = v
    return clean or None


def _is_ip_dangerous(ip_str: str) -> bool:
    ip = ipaddress.ip_address(ip_str)
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def _assert_url_safe(raw_url: str) -> None:
    parsed = urlparse(raw_url)
    host = parsed.hostname or ""
    # ローカルホスト系や.localは拒否
    if host in {"localhost", "localhost.localdomain", "local"} or host.endswith(".local"):
        raise HTTPException(status_code=400, detail="危険なホスト名は許可されていません")
    try:
        infos = socket.getaddrinfo(host, None)
    except Exception:
        raise HTTPException(status_code=400, detail="ホスト名解決に失敗しました")
    ips = {info[4][0] for info in infos if info and info[4]}
    if not ips:
        raise HTTPException(status_code=400, detail="有効なIPアドレスが見つかりません")
    for ip in ips:
        if _is_ip_dangerous(ip):
            raise HTTPException(status_code=400, detail="プライベート/危険なアドレスは許可されていません")


@app.post("/url-contents", response_model=UrlFetchResponse)
def fetch_url_contents(payload: UrlFetchRequest) -> UrlFetchResponse:
    """指定URLのコンテンツを取得し、指定した方法で処理して返す。

    - fetch_method: `request` or `browser`
    - process_method: `raw`, `markdown`, or `readability`
    - Optional: `timeout`, `wait_for_js`, `headers`
    """
    # SSRFプリチェック（事前にホスト解決とIP帯域検査）
    _assert_url_safe(str(payload.url))

    try:
        content = get_url_content(
            str(payload.url),
            fetch_method=payload.fetch_method,
            process_method=payload.process_method,
            timeout=payload.timeout,
            wait_for_js=payload.wait_for_js,
            headers=_sanitize_headers(payload.headers),
            allow_redirects=payload.allow_redirects,
            max_bytes=payload.max_bytes,
            max_chars=payload.max_chars,
        )
        return UrlFetchResponse(
            url=payload.url,
            fetch_method=payload.fetch_method,
            process_method=payload.process_method,
            content=content,
            length=len(content or ""),
        )
    except ImportError as e:
        raise HTTPException(status_code=400, detail=f"必要なライブラリが不足しています: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL取得時にエラーが発生しました: {e}")

# サーバー起動（開発用）
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info",
    )
