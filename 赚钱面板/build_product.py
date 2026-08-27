# -*- coding: utf-8 -*-
"""
把 data.json + 项目库 + 最新 AI日报 打包成一个独立的 HTML 成品页面。
双击即用，不依赖 .bat / 本地服务器 / 外部文件。

本版新增：
  M1 趋势雷达 —— 规则打分（来源权重 + 新鲜度 + 高潜力词命中 + 信息差标），零积分、无需 AI
  M6 复盘看板 —— 纯前端 localStorage，记录你试过的信号/投入/回报/ROI
"""
import json
import os
import re
import glob
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
DIGEST_DIR = r"D:\workbuddy\赚钱日报"

# ---------- M1 趋势评分配置（纯规则，零积分） ----------
SOURCE_WEIGHT = {
    "Hacker News 创业": 8, "Reddit r/SideHustle": 7, "Reddit r/Entrepreneur": 7,
    "Reddit r/EntrepreneurRideAlong": 7, "Side Hustle Nation": 8, "Smart Passive Income": 7,
    "少数派": 7, "阮一峰周刊": 6, "36氪快讯": 8, "知乎·副业搜索": 5,
    "B站·副业赚钱": 5, "微博·副业赚钱": 5,
}
# 高潜力关键词：命中越多越值得盯（每个 +2，最多 +6）
HOT_KW = ["AI", "副业", "出海", "跨境", "银发", "被动收入", "自动化", "一人公司",
          "SaaS", "数字产品", "短视频", "本地生活", "低空经济", "Agent", "赚钱", "创业", "副业赚钱"]

# ---------- M7 风险哨兵（纯规则，零积分） ----------
# 命中即标注风险，级别：high（红线/骗局）/ warn（需警惕）/ low（资质留意）
RISK_RULES = [
    # 骗局特征：先交钱
    ("high", ["押金", "培训费", "学费", "入会费", "代理费", "加盟费", "保证金", "交会费",
              "先交钱", "交钱才能", "付费培训", "割韭菜", "杀猪盘", "交押金"],
     "先交钱/培训费/加盟费——典型骗局特征，直接拉黑"),
    # 传销/拉人头
    ("high", ["拉人头", "多级分销", "层级返利", "发展下线", "金字塔", "传销", "静态收益",
              "动态收益", "团队计酬"],
     "含多级分销/拉人头——传销风险，法律红线"),
    # 政策红线（绝对不碰）
    ("high", ["虚拟币", "加密货币", "币圈", "博彩", "赌博", "彩票", "私彩", "灰产", "黑产",
              "色情", "赌博平台", "网赚盘"],
     "涉及博彩/虚拟币/灰产——政策红线，绝对不碰"),
    # 封号/违规风险
    ("warn", ["薅羊毛", "刷单", "刷量", "搬砖套利", "违规搬运", "搬运号", "批量注册", "接码",
              "养号", "淘宝刷单", "刷信誉", "撸货"],
     "含薅羊毛/刷单/批量号——平台封号风险高，账号资产易清零"),
    # 夸大收益
    ("warn", ["日入过万", "月入十万", "躺赚", "轻松赚", "自动赚钱", "被动躺赢", "一夜暴富",
              "稳赚不赔", "保证收益", " guaranteed", "保收益"],
     "收益夸大（躺赚/保收益）——多半是引流话术，需警惕"),
    # 敏感合规
    ("low", ["医美", "保健", "金融理财", "荐股", "外汇", "期货", "保险代理", "烟草",
             "医疗器械", "私募"],
     "医美/金融/保健等——资质与合规要求高，普通人慎入"),
]


def to_epoch(s):
    if not s:
        return 0
    s = s.strip()
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S",
                "%a, %d %b %Y %H:%M:%S GMT", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).timestamp()
        except Exception:
            pass
    return 0


def score_items(items):
    """给每条资讯打分 + 标注信息差。原地修改并返回。"""
    now = time.time()
    for it in items:
        s = SOURCE_WEIGHT.get(it.get("source", ""), 6)
        ep = to_epoch(it.get("pub", ""))
        if ep:
            days = (now - ep) / 86400
            if days <= 7:
                s += 4
            elif days <= 30:
                s += 2
        text = (it.get("title", "") + " " + it.get("desc", "")).lower()
        hit = 0
        for kw in HOT_KW:
            if kw.lower() in text:
                hit += 1
        s += min(hit, 3) * 2
        region = it.get("region", "")
        cat = it.get("category", "")
        gap = ""
        if region == "海外" and any(k in cat for k in ["副业", "被动收入", "AI副业"]):
            gap = "海外已火·国内可做"
        elif region == "国内":
            gap = "国内已验证"
        it["score"] = min(s, 30)
        it["gap"] = gap
        it["pct"] = max(6, min(100, int(it["score"] / 30 * 100)))
        it["risk"] = detect_risk(it.get("title", ""), it.get("desc", ""))
    return items


def detect_risk(title, desc):
    """M7 风险哨兵：纯规则标注骗局/红线/封号风险。零积分。"""
    text = (title + " " + desc).lower()
    for level, kws, reason in RISK_RULES:
        for kw in kws:
            if kw.lower() in text:
                return {"level": level, "reason": reason}
    return {"level": "", "reason": ""}


