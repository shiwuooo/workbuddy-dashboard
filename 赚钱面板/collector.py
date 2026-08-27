#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
赚钱面板 - 采集器（零成本 / 纯标准库 / 无需 API Key / 不调用任何 AI）
每天定时运行：
  1) 抓取 feeds.json 里的 RSS/Atom 源 -> data.json（供「资讯流」标签）
  2) 同步 D:\\workbuddy\\赚钱日报\\ 下的 AI 解读 .md -> digests/（供「AI 每日解读」标签）

运行：
  py collector.py          # 立即采集一次
  （register_task.bat 会把它注册成每天 09:00 自动跑）
"""
import json
import os
import ssl
import html
import re
import datetime
import shutil
from email.utils import parsedate_to_datetime
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
FEEDS_FILE = os.path.join(BASE, "feeds.json")
OUT_FILE = os.path.join(BASE, "data.json")
DIGEST_SRC = "D:/workbuddy/赚钱日报"
DIGEST_DST = os.path.join(BASE, "digests")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MakeMoneyPanel/1.0"
TIMEOUT = 8  # 单源超时（秒）；沙箱/弱网下避免卡太久

# 不校验证书，兼容个别源证书异常（仅抓公开资讯，无登录）
_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT, context=_CTX) as r:
        raw = r.read()
    enc = r.headers.get_content_charset() or "utf-8"
    return raw.decode(enc, errors="replace")


def clean(t):
    if not t:
        return ""
    t = re.sub(r"<[^>]+>", "", t)
    return html.unescape(t).strip()


def child_local(el, local):
    for c in list(el):
        if c.tag.split("}")[-1] == local:
            return c
    return None


def text_of(el, local):
    e = child_local(el, local)
    if e is None:
        return ""
    return (e.text or "").strip()


def to_epoch(s):
    if not s:
        return 0
    s = s.strip()
    try:
        return parsedate_to_datetime(s).timestamp()
    except Exception:
        pass
    try:
        return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except Exception:
        pass
    return 0


def parse(xml_text):
    import xml.etree.ElementTree as ET
    items = []
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return items
    for it in root.iter("item"):
        title = clean(text_of(it, "title"))
        link = text_of(it, "link")
        desc = clean(text_of(it, "description") or text_of(it, "encoded"))
        pub = text_of(it, "pubDate") or text_of(it, "date")
        items.append({"title": title, "link": link, "desc": desc[:280], "pub": pub})
    for it in root.iter():
        if it.tag.split("}")[-1] != "entry":
            continue
        title = clean(text_of(it, "title"))
        link = ""
        for l in it.findall("*"):
            if l.tag.split("}")[-1] == "link" and l.get("href"):
                link = l.get("href")
                break
        desc = clean(text_of(it, "summary") or text_of(it, "content"))
        pub = text_of(it, "updated") or text_of(it, "published")
        items.append({"title": title, "link": link, "desc": desc[:280], "pub": pub})
    return items


def ascii_safe(s, n=200):
    """把任意字符串压成 ASCII，避免写入 JSON 时编码崩溃。"""
    if s is None:
        return ""
    try:
        return ("%s: %s" % (type(s).__name__, s)).encode("ascii", "replace").decode("ascii")[:n]
    except Exception:
        return "[未知错误]"


def sync_digests():
    """把 AI 每日解读 .md 复制到面板 digests/，并生成 index.json（历史列表）"""
    os.makedirs(DIGEST_DST, exist_ok=True)
    records = []
    if os.path.isdir(DIGEST_SRC):
        for fn in sorted(os.listdir(DIGEST_SRC)):
            if not fn.endswith(".md"):
                continue
            sp = os.path.join(DIGEST_SRC, fn)
            try:
                with open(sp, encoding="utf-8") as f:
                    txt = f.read()
            except Exception:
                continue
            try:
                shutil.copy2(sp, os.path.join(DIGEST_DST, fn))
            except Exception:
                pass
            title = fn.replace(".md", "")
            for line in txt.splitlines():
                s = line.strip()
                if s.startswith("#"):
                    title = s.lstrip("#").strip()
                    break
                if s:
                    title = s
                    break
            records.append({"file": fn, "title": title, "date": fn.replace(".md", "")})
        records.sort(key=lambda r: r["date"], reverse=True)
    with open(os.path.join(DIGEST_DST, "index.json"), "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    return len(records)


def main():
    with open(FEEDS_FILE, encoding="utf-8") as f:
        cfg = json.load(f)
    rsshub_base = cfg.get("rsshub_base", "https://rsshub.app").rstrip("/")
    results = []
    ok_count = 0
    fail_count = 0
    for feed in cfg.get("feeds", []):
        name = feed.get("name", "未知")
        region = feed.get("region", "海外")
        cat = feed.get("category", "其他")
        limit = feed.get("limit", 12)
        url = (rsshub_base + feed["route"]) if feed.get("rsshub") else feed["url"]
        try:
            items = parse(fetch(url))
            if not items:
                raise ValueError("返回为空或解析不到条目")
            for it in items[:limit]:
                it.update({"source": name, "region": region, "category": cat})
                results.append(it)
            ok_count += 1
        except Exception as e:
            results.append({
                "source": name, "region": region, "category": cat,
                "title": "[抓取失败] " + name,
                "link": "", "desc": ascii_safe(e), "pub": "",
            })
            fail_count += 1
    results.sort(key=lambda x: to_epoch(x.get("pub", "")), reverse=True)
    out = {
        "updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "ok": ok_count,
        "fail": fail_count,
        "items": results,
        "notice": "每天 09:00 自动更新（由 register_task.bat 注册）。想加源改 feeds.json 即可。失败源多因当前网络环境拦截，换到有完整外网的机器即可正常。",
    }
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=True, indent=2)
    n = sync_digests()
    print("OK 采集 %d 条（成功源 %d / 失败 %d）+ 同步 %d 期 AI 解读 -> 面板目录"
          % (len(results), ok_count, fail_count, n))


if __name__ == "__main__":
    main()
