from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

# FastAPIアプリケーションのインスタンス作成
app = FastAPI(
    title="N8N Python Server",
    description="FastAPIを使用したシンプルなAPIサーバー",
    version="1.0.0"
)

# データモデルの定義
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

# サーバー起動（開発用）
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