# ---------- Markdown -> HTML（轻量） ----------
def md_to_html(md: str) -> str:
    h = md.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    h = re.sub(r"^# (.*)$", r"<h1>\1</h1>", h, flags=re.M)
    h = re.sub(r"^## (.*)$", r"<h2>\1</h2>", h, flags=re.M)
    h = re.sub(r"^### (.*)$", r"<h3>\1</h3>", h, flags=re.M)
    h = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", h)
    h = re.sub(r"\*(.*?)\*", r"<i>\1</i>", h)
    h = re.sub(r"^\> (.*)$", r"<blockquote>\1</blockquote>", h, flags=re.M)
    h = re.sub(r"`([^`]+)`", r"<code>\1</code>", h)

    lines = h.split("\n")
    out = []
    in_ul = in_ol = in_table = False
    thead = False
    rows = []

    def flush_table():
        nonlocal in_table, rows
        if in_table:
            out.append("<table>" + "\n".join(rows) + "</table>")
            in_table = False
            rows = []

    for line in lines:
        if line.startswith("|") and "|" in line[1:]:
            if not in_table:
                in_table = True
                thead = True
                rows = []
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if cells and all(re.fullmatch(r"[-:]+", c) for c in cells):
                thead = False
                continue
            tag = "th" if thead else "td"
            rows.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>")
            if thead:
                thead = False
            continue

        flush_table()

        if line.startswith("- "):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append("<li>" + line[2:] + "</li>")
        elif re.match(r"\d+\. ", line):
            if not in_ol:
                out.append("<ol>")
                in_ol = True
            out.append("<li>" + re.sub(r"^\d+\. ", "", line) + "</li>")
        else:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if line.strip():
                out.append("<p>" + line + "</p>")
            else:
                out.append("<br>")

    flush_table()
    if in_ul:
        out.append("</ul>")
    if in_ol:
        out.append("</ol>")
    return "\n".join(out)


FALLBACK_ITEMS = [
    {"region": "国内", "category": "平台接单", "source": "新浪", "title": "下半年干什么挣钱？猪八戒网、闲鱼、喜马拉雅新手接单价29.9元起", "desc": "线上技能接单成为新手副业热门选择：猪八戒网设计/文案/PPT美化50-100元小单、闲鱼简历优化29.9元起、喜马拉雅音频打赏。避开培训贷，先以低价小单积累数据和好评。", "link": "https://k.sina.cn/article_7879848900_1d5acf3c4068039g9u.html"},
    {"region": "国内", "category": "本地服务", "source": "今日头条", "title": "2026下半年普通人3个低成本落地赚钱赛道（全国通用，上手快）", "desc": "① AI本地商家代运营：399元/月起帮小店做短视频/团购；② 家电深度清洗：入秋后空调/油烟机清洗需求暴涨，日纯利400-700元；③ 银发便民服务：陪诊150-260元/半天，适老化改造单项利润100-300元。", "link": "https://www.toutiao.com/article/7661240830761517587"},
    {"region": "国内", "category": "AI副业", "source": "今日头条", "title": "2026下半年低门槛副业，适合上班族、宝妈，零成本起步", "desc": "大厂数据标注/音频转写（时薪15-45元）、闲鱼卖技能、1688→闲鱼一件代发、AI辅助自媒体、售卖电子资料。关键是信息差+执行力。", "link": "https://www.toutiao.com/a7664023638814884387"},
    {"region": "国内", "category": "内容创作", "source": "QQ看点", "title": "2026年，死磕这4个小项目，让你实现不上班也有收入", "desc": "网盘拉新（一份资料多份收入）、小红书开店（0粉丝可变现，教辅/百货）、社群团购（借助平台零囤货）。从小钱开始，积少成多。", "link": "https://so.html5.qq.com/page/real/search_news?docid=70000021_3266a61932f83852"},
    {"region": "国内", "category": "本地服务", "source": "QQ看点", "title": "网约车司机新副业爆火！2小时176元起，一个月能多赚3000元", "desc": "成都10万网约车司机解锁新身份“陪诊师”。滴滴上线“滴滴陪诊”入口，2小时176元起。陪诊服务2025年约740.6万人次，行业进入爆发期。", "link": "https://so.html5.qq.com/page/real/search_news?docid=70000021_5596a6de8a028152"},
    {"region": "海外", "category": "AI副业", "source": "mayursharma.co", "title": "Best Side Hustles to Start in 2026 (No Investment Needed)", "desc": "2026年零投资副业Top 10：AI内容创作、TikTok/Reels不露脸账号、AI缩略图/Logo设计、远程客服、AI辅助视频剪辑、数字产品、在线辅导、联盟营销、按需印刷、在线微任务。", "link": "https://mayursharma.co/best-side-hustles-to-start-in-2026-no-investment-needed"},
    {"region": "海外", "category": "被动收入", "source": "quickhustlehub.com", "title": "Passive Income With No Money in 2026: 10 Methods That Work", "desc": "最快路径是数字产品（PDF指南、Canva模板、清单），零库存、即时交付。新手1-2个月可预期100-500美元/月。关键：先选一个方法深耕90天，别贪多。", "link": "https://quickhustlehub.com/passive-income-with-no-money-in-2026-10-methods-that-work"},
    {"region": "海外", "category": "被动收入", "source": "bloggrower.com", "title": "17 Passive Income Ideas for Beginners With No Money [2026 Guide]", "desc": "四大类：内容资产（博客/YouTube不露脸/Newsletter）、数字产品（Canva模板/Etsy可打印/E-book KDP）、营销获客（高客单价联盟/推荐）、技能变现（股票素材/迷你课程/Chrome扩展）。", "link": "https://bloggrower.com/blog/passive-income-ideas-beginners-no-money-2026"},
    {"region": "海外", "category": "内容创作", "source": "dollarbreak.co.ke", "title": "Lazy Girl Online Income Ideas: Low Effort Ways to Make Money in 2026", "desc": "低门槛在线收入：卖Canva模板、卖电子书/迷你指南、图库授权照片/视频、不露脸YouTube/TikTok。核心建议：只选一个方向，第一周就发布第一个作品。", "link": "https://dollarbreak.co.ke/lazy-girl-online-income-ideas"}
]


