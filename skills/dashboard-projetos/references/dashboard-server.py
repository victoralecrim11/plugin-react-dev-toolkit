#!/usr/bin/env python3
"""Project Hub local: Python standard library + JSON persistence."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlsplit, parse_qs
import json, os, re, sys, webbrowser
import urllib.request, urllib.error

APP_VERSION = "2026-07-27-v5"

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "projetos-data.json"
CONFIG_FILE = ROOT / "dashboard-config.json"
HTML_FILE = ROOT / "dashboard-template.html"

DEFAULT = {"projects": [], "components": [], "reviews": [], "checklists": {}}
DEFAULT_CONFIG = {"scanRoot": str(Path.home() / "Downloads"), "githubUsername": "", "githubToken": ""}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", ".expo", "coverage", ".turbo", ".cache"}
REACT_DEP_MARKERS = ("react", "react-native", "next", "expo")

def load_data():
    if not DATA_FILE.exists(): return json.loads(json.dumps(DEFAULT))
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        for key, value in DEFAULT.items(): data.setdefault(key, json.loads(json.dumps(value)))
        return data
    except (OSError, json.JSONDecodeError): return json.loads(json.dumps(DEFAULT))

def save_data(data):
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def load_config():
    if not CONFIG_FILE.exists(): return DEFAULT_CONFIG.copy()
    try:
        cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        for key, value in DEFAULT_CONFIG.items(): cfg.setdefault(key, value)
        return cfg
    except (OSError, json.JSONDecodeError): return DEFAULT_CONFIG.copy()

def save_config(cfg):
    CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")

def stamp(item):
    item["updatedAt"] = datetime.now(timezone.utc).isoformat()
    if not item.get("id"):
        item["id"] = str(int(datetime.now(timezone.utc).timestamp() * 1000000))
    return item

def scan_projects(root, max_depth=6):
    results = []
    try:
        root_path = Path(root).expanduser().resolve()
    except (OSError, RuntimeError):
        return results
    if not root_path.exists() or not root_path.is_dir():
        return results
    root_depth = len(root_path.parts)
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        depth = len(Path(dirpath).parts) - root_depth
        if depth > max_depth:
            dirnames[:] = []
            continue
        if "package.json" not in filenames:
            continue
        try:
            pkg = json.loads((Path(dirpath) / "package.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        if not any(marker in deps for marker in REACT_DEP_MARKERS):
            continue
        platform = ("Expo" if "expo" in deps else "Next.js" if "next" in deps
                    else "React Native" if "react-native" in deps else "React")
        stack = [k for k in ("react", "react-native", "next", "expo", "typescript", "zustand", "redux", "tailwindcss") if k in deps]
        results.append({
            "name": pkg.get("name") or Path(dirpath).name,
            "path": str(dirpath),
            "reactVersion": deps.get("react", deps.get("react-native", "")),
            "platform": platform,
            "stack": ", ".join(stack),
        })
        dirnames[:] = []  # nao desce dentro de um projeto ja identificado
    return results

CATEGORY_HINTS = ["atoms", "molecules", "organisms", "templates", "pages", "screens", "hooks", "layout", "layouts", "components"]
IGNORED_SUFFIXES = (".test.tsx", ".test.jsx", ".spec.tsx", ".spec.jsx", ".stories.tsx", ".stories.jsx", ".d.ts")

def scan_components(root, max_depth=8):
    results = []
    try:
        root_path = Path(root).expanduser().resolve()
    except (OSError, RuntimeError):
        return results
    if not root_path.exists() or not root_path.is_dir():
        return results
    root_depth = len(root_path.parts)
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        depth = len(Path(dirpath).parts) - root_depth
        if depth > max_depth:
            dirnames[:] = []
            continue
        for filename in filenames:
            if not filename.endswith((".tsx", ".jsx")): continue
            if filename.endswith(IGNORED_SUFFIXES): continue
            stem = filename.rsplit(".", 1)[0]
            if not stem[:1].isupper(): continue  # convencao de componente React: PascalCase
            file_path = Path(dirpath) / filename
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            looks_like_component = (
                re.search(r"export\s+default\s+function\s+" + re.escape(stem), content)
                or re.search(r"export\s+(default\s+)?(const|function|class)\s+" + re.escape(stem), content)
                or "export default" in content
            )
            if not looks_like_component: continue
            parent_names = [p.lower() for p in Path(dirpath).parts[root_depth:]]
            category = next((h for h in CATEGORY_HINTS if h in parent_names), "component")
            results.append({
                "name": stem,
                "path": str(file_path.relative_to(root_path)),
                "category": category,
            })
    return results

def github_api(path, token=""):
    url = "https://api.github.com" + path
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "react-dev-hub-dashboard"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        msg = "Usuario/token invalido ou limite de requisicoes atingido" if e.code in (401, 403) else "GitHub retornou %s" % e.code
        return None, msg
    except urllib.error.URLError:
        return None, "Sem conexao com a internet"

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs): super().__init__(*args, directory=str(ROOT), **kwargs)

    def send_json(self, status, payload):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self):
        parsed = urlsplit(self.path)
        qs = parse_qs(parsed.query)

        if parsed.path == "/api/version":
            return self.send_json(200, {"version": APP_VERSION, "root": str(ROOT), "html": str(HTML_FILE), "data": str(DATA_FILE)})
        if parsed.path == "/api/data": return self.send_json(200, load_data())
        if parsed.path == "/api/config": return self.send_json(200, load_config())

        if parsed.path == "/api/scan":
            cfg = load_config()
            scan_root = qs.get("path", [cfg.get("scanRoot", "")])[0]
            found = scan_projects(scan_root)
            registered = {p.get("path") for p in load_data()["projects"]}
            for item in found: item["alreadyRegistered"] = item["path"] in registered
            return self.send_json(200, {"root": scan_root, "found": found})

        if parsed.path == "/api/scan-components":
            project_id = qs.get("projectId", [""])[0]
            data = load_data()
            project = next((p for p in data["projects"] if str(p.get("id")) == str(project_id)), None)
            if not project:
                return self.send_json(404, {"error": "Projeto nao encontrado (id %s)" % project_id})
            if not project.get("path"):
                return self.send_json(400, {"error": "Este projeto nao tem um caminho local salvo. Edite o projeto e preencha o campo 'Caminho local'."})
            if not Path(project["path"]).expanduser().is_dir():
                return self.send_json(400, {"error": "A pasta '%s' nao existe ou nao e acessivel." % project["path"]})
            found = scan_components(project["path"])
            registered = {(c.get("project"), c.get("path")) for c in data["components"]}
            for c in found: c["alreadyRegistered"] = (project.get("name"), c["path"]) in registered
            return self.send_json(200, {"projectId": project_id, "projectName": project.get("name", ""),
                                        "projectPath": project.get("path", ""), "found": found})

        if parsed.path == "/api/github/repos":
            cfg = load_config()
            username = cfg.get("githubUsername", "")
            if not username: return self.send_json(400, {"error": "Configure seu usuario do GitHub em Configuracoes."})
            result, err = github_api("/users/%s/repos?per_page=100&sort=updated" % username, cfg.get("githubToken", ""))
            if err: return self.send_json(502, {"error": err})
            registered = {p.get("repoUrl") for p in load_data()["projects"]}
            repos = [{
                "name": r["name"], "fullName": r["full_name"], "description": r.get("description") or "",
                "language": r.get("language") or "", "stars": r.get("stargazers_count", 0),
                "private": r.get("private", False), "url": r.get("html_url"), "pushedAt": r.get("pushed_at"),
                "alreadyRegistered": r["full_name"] in registered,
            } for r in result]
            return self.send_json(200, repos)

        if parsed.path == "/api/github/repo-info":
            repo = qs.get("repo", [""])[0]
            if not repo: return self.send_json(400, {"error": "Parametro repo e obrigatorio (owner/nome)."})
            cfg = load_config()
            info, err = github_api("/repos/" + repo, cfg.get("githubToken", ""))
            if err: return self.send_json(502, {"error": err})
            commits, cerr = github_api("/repos/%s/commits?per_page=1" % repo, cfg.get("githubToken", ""))
            last_msg = commits[0]["commit"]["message"].split("\n")[0] if not cerr and commits else ""
            last_date = commits[0]["commit"]["author"]["date"] if not cerr and commits else ""
            return self.send_json(200, {
                "stars": info.get("stargazers_count", 0), "defaultBranch": info.get("default_branch", ""),
                "lastCommitMessage": last_msg, "lastCommitDate": last_date,
            })

        if parsed.path in ("/", "/index.html", "/dashboard-template.html"):
            return self.serve_html()
        return super().do_GET()

    def serve_html(self):
        # Le o HTML do disco a cada requisicao e envia com no-store, sem passar pelo cache
        # condicional (If-Modified-Since / ETag) do SimpleHTTPRequestHandler. Era esse cache
        # que gerava "304 Not Modified" e fazia o navegador continuar usando a versao antiga
        # do arquivo mesmo depois de ele ter sido substituido no disco.
        try:
            raw = HTML_FILE.read_bytes()
        except OSError:
            return self.send_json(404, {"error": "dashboard-template.html nao encontrado em " + str(HTML_FILE)})
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self):
        try: payload = self.read_json()
        except json.JSONDecodeError: return self.send_json(400, {"error": "JSON invalido"})

        if self.path == "/api/config":
            cfg = load_config(); cfg.update(payload); save_config(cfg)
            return self.send_json(200, cfg)

        data = load_data()
        collection = {"/api/projects": "projects", "/api/components": "components", "/api/reviews": "reviews"}.get(self.path)
        if collection:
            item = stamp(payload); items = data[collection]
            old = next((i for i, value in enumerate(items) if value.get("id") == item["id"]), None)
            if old is None: items.append(item)
            else: items[old] = item
            save_data(data); return self.send_json(200, item)
        if self.path == "/api/checklists":
            project_id = str(payload.get("projectId", "")); data["checklists"][project_id] = payload.get("items", {})
            save_data(data); return self.send_json(200, data["checklists"][project_id])
        return self.send_json(404, {"error": "Endpoint nao encontrado"})

    def do_DELETE(self):
        parts = self.path.strip("/").split("/")
        if len(parts) != 3 or parts[0] != "api": return self.send_json(404, {"error": "Rota invalida"})
        collection = {"projects": "projects", "components": "components", "reviews": "reviews"}.get(parts[1])
        if not collection: return self.send_json(404, {"error": "Colecao invalida"})
        data = load_data(); data[collection] = [x for x in data[collection] if x.get("id") != parts[2]]; save_data(data)
        return self.send_json(200, {"ok": True})

if __name__ == "__main__":
    print("=" * 70)
    print(" Project Hub", APP_VERSION)
    print(" Pasta lida por este servidor :", ROOT)
    print(" HTML  :", HTML_FILE, "(existe)" if HTML_FILE.exists() else "(NAO ENCONTRADO!)")
    print(" Dados :", DATA_FILE, "(existe)" if DATA_FILE.exists() else "(sera criado no primeiro registro)")
    print("=" * 70)
    if not HTML_FILE.exists():
        print("\nERRO: o dashboard-template.html precisa estar NA MESMA PASTA deste .py.")
        print("Coloque os dois arquivos juntos em", ROOT, "e rode de novo.\n")
        sys.exit(1)
    server = ThreadingHTTPServer(("127.0.0.1", 8766), Handler)
    print("Abra http://127.0.0.1:8766")
    webbrowser.open("http://127.0.0.1:8766")
    try: server.serve_forever()
    except KeyboardInterrupt: print("\nServidor encerrado.")