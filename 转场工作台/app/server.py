# -*- coding: utf-8 -*-
import http.server
import socketserver
import json
import urllib.parse
import webbrowser
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent
VIDEOS = BASE / "videos"
DATAFILE = BASE / "data" / "transitions.json"
PORT = 8765

VIDEO_EXTS = {".mp4", ".mov", ".webm", ".m4v", ".avi", ".mkv"}
MIME = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".webm": "video/webm",
    ".m4v": "video/mp4",
    ".avi": "video/x-msvideo",
    ".mkv": "video/x-matroska",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
}


def ensure_data():
    DATAFILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATAFILE.exists():
        DATAFILE.write_text("[]", encoding="utf-8")


def load_items():
    ensure_data()
    try:
        return json.loads(DATAFILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_items(items):
    ensure_data()
    DATAFILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def scan_videos():
    items = load_items()
    known = {it.get("file") for it in items if it.get("file")}
    added = 0
    if VIDEOS.exists():
        for f in sorted(VIDEOS.iterdir()):
            if f.suffix.lower() in VIDEO_EXTS:
                if f.name in known:
                    continue
                items.append({
                    "id": f.name,
                    "title": f.stem,
                    "file": f.name,
                    "platform": "未知",
                    "transitionType": "待分类",
                    "difficulty": "未知",
                    "style": "",
                    "rating": 0,
                    "tags": [],
                    "notes": "",
                    "dateAdded": time.strftime("%Y-%m-%d"),
                })
                added += 1
    if added:
        save_items(items)
    return added


class Handler(http.server.BaseHTTPRequestHandler):
    def _send(self, code, ctype, data):
        if isinstance(data, str):
            data = data.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_file(self, fp):
        if not fp.exists() or not fp.is_file():
            return self.send_error(404)
        ext = fp.suffix.lower()
        ctype = MIME.get(ext, "application/octet-stream")
        data = fp.read_bytes()
        total = len(data)
        rng = self.headers.get("Range")
        if rng and rng.startswith("bytes="):
            try:
                part = rng[len("bytes="):].split(",")[0]
                s, e = part.split("-")
                start = int(s) if s else 0
                end = int(e) if e else total - 1
                end = min(end, total - 1)
                chunk = data[start:end + 1]
                self.send_response(206)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Range", "bytes %d-%d/%d" % (start, end, total))
                self.send_header("Content-Length", str(len(chunk)))
                self.send_header("Accept-Ranges", "bytes")
                self.end_headers()
                self.wfile.write(chunk)
                return
            except Exception:
                pass
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(total))
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        p = u.path
        if p in ("/", "/index.html"):
            return self._serve_file(ROOT / "index.html")
        if p == "/api/items":
            return self._send(200, "application/json; charset=utf-8",
                              json.dumps(load_items(), ensure_ascii=False))
        if p == "/api/scan":
            added = scan_videos()
            return self._send(200, "application/json; charset=utf-8",
                              json.dumps({"added": added, "items": load_items()}, ensure_ascii=False))
        if p.startswith("/videos/"):
            name = urllib.parse.unquote(p[len("/videos/"):])
            return self._serve_file(VIDEOS / name)
        return self.send_error(404)

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/api/items":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            try:
                items = json.loads(raw)
            except Exception:
                return self.send_error(400)
            save_items(items)
            return self._send(200, "application/json; charset=utf-8",
                              json.dumps({"ok": True}, ensure_ascii=False))
        return self.send_error(404)

    def log_message(self, *a):
        pass


def open_browser():
    time.sleep(1.5)
    try:
        webbrowser.open("http://127.0.0.1:%d" % PORT)
    except Exception:
        pass


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    scan_videos()
    threading.Thread(target=open_browser, daemon=True).start()
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        print("转场工作台已启动: http://127.0.0.1:%d  (Ctrl+C 退出)" % PORT)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