def load_data():
    data_path = os.path.join(ROOT, "data.json")
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        data = {
            "updated": datetime.now().isoformat(),
            "ok": 0,
            "fail": 0,
            "items": [],
            "error": str(e),
        }
    valid = [it for it in data.get("items", []) if not (it.get("title") or "").startswith("[抓取失败]")]
    if not valid:
        data["items"] = FALLBACK_ITEMS
        data["ok"] = len(FALLBACK_ITEMS)
        data["fail"] = data.get("fail", 0)
        data["fallback"] = True
    else:
        data["items"] = valid
        data["fallback"] = False
    score_items(data["items"])
    return data


def load_projects():
    feeds_path = os.path.join(ROOT, "feeds.json")
    try:
        with open(feeds_path, "r", encoding="utf-8") as f:
            return json.load(f).get("projects", [])
    except Exception:
        return []


def load_gap():
    """M9 中外信息差：载入人工精选的套利案例 + 思考/逻辑层。"""
    p = os.path.join(ROOT, "信息差案例.json")
    try:
        with open(p, "r", encoding="utf-8") as f:
            cases = json.load(f)
    except Exception:
        return []
    for c in cases:
        if not c.get("risk"):
            c["risk"] = detect_risk(
                c.get("product", "") + " " + c.get("phenomenon", "")
            )
    return cases


def latest_digest():
    """返回 (日期字符串, markdown内容)"""
    try:
        files = glob.glob(os.path.join(DIGEST_DIR, "*.md"))
        files = [p for p in files if re.search(r"\d{4}-\d{2}-\d{2}", os.path.basename(p))]
        if not files:
            return None, "暂无 AI 日报。"
        latest = max(files, key=os.path.getmtime)
        date = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(latest)).group(1)
        with open(latest, "r", encoding="utf-8") as f:
            return date, f.read()
    except Exception as e:
        return None, f"读取日报失败：{e}"


