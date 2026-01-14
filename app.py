from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from core.osint import deep_extract
import json, asyncio

app = FastAPI(title="Shadow-Reaper", version="1.0")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        handle = json.loads(data)["handle"]
        report = await asyncio.to_thread(deep_extract, handle)
        await websocket.send_json(report)