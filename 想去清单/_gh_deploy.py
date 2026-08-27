#!/usr/bin/env python3
# 想去清单 -> GitHub Pages 单文件部署（路径 A）
# 用法: GH_TOKEN=ghp_xxx python _gh_deploy.py
# 只部署 index.html（工具本体），用户数据在浏览器 localStorage，不入库，无隐私泄露
import os, base64, json, time, sys, urllib.request, urllib.error

TOKEN = os.environ.get("GH_TOKEN")
if not TOKEN:
    print("ERROR: 缺少 GH_TOKEN 环境变量（你的 GitHub token 已过期，需要一个有效的）")
    sys.exit(2)

OWNER = "shiwuooo"          # 你的 GitHub 账号（shiwuooo.github.io）
REPO   = "xiangqu-qingdan"  # 仓库名（想去清单）
BRANCH = "main"
API    = "https://api.github.com"

def api(method, path, body=None, _try=0):
    url = API + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "wb-deploy")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        txt = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(txt)
        except Exception:
            return e.code, {"raw": txt}

def put_file(path, content_b64, message):
    st, resp = api("GET", f"/repos/{OWNER}/{REPO}/contents/{path}?ref={BRANCH}")
    sha = resp.get("sha") if st == 200 else None
    body = {"message": message, "content": content_b64, "branch": BRANCH}
    if sha:
        body["sha"] = sha
    st, resp = api("PUT", f"/repos/{OWNER}/{REPO}/contents/{path}", body)
    return st, resp

# 1) 建仓库（已存在则复用）
st, resp = api("POST", "/user/repos", {"name": REPO, "private": False, "auto_init": True})
if st == 201:
    print("仓库已创建:", REPO)
elif st == 422:
    print("仓库已存在，复用:", REPO)
else:
    print("建仓库失败", st, resp); sys.exit(1)
time.sleep(2)

# 2) 开 Pages（409=已开；失败重试）
for i in range(5):
    st, resp = api("POST", f"/repos/{OWNER}/{REPO}/pages",
                   {"source": {"branch": BRANCH, "path": "/"}})
    if st in (201, 409):
        print("Pages 已开启/已存在")
        break
    print(f"Pages 开启重试 {i+1}...", st, resp.get("message", ""))
    time.sleep(3)

# 3) 上传 index.html
with open("index.html", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()
st, resp = put_file("index.html", b64, "deploy 想去清单")
if st in (200, 201):
    print("index.html 已上传")
else:
    print("上传 index.html 失败", st, resp); sys.exit(1)

# 4) 加 .nojekyll（跳过 Jekyll 构建）
st, resp = put_file(".nojekyll", base64.b64encode(b"").decode(), "add .nojekyll")
print(".nojekyll:", "ok" if st in (200, 201) else f"skip({st})")

print("=" * 40)
print("部署完成！约 1-3 分钟后可访问：")
print(f"  https://{OWNER}.github.io/{REPO}/")
print("注意：网址是公开的工具壳，你的'想去的地方'存在浏览器本地，不会上传。")