def build():
    data = load_data()
    projects = load_projects()
    gap_cases = load_gap()
    gap_json = json.dumps(gap_cases, ensure_ascii=False)
    digest_date, digest_md = latest_digest()
    digest_title = f"AI每日解读 · {digest_date}" if digest_date else "AI每日解读"
    digest_html = md_to_html(digest_md)
    items_json = json.dumps(data.get("items", []), ensure_ascii=False)
    radar_items = sorted(
        [i for i in data.get("items", []) if not (i.get("title") or "").startswith("[抓取失败]")],
        key=lambda x: x.get("score", 0), reverse=True
    )[:15]
    radar_json = json.dumps(radar_items, ensure_ascii=False)
    projects_json = json.dumps(projects, ensure_ascii=False)

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>赚钱面板 · 成品</title>
<style>
:root{{--bg:#f6f7f9;--card:#fff;--text:#1f2937;--muted:#6b7280;--border:#e5e7eb;--accent:#2563eb;--accent2:#10b981;--radius:12px;--shadow:0 4px 6px -1px rgba(0,0,0,.07)}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--text);line-height:1.6}}
header{{position:sticky;top:0;background:rgba(255,255,255,.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--border);z-index:50}}
.nav{{max-width:1180px;margin:0 auto;padding:12px 16px;display:flex;gap:8px;overflow-x:auto}}
.nav button{{flex:0 0 auto;border:0;background:transparent;color:var(--muted);font-size:14px;font-weight:600;padding:8px 14px;border-radius:20px;cursor:pointer;white-space:nowrap}}
.nav button.active{{background:var(--accent);color:#fff}}
main{{max-width:1180px;margin:0 auto;padding:20px 16px 60px}}
.panel{{display:none}}
.panel.active{{display:block}}
h1{{font-size:22px;margin:0 0 6px}}
h2{{font-size:18px;margin:24px 0 12px;border-left:4px solid var(--accent);padding-left:10px}}
p{{margin:0 0 12px}}
a{{color:var(--accent);text-decoration:none}}
a:hover{{text-decoration:underline}}
.card{{background:var(--card);border-radius:var(--radius);box-shadow:var(--shadow);padding:16px;margin-bottom:14px}}
.top{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:8px}}
.badge{{font-size:11px;font-weight:700;padding:3px 8px;border-radius:999px;color:#fff}}
.badge.cn{{background:#ef4444}}
.badge.os{{background:#3b82f6}}
.tag{{font-size:12px;color:var(--muted);background:var(--bg);padding:3px 8px;border-radius:999px}}
.gap-tag{{font-size:11px;font-weight:700;padding:2px 8px;border-radius:999px;background:#fef3c7;color:#92400e}}
.risk-tag{{font-size:11px;font-weight:700;padding:2px 8px;border-radius:999px;color:#fff}}
.risk-tag.risk-high{{background:#dc2626}}
.risk-tag.risk-warn{{background:#f59e0b}}
.risk-tag.risk-low{{background:#6b7280}}
.card a.title{{font-size:16px;font-weight:700;display:block;margin-bottom:6px;line-height:1.4}}
.desc{{font-size:14px;color:#374151;margin-bottom:8px}}
.meta{{font-size:12px;color:var(--muted)}}
.empty{{text-align:center;color:var(--muted);padding:40px 0}}
.filters{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px;align-items:center}}
.filters select,.filters input{{padding:8px 12px;border:1px solid var(--border);border-radius:8px;font-size:14px;background:#fff}}
.filters input{{min-width:160px;flex:1 1 180px}}
.status-bar{{background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:10px 14px;font-size:13px;color:#1e40af;margin-bottom:16px}}
.status-bar.warn{{background:#fffbeb;border-color:#fde68a;color:#92400e}}
.score-row{{display:flex;align-items:center;gap:10px;margin-top:8px;font-size:12px;color:var(--muted)}}
.score-num{{font-weight:700;color:var(--accent);font-size:14px}}
.score-bar{{flex:1;height:6px;background:#e5e7eb;border-radius:3px;overflow:hidden;max-width:220px}}
.score-bar>span{{display:block;height:100%;background:linear-gradient(90deg,#10b981,#2563eb)}}
.markdown h1{{font-size:22px}}
.markdown h2{{font-size:18px;margin-top:20px}}
.markdown h3{{font-size:16px;margin-top:16px}}
.markdown table{{width:100%;border-collapse:collapse;font-size:13px;margin:12px 0;background:#fff;box-shadow:var(--shadow);border-radius:var(--radius);overflow:hidden}}
.markdown th,.markdown td{{border:1px solid var(--border);padding:8px;text-align:left}}
.markdown th{{background:#f3f4f6;font-weight:700}}
.markdown ul,.markdown ol{{margin:8px 0;padding-left:22px}}
.markdown blockquote{{border-left:4px solid var(--accent);margin:12px 0;padding:8px 14px;background:#eff6ff;color:#1e3a8a}}
.markdown code{{background:#f3f4f6;padding:2px 6px;border-radius:4px;font-size:12px}}
.proj{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}}
.proj .card{{padding:14px}}
.proj h3{{margin:0 0 6px;font-size:15px}}
.proj p{{font-size:13px;color:#4b5563;margin:0 0 10px}}
.btn{{display:inline-block;background:var(--accent);color:#fff;font-size:13px;font-weight:600;padding:6px 12px;border-radius:6px;border:0;cursor:pointer}}
.btn:hover{{text-decoration:none;background:#1d4ed8}}
.btn.green{{background:var(--accent2)}}
.btn.green:hover{{background:#059669}}
.btn.red{{background:#ef4444}}
.btn.red:hover{{background:#dc2626}}
.btn.tiny{{padding:4px 10px;font-size:12px}}
.about-step{{display:flex;gap:12px;margin-bottom:14px}}
.about-step .num{{flex:0 0 28px;height:28px;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px}}
.about-step div{{flex:1}}
.about-step h4{{margin:0 0 4px;font-size:15px}}
.about-step p{{margin:0;font-size:13px;color:#4b5563}}
.tip{{background:#ecfdf5;border:1px solid #a7f3d0;border-radius:8px;padding:12px 14px;font-size:13px;color:#065f46;margin:12px 0}}
.warning{{background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:12px 14px;font-size:13px;color:#991b1b;margin:12px 0}}
.footer{{text-align:center;color:var(--muted);font-size:12px;margin-top:30px}}
.review-form label{{display:block;font-size:13px;font-weight:600;margin:10px 0 4px}}
.review-form input,.review-form select,.review-form textarea{{width:100%;padding:8px 10px;border:1px solid var(--border);border-radius:8px;font-size:14px;font-family:inherit;box-sizing:border-box}}
.review-form .row{{display:flex;gap:10px;flex-wrap:wrap}}
.review-form .row>div{{flex:1;min-width:120px}}
.review-stats{{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0}}
.stat{{flex:1;min-width:130px;background:var(--card);border-radius:var(--radius);box-shadow:var(--shadow);padding:14px;text-align:center}}
.stat .v{{font-size:22px;font-weight:800}}
.stat .l{{font-size:12px;color:var(--muted)}}
.rv{{display:flex;gap:10px;align-items:flex-start;background:var(--card);border-radius:var(--radius);box-shadow:var(--shadow);padding:12px 14px;margin-bottom:10px}}
.rv .main{{flex:1}}
.rv .main h4{{margin:0 0 4px;font-size:15px}}
.rv .main .line{{font-size:13px;color:#4b5563}}
.rv .money{{font-weight:700}}
.rv .pos{{color:#059669}}
.rv .neg{{color:#dc2626}}
.rv .badge2{{font-size:11px;font-weight:700;padding:2px 8px;border-radius:999px;margin-right:6px}}
.badge2.do{{background:#dbeafe;color:#1e40af}}
.badge2.win{{background:#d1fae5;color:#065f46}}
.badge2.give{{background:#fee2e2;color:#991b1b}}
.radar-rank{{display:flex;align-items:center;gap:10px;margin-bottom:10px}}
.radar-rank .rk{{flex:0 0 26px;height:26px;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px}}
.gap-card .dir{{font-size:11px;font-weight:700;padding:2px 8px;border-radius:999px;background:#ede9fe;color:#6d28d9}}
.gap-card .type{{font-size:11px;font-weight:700;padding:2px 8px;border-radius:999px;background:#e0f2fe;color:#0369a1}}
.think{{margin-top:10px;border:1px solid var(--border);border-radius:8px;background:#fafafe;overflow:hidden}}
.think>summary{{cursor:pointer;font-size:13px;font-weight:700;color:#7c3aed;padding:8px 12px;list-style:none}}
.think>summary::-webkit-details-marker{{display:none}}
.think>summary::before{{content:"\\25B8 ";}}
.think[open]>summary::before{{content:"\\25BE ";}}
.think .body{{padding:0 14px 12px;font-size:13px;color:#374151;line-height:1.7}}
.think .body p{{margin:6px 0}}
.think .body b{{color:#6d28d9}}
</style>
</head>
<body>
<header>
  <div class="nav">
    <button class="active" onclick="show('feed')">📡 资讯流</button>
    <button onclick="show('radar')">🔥 趋势雷达</button>
    <button onclick="show('digest')">🤖 {digest_title}</button>
    <button onclick="show('projects')">📚 项目库</button>
    <button onclick="show('gap')">🌐 中外信息差</button>
    <button onclick="show('review')">📊 复盘看板</button>
    <button onclick="show('about')">ℹ️ 关于</button>
  </div>
</header>
<main>
  <section id="feed" class="panel active">
    <h1>📡 赚钱资讯流</h1>
    <div class="status-bar">已内联 <b id="feed-count">0</b> 条资讯（含趋势评分 + 风险标注 M7）。更新时间：{data.get('updated','未知')}</div>
    <div class="filters">
      <select id="region" onchange="renderFeed()">
        <option value="全部">全部地区</option>
        <option value="国内">国内</option>
        <option value="海外">海外</option>
      </select>
      <select id="cat" onchange="renderFeed()">
        <option value="全部">全部分类</option>
        <option value="平台接单">平台接单</option>
        <option value="本地服务">本地服务</option>
        <option value="AI副业">AI副业</option>
        <option value="电商/带货">电商/带货</option>
        <option value="内容创作">内容创作</option>
        <option value="被动收入">被动收入</option>
        <option value="创业">创业</option>
        <option value="副业">副业</option>
        <option value="思维">思维</option>
        <option value="行业动向">行业动向</option>
      </select>
      <input id="q" type="search" placeholder="搜索标题/摘要…" oninput="renderFeed()">
    </div>
    <div id="feed-grid"></div>
  </section>

  <section id="radar" class="panel">
    <h1>🔥 趋势雷达（自动评分）</h1>
    <div class="status-bar">规则打分 = 来源权重 + 新鲜度 + 高潜力词命中 + 信息差标。<b>零积分、无需 AI</b>。每天刷新，越靠上越值得盯。</div>
    <div id="radar-grid"></div>
  </section>

  <section id="digest" class="panel">
    <h1>🤖 {digest_title}</h1>
    <div class="status-bar">由 WorkBuddy 自动生成，已同步到 Obsidian 仓库。</div>
    <div class="markdown card" id="digest-md">
      {digest_html}
    </div>
  </section>

  <section id="projects" class="panel">
    <h1>📚 现成开源项目 / 工具库</h1>
    <div class="status-bar">下面这些项目/工具已经帮你整理好赚钱思路、资讯源或自动化能力，可直接白嫖（点击跳官网/GitHub）。</div>
    <div class="proj" id="proj-grid"></div>
  </section>

  <section id="gap" class="panel">
    <h1>🌐 中外信息差 · 套利案例库（M9）</h1>
    <div class="status-bar">看到「国内过时 = 海外潮流」的信息差，就是赚钱机会。每条都附 <b>💡思考/逻辑</b>：信息差在哪、为什么这产品、为什么赚钱、背后逻辑、普通人怎么复制。<b>点卡片展开看</b>。</div>
    <div id="gap-grid"></div>
  </section>

  <section id="review" class="panel">
    <h1>📊 我的赚钱复盘看板</h1>
    <div class="status-bar">本地保存（localStorage），<b>不联网、不上传</b>。建议每周花 5 分钟复盘：哪个信号真赚到钱，哪个是坑。可导出备份防丢失。</div>
    <div class="card review-form">
      <div class="row">
        <div><label>日期</label><input id="rv-date" type="date"></div>
        <div><label>信号 / 尝试项目</label><input id="rv-name" type="text" placeholder="如：AI本地商家代运营"></div>
      </div>
      <div class="row">
        <div><label>投入（元）</label><input id="rv-cost" type="number" min="0" placeholder="0"></div>
        <div><label>回报（元）</label><input id="rv-gain" type="number" min="0" placeholder="0"></div>
        <div><label>状态</label>
          <select id="rv-status">
            <option value="进行中">进行中</option>
            <option value="已赚到">已赚到</option>
            <option value="已放弃">已放弃</option>
          </select>
        </div>
      </div>
      <label>备注（做了什么、卡在哪）</label>
      <textarea id="rv-note" rows="2" placeholder="如：发了3条闲鱼，成交1单49元"></textarea>
      <div style="margin-top:10px"><button class="btn green" onclick="addReview()">+ 添加记录</button></div>
    </div>
    <div class="review-stats" id="rv-stats"></div>
    <div id="review-grid"></div>
    <div style="margin-top:10px">
      <button class="btn tiny" onclick="exportReview()">⬇ 导出备份</button>
      <button class="btn tiny" onclick="document.getElementById('rv-import').click()">⬆ 导入备份</button>
      <input id="rv-import" type="file" accept="application/json" style="display:none" onchange="importReview(event)">
    </div>
  </section>

  <section id="about" class="panel">
    <h1>ℹ️ 使用说明</h1>
    <div class="card">
      <div class="about-step"><div class="num">1</div><div><h4>这是一个纯 HTML 成品页面</h4><p>双击即可打开，无需服务器、无需安装、不依赖任何 .bat/.py 文件。所有内容都已内联在页面里。</p></div></div>
      <div class="about-step"><div class="num">2</div><div><h4>六个标签怎么用</h4><p><b>资讯流</b>：当天国内外赚钱/副业资讯，可按地区、分类筛选和搜索，每条带趋势分。<br><b>🔥 趋势雷达</b>：按评分排序的最该盯信号，自动标注信息差（海外已火/国内已验证）。<br><b>AI每日解读</b>：WorkBuddy 帮你消化成小白能懂的简报。<br><b>项目库</b>：现成开源项目、阅读器、知识库，点击跳 GitHub/官网。<br><b>🌐 中外信息差</b>：国内过时=海外潮流的套利案例，每条附💡思考/逻辑（信息差在哪、为什么赚钱、背后逻辑、怎么复制）。<br><b>📊 复盘看板</b>：你自己的赚钱试验记录与 ROI。<br><b>关于</b>：就是你正在看的。</p></div></div>
      <div class="about-step"><div class="num">3</div><div><h4>为什么 .bat 被 Windows 安全中心拦截？</h4><p>从网上/其他位置复制来的 .bat 文件会被 Windows 标记为“来自 Internet 的文件”。解决很简单：在资源管理器里右键 .bat → 属性 → 勾选“解除锁定” → 确定，之后就能双击运行了。</p></div></div>
      <div class="about-step"><div class="num">4</div><div><h4>如何更新数据</h4><p>本页面是“离线成品”。想每天自动更新，可让 WorkBuddy 每天生成新的成品页面；或者在本机解除 .bat 锁定后，双击 <code>立即采集.bat</code> + <code>start.bat</code> 查看动态面板。</p></div></div>
    </div>
      <div class="warning">
        <b>避坑提醒</b>：任何要求"先交押金/培训费/买课才能接单"的项目，直接拉黑。靠谱的副业一定是低成本先开干。
        <br><br><b>🛡️ 风险哨兵（M7 已上线）</b>：面板已自动给每条机会挂风险标签——<span style="color:#dc2626;font-weight:700">🚫红线·骗局</span>（先交钱/传销/博彩/灰产，直接拉黑）、<span style="color:#f59e0b;font-weight:700">⚠️警惕</span>（薅羊毛/刷单/夸大收益，封号或引流话术）、<span style="color:#6b7280;font-weight:700">📋留意</span>（医美/金融等高资质门槛）。带标签的，先别动手。
      </div>
  </section>

  <div class="footer">赚钱面板 · D:\\workbuddy\\赚钱面板\\ · 离线成品版（M1趋势雷达+M6复盘看板+M7风险哨兵+M9中外信息差） · 生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
</main>

<script>
const FEED_ITEMS={items_json};
const RADAR_ITEMS={radar_json};
const PROJECTS={projects_json};
const GAP_CASES={gap_json};
const DIGEST_HTML=`{digest_html.replace('`','\\`')}`;

function show(id){{
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  document.querySelectorAll('.nav button').forEach(b=>b.classList.remove('active'));
  event.target.classList.add('active');
}}

function esc(s){{return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}}

function gapTag(gap){{
  if(!gap) return '';
  return `<span class="gap-tag">${{gap}}</span>`;
}}

function riskTag(risk){{
  if(!risk || !risk.level) return '';
  const map={{high:['risk-high','🚫 红线·骗局'],warn:['risk-warn','⚠️ 警惕'],low:['risk-low','📋 留意']}};
  const m=map[risk.level]||map.low;
  return `<span class="risk-tag ${{m[0]}}" title="${{esc(risk.reason)}}">${{m[1]}}</span>`;
}}

function scoreBlock(it){{
  const pct=it.pct||0, sc=it.score||0;
  return `<div class="score-row"><span class="score-num">${{sc}}/30</span>
    <span class="score-bar"><span style="width:${{pct}}%"></span></span>
    ${{gapTag(it.gap)}}
    ${{riskTag(it.risk)}}</div>`;
}}

function renderFeed(){{
  const region=document.getElementById('region').value;
  const cat=document.getElementById('cat').value;
  const q=(document.getElementById('q').value||'').toLowerCase();
  const grid=document.getElementById('feed-grid');
  const items=FEED_ITEMS.filter(i=>{{
    if(region!=='全部'&&i.region!==region)return false;
    if(cat!=='全部'&&i.category!==cat)return false;
    if(q&&!(i.title+i.desc+i.source).toLowerCase().includes(q))return false;
    return true;
  }});
  document.getElementById('feed-count').textContent=items.length;
  grid.innerHTML=items.length?items.map(i=>`
    <div class="card">
      <div class="top">
        <span class="badge ${{i.region==='国内'?'cn':'os'}}">${{i.region}}</span>
        <span class="tag">${{i.category}}</span>
        <span class="tag">${{i.source}}</span>
      </div>
      <a class="title" href="${{i.link}}" target="_blank" rel="noopener">${{esc(i.title)}}</a>
      <div class="desc">${{esc(i.desc)}}</div>
      ${{scoreBlock(i)}}
      ${{ i.思考 ? `<details class="think"><summary>💡 思考/逻辑</summary><div class="body"><p>${{esc(i.思考)}}</p></div></details>`:'' }}
      <div class="meta">来源：${{i.source}} · <a href="${{i.link}}" target="_blank" rel="noopener">查看原文 →</a></div>
    </div>
  `).join(''):'<div class="empty">没有匹配的资讯，换个筛选条件试试。</div>';
}}

function renderRadar(){{
  const grid=document.getElementById('radar-grid');
  grid.innerHTML=RADAR_ITEMS.length?RADAR_ITEMS.map((i,idx)=>`
    <div class="card">
      <div class="radar-rank">
        <span class="rk">${{idx+1}}</span>
        <span class="badge ${{i.region==='国内'?'cn':'os'}}">${{i.region}}</span>
        <span class="tag">${{i.score||0}}/30</span>
        ${{gapTag(i.gap)}}
        ${{riskTag(i.risk)}}
      </div>
      <a class="title" href="${{i.link}}" target="_blank" rel="noopener">${{esc(i.title)}}</a>
      <div class="desc">${{esc(i.desc)}}</div>
      <div class="score-row"><span class="score-bar"><span style="width:${{i.pct||0}}%"></span></span></div>
    </div>
  `).join(''):'<div class="empty">暂无评分数据。</div>';
}}

function renderProjects(){{
  document.getElementById('proj-grid').innerHTML=PROJECTS.map(p=>`
    <div class="card">
      <h3>${{esc(p.name)}}</h3>
      <p>${{esc(p.desc)}}</p>
      <a class="btn" href="${{p.link}}" target="_blank" rel="noopener">去 GitHub / 官网</a>
    </div>
  `).join('');
}}

function renderGap(){{
  const grid=document.getElementById('gap-grid');
  grid.innerHTML=GAP_CASES.length?GAP_CASES.map(c=>`
    <div class="card gap-card">
      <div class="top">
        <span class="dir">${{esc(c.direction)}}</span>
        <span class="type">${{esc(c.type)}}</span>
        ${{riskTag(c.risk)}}
      </div>
      <a class="title" href="${{esc(c.link)}}" target="_blank" rel="noopener">${{esc(c.product)}}</a>
      <div class="desc">${{esc(c.phenomenon)}}</div>
      <details class="think">
        <summary>💡 思考 / 逻辑（点开看）</summary>
        <div class="body">
          <p><b>📌 信息差在哪：</b>${{esc(c.gap)}}</p>
          <p><b>🎯 为什么是这个产品：</b>${{esc(c.why_product)}}</p>
          <p><b>💰 为什么赚钱：</b>${{esc(c.why_money)}}</p>
          <p><b>🧠 背后逻辑：</b>${{esc(c.logic)}}</p>
          <p><b>🛠️ 普通人可复制：</b>${{esc(c.how_to)}}</p>
          <p><b>📊 事实支撑：</b>${{esc(c.evidence)}}</p>
        </div>
      </details>
      <div class="meta">来源：${{esc(c.source)}} · <a href="${{esc(c.link)}}" target="_blank" rel="noopener">查看原文 →</a></div>
    </div>
  `).join(''):'<div class="empty">暂无案例。</div>';
}}

/* ---------- M6 复盘看板（localStorage） ---------- */
const RK="mm_review_v1";
function loadReview(){{try{{return JSON.parse(localStorage.getItem(RK))||[]}}catch(e){{return[]}}}}
function saveReview(a){{localStorage.setItem(RK,JSON.stringify(a));}}
function todayStr(){{const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');}}
function statusBadge(s){{
  if(s==='已赚到')return '<span class="badge2 win">已赚到</span>';
  if(s==='已放弃')return '<span class="badge2 give">已放弃</span>';
  return '<span class="badge2 do">进行中</span>';
}}
function addReview(){{
  const name=document.getElementById('rv-name').value.trim();
  if(!name){{alert('请填写信号/尝试项目名');return;}}
  const rec={{
    id:Date.now(),
    date:document.getElementById('rv-date').value||todayStr(),
    name:name,
    cost:parseFloat(document.getElementById('rv-cost').value)||0,
    gain:parseFloat(document.getElementById('rv-gain').value)||0,
    status:document.getElementById('rv-status').value,
    note:document.getElementById('rv-note').value.trim()
  }};
  const a=loadReview();a.push(rec);saveReview(a);
  document.getElementById('rv-name').value='';document.getElementById('rv-cost').value='';
  document.getElementById('rv-gain').value='';document.getElementById('rv-note').value='';
  renderReview();
}}
function delReview(id){{
  const a=loadReview().filter(r=>r.id!==id);saveReview(a);renderReview();
}}
function renderReview(){{
  const a=loadReview();
  let tc=0,tg=0,win=0;
  a.forEach(r=>{{tc+=r.cost||0;tg+=r.gain||0;if(r.status==='已赚到')win++;}});
  const net=tg-tc;const roi=tc>0?((net/tc)*100):0;
  document.getElementById('rv-stats').innerHTML=`
    <div class="stat"><div class="v">${{a.length}}</div><div class="l">记录数</div></div>
    <div class="stat"><div class="v">¥${{tc.toFixed(0)}}</div><div class="l">总投入</div></div>
    <div class="stat"><div class="v">¥${{tg.toFixed(0)}}</div><div class="l">总回报</div></div>
    <div class="stat"><div class="v ${{net>=0?'pos':'neg'}}">¥${{net.toFixed(0)}}</div><div class="l">净收益</div></div>
    <div class="stat"><div class="v ${{roi>=0?'pos':'neg'}}">${{roi.toFixed(0)}}%</div><div class="l">ROI</div></div>
    <div class="stat"><div class="v">${{win}}</div><div class="l">已赚到</div></div>`;
  document.getElementById('review-grid').innerHTML=a.length?a.slice().reverse().map(r=>{{
    const net=r.gain-r.cost;const nc=net>=0?'pos':'neg';
    return `<div class="rv">
      <div class="main">
        <h4>${{statusBadge(r.status)}}${{esc(r.name)}}</h4>
        <div class="line">日期：${{r.date}} · 投入 <span class="money">¥${{r.cost}}</span> · 回报 <span class="money ${{r.gain>=r.cost?'pos':'neg'}}">¥${{r.gain}}</span> · 净 <span class="money ${{nc}}">¥${{net}}</span></div>
        ${{r.note?`<div class="line">备注：${{esc(r.note)}}</div>`:''}}
      </div>
      <button class="btn red tiny" onclick="delReview(${{r.id}})">删除</button>
    </div>`;
  }}).join(''):'<div class="empty">还没有记录。从今天起，每试一个信号就记一笔。</div>';
}}
function exportReview(){{
  const a=loadReview();if(!a.length){{alert('暂无记录可导出');return;}}
  const blob=new Blob([JSON.stringify(a,null,2)],{{type:'application/json'}});
  const url=URL.createObjectURL(blob);
  const x=document.createElement('a');x.href=url;x.download='赚钱复盘-'+todayStr()+'.json';x.click();
  URL.revokeObjectURL(url);
}}
function importReview(e){{
  const f=e.target.files[0];if(!f)return;
  const rd=new FileReader();
  rd.onload=function(){{
    try{{const a=JSON.parse(rd.result);if(Array.isArray(a)){{saveReview(a);renderReview();alert('导入成功：'+a.length+' 条');}}else{{alert('格式不对');}}
    }}catch(err){{alert('解析失败');}}
  }};
  rd.readAsText(f);
}}
document.getElementById('rv-date').value=todayStr();

renderFeed();
renderRadar();
renderProjects();
renderGap();
renderReview();
</script>
</body>
</html>'''

    out_path = os.path.join(ROOT, "赚钱面板-成品.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[build_product] 已生成：{out_path}")
    print(f"[build_product] 资讯条数：{len(data.get('items', []))}，雷达TOP：{len(radar_items)}，项目数：{len(projects)}，日报：{digest_title}")


if __name__ == "__main__":
    build()
