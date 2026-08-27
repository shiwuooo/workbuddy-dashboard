# -*- coding: utf-8 -*-
"""
个人工作台 · 本地后端（纯标准库，无第三方依赖）
启动：双击 启动.bat
访问：浏览器打开 http://localhost:8765
数据：本目录 data/ 下各模块 JSON + uploads/ 图片（可放进夸克网盘同步目录实现跨设备）
"""
import os
import json
import base64
import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
UPLOADS = os.path.join(DATA, "uploads")
os.makedirs(UPLOADS, exist_ok=True)

MODULES = ["shenlun", "xingce", "wangpan"]


def read_list(mod):
    p = os.path.join(DATA, mod + ".json")
    if not os.path.exists(p):
        return []
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def write_list(mod, arr):
    p = os.path.join(DATA, mod + ".json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(arr, f, ensure_ascii=False, indent=2)


def guess(fn):
    fn = fn.lower()
    if fn.endswith(".html"):
        return "text/html; charset=utf-8"
    if fn.endswith(".js"):
        return "application/javascript; charset=utf-8"
    if fn.endswith(".css"):
        return "text/css; charset=utf-8"
    if fn.endswith((".png", ".jpg", ".jpeg")):
        return "image/" + fn.split(".")[-1]
    if fn.endswith(".gif"):
        return "image/gif"
    return "application/octet-stream"


class H(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def _send(self, code, ctype, data):
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", ctype)
        self.end_headers()
        if isinstance(data, str):
            data = data.encode("utf-8")
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self._serve(os.path.join(ROOT, "index.html"),
                               "text/html; charset=utf-8")
        if self.path.startswith("/uploads/"):
            fn = os.path.basename(self.path)
            fp = os.path.join(UPLOADS, fn)
            if os.path.exists(fp):
                return self._serve(fp, guess(fn))
            return self._send(404, "text/plain; charset=utf-8", "not found")
        if self.path.startswith("/api/") and self.path.endswith("/list"):
            mod = self.path.split("/")[2]
            if mod in MODULES:
                return self._send(200, "application/json; charset=utf-8",
                                  json.dumps(read_list(mod), ensure_ascii=False))
        return self._send(404, "text/plain; charset=utf-8", "not found")

    def do_POST(self):
        if self.path.startswith("/api/") and self.path.endswith("/add"):
            mod = self.path.split("/")[2]
            if mod not in MODULES:
                return self._send(400, "text/plain; charset=utf-8", "bad module")
            try:
                n = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(n).decode("utf-8"))
            except Exception:
                return self._send(400, "text/plain; charset=utf-8", "bad body")
            arr = read_list(mod)
            body["id"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
            body["ts"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            arr.append(body)
            write_list(mod, arr)
            return self._send(200, "application/json; charset=utf-8",
                              json.dumps({"ok": True, "rec": body},
                                         ensure_ascii=False))
        if self.path == "/api/upload":
            try:
                n = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(n).decode("utf-8"))
                b64 = body.get("b64", "")
                name = body.get("filename", "upload.bin")
                ext = os.path.splitext(name)[1] or ".bin"
                fn = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + ext
                with open(os.path.join(UPLOADS, fn), "wb") as f:
                    f.write(base64.b64decode(b64.split(",", 1)[-1]))
                return self._send(200, "application/json; charset=utf-8",
                                  json.dumps({"ok": True, "url": "/uploads/" + fn},
                                             ensure_ascii=False))
            except Exception as e:
                return self._send(400, "text/plain; charset=utf-8", str(e))
        return self._send(404, "text/plain; charset=utf-8", "not found")

    def _serve(self, fp, ctype):
        if not os.path.exists(fp):
            return self._send(404, "text/plain; charset=utf-8", "not found")
        with open(fp, "rb") as f:
            self._send(200, ctype, f.read())

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = 8765
    print("个人工作台 running -> http://localhost:%d" % port)
    ThreadingHTTPServer(("0.0.0.0", port), H).serve_forever()
