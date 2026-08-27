#!/usr/bin/env python3
# 大庆旅游攻略 -> GitHub Pages 部署（Contents API 逐文件）
# token 从 .gh_token 复用，不落盘不打印
import os, re, base64, json, time, sys, urllib.request, urllib.error
from urllib.parse import quote

TOKEN = open(r"D:/workbuddy/国考申论/求是申论素材库/.gh_token", encoding="utf-8").read().strip()
if not TOKEN:
    print("ERROR: 未找到 token"); sys.exit(2)

OWNER = "shiwuooo"
REPO = "daqing-travel"
BRANCH = "main"
API = "https://api.github.com"
SRC = r"D:/workbuddy/旅游攻略"
FILES = ["index.html", "大庆2.5天旅游攻略.html", "大庆游览地图.html", ".nojekyll"]

def api(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method)
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "wb-deploy")
    if data: req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        txt = e.read().decode("utf-8", "replace")
        try: return e.code, json.loads(txt)
        except Exception: return e.code, {"raw": txt}

# 1) 建仓库
st, resp = api("POST", "/user/repos", {"name": REPO, "private": False, "auto_init": True})
print("仓库:", "已创建" if st == 201 else ("已存在" if st == 422 else f"失败 {st} {resp}"))
if st not in (201, 422): sys.exit(1)
time.sleep(2)

# 2) 开 Pages
for i in range(5):
    st, resp = api("POST", f"/repos/{OWNER}/{REPO}/pages", {"source": {"branch": BRANCH, "path": "/"}})
    if st in (201, 409):
        print("Pages 已开/已存在"); break
    print(f"Pages 重试 {i+1}"); time.sleep(3)

# 3) 逐文件 PUT
for fn in FILES:
    with open(os.path.join(SRC, fn), "rb") as f:
        content = base64.b64encode(f.read()).decode()
    q = quote(fn)
    st, resp = api("GET", f"/repos/{OWNER}/{REPO}/contents/{q}?ref={BRANCH}")
    sha = resp.get("sha") if st == 200 else None
    body = {"message": f"deploy {fn}", "content": content, "branch": BRANCH}
    if sha: body["sha"] = sha
    st, resp = api("PUT", f"/repos/{OWNER}/{REPO}/contents/{q}", body)
    print(f"上传 {fn}: {'OK' if st in (200, 201) else 'FAIL ' + str(st)}")

# 4) 验证
st, resp = api("GET", f"/repos/{OWNER}/{REPO}/pages")
print("Pages 状态:", resp.get("status", resp))
print("URL: https://shiwuooo.github.io/daqing-travel/")
