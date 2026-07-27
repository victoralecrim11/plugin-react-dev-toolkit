#!/usr/bin/env python3
"""Project Hub local: Python standard library + JSON persistence."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from datetime import datetime, timezone
import json, webbrowser

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "projetos-data.json"
HTML_FILE = ROOT / "dashboard-template.html"

DEFAULT = {"projects": [], "components": [], "reviews": [], "checklists": {}}

def load_data():
    if not DATA_FILE.exists(): return DEFAULT.copy()
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        for key, value in DEFAULT.items(): data.setdefault(key, value)
        return data
    except (OSError, json.JSONDecodeError): return DEFAULT.copy()

def save_data(data):
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def stamp(item):
    item["updatedAt"] = datetime.now(timezone.utc).isoformat()
    item.setdefault("id", str(int(datetime.now(timezone.utc).timestamp() * 1000000)))
    return item

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs): super().__init__(*args, directory=str(ROOT), **kwargs)
    def send_json(self, status, payload):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length).decode("utf-8"))
    def do_GET(self):
        if self.path == "/api/data": return self.send_json(200, load_data())
        if self.path in ("/", "/index.html"): self.path = "/dashboard-template.html"
        return super().do_GET()
    def do_POST(self):
        try: payload = self.read_json()
        except json.JSONDecodeError: return self.send_json(400, {"error": "JSON inválido"})
        data = load_data(); collection = {"/api/projects": "projects", "/api/components": "components", "/api/reviews": "reviews"}.get(self.path)
        if collection:
            item = stamp(payload); items = data[collection]
            old = next((i for i, value in enumerate(items) if value.get("id") == item["id"]), None)
            if old is None: items.append(item)
            else: items[old] = item
            save_data(data); return self.send_json(200, item)
        if self.path == "/api/checklists":
            project_id = str(payload.get("projectId", "")); data["checklists"][project_id] = payload.get("items", {})
            save_data(data); return self.send_json(200, data["checklists"][project_id])
        return self.send_json(404, {"error": "Endpoint não encontrado"})
    def do_DELETE(self):
        parts = self.path.strip("/").split("/")
        if len(parts) != 3 or parts[0] != "api": return self.send_json(404, {"error": "Rota inválida"})
        collection = {"projects": "projects", "components": "components", "reviews": "reviews"}.get(parts[1])
        if not collection: return self.send_json(404, {"error": "Coleção inválida"})
        data = load_data(); data[collection] = [x for x in data[collection] if x.get("id") != parts[2]]; save_data(data)
        return self.send_json(200, {"ok": True})

if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8766), Handler)
    print("Project Hub em http://127.0.0.1:8766")
    webbrowser.open("http://127.0.0.1:8766")
    try: server.serve_forever()
    except KeyboardInterrupt: print("\nServidor encerrado.")
