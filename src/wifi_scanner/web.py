from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from .main import WiFiScanner

app = FastAPI(title="macOS WiFi Scanner")
package_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=package_dir / "static"), name="static")

templates = Jinja2Templates(directory=package_dir / "templates")
scanner = WiFiScanner()

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/scan")
async def scan_wifi():
    networks = scanner.scan()
    return networks
