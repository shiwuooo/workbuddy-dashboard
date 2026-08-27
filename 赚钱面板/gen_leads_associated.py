# -*- coding: utf-8 -*-
"""
副业线索库 -> 关联版（结构化 + 互相关联）
从「副业线索库-作战版.html」取 212 条数据，自动增强 4 维标签与赛道聚类，
生成自包含离线 HTML：赛道地图 / 多维筛选 / 点标签即关联 / 详情相关推荐。
用法: python gen_leads_associated.py
"""
import os, re, json, html

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "副业线索库-作战版.html")
OUT = os.path.join(ROOT, "副业线索库-关联版.html")

# ---------- 维度词典 ----------
CHANNELS = {
    "抖音": ["抖音"], "快手": ["快手"], "视频号": ["视频号"], "小红书": ["小红书"],
    "知乎": ["知乎"], "B站": ["b站", "bilibili"], "公众号": ["公众号", "微信公", "订阅号"],
    "微博": ["微博"], "私域/微信": ["私域", "朋友圈", "微信社群", "社群", "企微"],
    "闲鱼": ["闲鱼"], "淘宝/天猫": ["淘宝", "天猫"], "拼多多": ["拼多多"], "京东": ["京东"],
    "TikTok": ["tiktok"], "YouTube": ["youtube"], "Instagram": ["instagram"],
    "Reddit": ["reddit"], "Pinterest": ["pinterest"], "Facebook": ["facebook"],
    "Twitter/X": ["twitter", "x.com"], "Etsy": ["etsy"], "eBay": ["ebay"],
    "Amazon": ["amazon"], "Shopify": ["shopify"], "Upwork": ["upwork"],
    "Fiverr": ["fiverr"], "Gumroad": ["gumroad"], "Substack": ["substack"],
    "美团/点评": ["美团", "大众点评"], "豆瓣": ["豆瓣"],
}
MONETIZE = {
    "佣金/CPS": ["佣金", "cps", "分成", "带货", "affiliate", "联盟"],
    "广告/流量主": ["广告", "流量主", "接广", "ad "],
    "私域成交": ["私域", "成交", "复购", "社群卖", "朋友圈卖"],
    "卖课/知识付费": ["卖课", "知识付费", "课程", "训练营", "培训", "网课"],
    "订阅/会员": ["订阅", "会员", "patreon", "onlyfans", "月费"],
    "接单/外包": ["接单", "外包", "freelance", "项目制", "众包接"],
    "服务/咨询": ["咨询", "陪跑", "顾问", "服务", "代运营"],
    "卖数字产品": ["数字产品", "电子书", "模板", "素材", "notion", "pdf", "资料", "课件"],
    "卖实物/差价": ["差价", "倒卖", "信息差", "铺货", "dropship", "代发", "一件代发", "零售", "转售"],
    "打赏/赞助": ["打赏", "赞助", "donate", "patron"],
    "平台任务奖励": ["做任务", "任务奖励", "返现", "问卷", "调研", "测试", "标注", "众包"],
}
SKILL = {
    "写作/文案": ["写作", "文案", "文章", "稿件", "编辑", "内容创作"],
    "视频剪辑": ["剪辑", "二剪", "后期", "视频制作", "短片"],
    "拍摄/出镜": ["拍摄", "出镜", "主播", "露脸", "口播", "直播"],
    "设计/美工": ["设计", "美工", "ps", "作图", "排版", "ui", "插画"],
    "编程/技术": ["编程", "代码", "开发", "爬虫", "python", "建站", "脚本", "技术"],
    "外语": ["英语", "外语", "翻译", "双语", "日文", "德语", "小语种"],
    "运营/投放": ["运营", "投放", "投流", "seo", "增长", "引流", "涨粉", "seo"],
    "选品/供应链": ["选品", "货源", "供应链", "采购", "1688", "义乌"],
    "AI工具": ["ai", "gpt", "生图", "生视频", "提示词", "chatgpt", "数字人", "ai工具"],
    "销售/谈判": ["销售", "谈判", "话术", "成交技巧"],
    "无技能/执行力": ["零基础", "零技能", "无技能", "纯执行", "体力", "搬运", "整理", "挂机", "自动", "简单操作"],
}
SUPPLY = {
    "1688/义乌": ["1688", "义乌", "货源", "供应链", "工厂"],
    "一件代发": ["代发", "dropship", "一件代发", "无货源"],
    "信息源/资料": ["信息源", "独家", "数据库", "内部资料"],
    "AI生成": ["ai生成", "生图", "生视频", "数字人", "自动生成"],
}

TRACKS = [
    ("内容流量变现", "#3b82f6",
     "靠持续输出内容吸粉，再把注意力变现（带货 / 广告 / 私域）。核心杠杆 = 内容生产能力 + 平台算法理解。"),
    ("电商与信息差套利", "#f59e0b",
     "靠供应链成本差或信息差赚差价（国内货→海外溢价、倒卖、Dropship）。核心杠杆 = 选品 + 渠道。"),
    ("技能外包接单", "#10b981",
     "把你的技能（设计 / 编程 / 翻译 / 咨询）在平台卖给需求方。核心杠杆 = 一技之长 + 报价能力。"),
    ("AI杠杆提效", "#8b5cf6",
     "用 AI 工具把上述任一模式降本增效（批量生成 / 自动运营 / 辅助交付）。核心杠杆 = 会用 AI。"),
    ("平台众包换钱", "#64748b",
     "在平台接任务 / 调研 / 测试，用时间换钱。门槛最低、天花板也低，适合练手起步。核心杠杆 = 执行力。"),
]

CATCOLOR = {"内容": "#3b82f6", "服务": "#10b981", "电商": "#f59e0b",
            "套利": "#ef4444", "信息差": "#8b5cf6"}


def extract(text, dic):
    text = text.lower()
    out = []
    for k, al in dic.items():
        if any(a.lower() in text for a in al):
            out.append(k)
    return out


def infer_track(l):
    cat = l["cat"]
    blob = (l["name"] + l["play"] + l["earn"]).lower()
    if "ai" in blob or "gpt" in blob or "生图" in l["play"] or "chatgpt" in blob or "数字人" in blob:
        return "AI杠杆提效"
    if any(k in blob for k in ["任务", "众包", "调研", "问卷", "测试", "标注", "做任务", "返现", "试玩", "众测", "mechanical"]):
        return "平台众包换钱"
    if cat == "内容":
        return "内容流量变现"
    if cat in ("电商", "套利", "信息差"):
        return "电商与信息差套利"
    if cat == "服务":
        return "技能外包接单"
    return "其他赛道"


def build_logic(l):
    parts = []
    if l["channels"]:
        parts.append("获客【" + l["channels"][0] + "】")
    if l["skill"]:
        parts.append("用【" + l["skill"][0] + "】能力")
    if l["monetize"]:
        parts.append("以【" + l["monetize"][0] + "】变现")
    return " → ".join(parts) if parts else "（信息不足，待补充）"


# ---------- 读取并增强 ----------
h = open(SRC, encoding="utf-8").read()
m = re.search(r"const LEADS\s*=\s*(\[.*?\]);", h, re.S)
leads = json.loads(m.group(1))
print("读取线索:", len(leads))

for l in leads:
    blob = l["name"] + " " + l["plat"] + " " + l["play"] + " " + l["earn"]
    l["channels"] = extract(blob, CHANNELS)
    l["monetize"] = extract(blob, MONETIZE)
    l["skill"] = extract(blob, SKILL)
    l["supply"] = extract(blob, SUPPLY)
    l["track"] = infer_track(l)
    l["logic"] = build_logic(l)

# 期数去重保序
issues = []
for l in leads:
    if l["issue"] and l["issue"] not in issues:
        issues.append(l["issue"])

# 赛道计数
track_counts = {}
for l in leads:
    track_counts[l["track"]] = track_counts.get(l["track"], 0) + 1

esc = lambda s: html.escape(str(s), quote=True)
DATA = json.dumps(leads, ensure_ascii=False).replace("</", "<\\/")
ISSUES = json.dumps(issues, ensure_ascii=False)
TRACKS_JSON = json.dumps([{"name": t[0], "color": t[1], "desc": t[2]} for t in TRACKS], ensure_ascii=False)
CATCOLOR_JSON = json.dumps(CATCOLOR, ensure_ascii=False)
TCOUNT = json.dumps(track_counts, ensure_ascii=False)

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>副业线索库 · 关联版</title>
<style>
:root{
  --bg:#f4f6fb; --card:#fff; --ink:#1f2933; --muted:#6b7280; --line:#e5e7eb;
  --accent:#2563eb; --accent2:#1e3a8a; --soft:#eef2ff;
  --cCh:#0ea5e9; --cMon:#f59e0b; --cSk:#10b981;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
  font-size:14px;line-height:1.6}
.topbar{position:sticky;top:0;z-index:30;background:rgba(255,255,255,.96);
  backdrop-filter:blur(8px);border-bottom:1px solid var(--line);
  display:flex;align-items:center;gap:10px;padding:10px 18px;flex-wrap:wrap}
.topbar .ttl{font-weight:800;font-size:17px;color:var(--accent2)}
.topbar .sub{font-size:12px;color:var(--muted)}
.search{flex:1;min-width:160px;display:flex;align-items:center;gap:6px}
.search input{width:100%;max-width:320px;padding:8px 12px;border:1px solid var(--line);
  border-radius:999px;font-size:14px;outline:none}
.search input:focus{border-color:var(--accent)}
.btn{border:1px solid var(--line);background:#fff;border-radius:8px;padding:7px 12px;
  font-size:13px;cursor:pointer;white-space:nowrap}
.btn.on{background:var(--accent);color:#fff;border-color:var(--accent)}
.btn.ghost{background:#fff}
.seg{display:flex;border:1px solid var(--line);border-radius:8px;overflow:hidden}
.seg button{border:0;background:#fff;padding:7px 14px;font-size:13px;cursor:pointer}
.seg button.on{background:var(--accent);color:#fff}
.wrap{display:flex;align-items:flex-start;max-width:1320px;margin:0 auto}
.side{position:sticky;top:56px;width:232px;flex:0 0 232px;align-self:flex-start;
  height:calc(100vh - 56px);overflow:auto;padding:14px 12px;border-right:1px solid var(--line);background:#fbfcfe}
.side h4{margin:13px 0 7px;font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}
.side h4:first-child{margin-top:0}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{border:1px solid var(--line);background:#fff;border-radius:999px;padding:4px 10px;
  font-size:12px;cursor:pointer;user-select:none}
.chip.on{background:var(--accent);color:#fff;border-color:var(--accent)}
.main{flex:1;padding:18px;min-width:0}
.stats{font-size:13px;color:var(--muted);margin-bottom:10px}
.assoc{background:var(--soft);border:1px solid #c7d2fe;border-radius:10px;padding:10px 14px;
  font-size:13px;color:var(--accent2);margin-bottom:12px;display:none}
.assoc.show{display:block}
.assoc b{color:var(--accent)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:15px;
  box-shadow:0 1px 2px rgba(0,0,0,.04);display:flex;flex-direction:column;gap:8px;cursor:pointer}
.card:hover{border-color:var(--accent)}
.card .hd{display:flex;align-items:flex-start;gap:8px;justify-content:space-between}
.card .nm{font-weight:700;font-size:15px;color:var(--ink)}
.card .no{font-size:12px;color:var(--muted);flex:0 0 auto}
.tagrow{display:flex;flex-wrap:wrap;gap:5px}
.tag{font-size:11px;padding:2px 8px;border-radius:999px;color:#fff;cursor:pointer}
.tag.d{opacity:.92}
.tag.d:hover{filter:brightness(.92);text-decoration:underline}
.lvl{font-size:11px;padding:2px 8px;border-radius:6px;font-weight:700;color:#fff}
.lvl.低{background:#10b981}.lvl.中{background:#f59e0b}.lvl.高{background:#ef4444}
.logic{font-size:12px;color:#475569;background:#f1f5f9;border-radius:8px;padding:7px 9px}
.logic b{color:#334155}
.kv{font-size:13px}.kv b{color:#374151}.kv .v{color:#4b5563}
.play{font-size:13px;color:#374151;background:#f8fafc;border-radius:8px;padding:8px 10px}
.actions{display:flex;gap:6px;flex-wrap:wrap;margin-top:2px}
.act{border:1px solid var(--line);background:#fff;border-radius:8px;padding:5px 9px;font-size:12px;cursor:pointer}
.act.on.want{background:#fef3c7;border-color:#f59e0b;color:#92400e}
.act.on.tried{background:#dbeafe;border-color:#3b82f6;color:#1e40af}
.act.on.fav{background:#fce7f3;border-color:#ec4899;color:#9d174d}
.note{border:1px dashed var(--line);border-radius:8px;padding:7px 9px;font-size:12px;
  width:100%;resize:vertical;min-height:36px;display:none;font-family:inherit}
.note.show{display:block}
.foot{text-align:center;color:var(--muted);font-size:12px;margin:24px 0}
.barmask{display:none}
/* 赛道地图 */
#trackmap{padding:18px;max-width:1320px;margin:0 auto}
.tmap-h{font-size:13px;color:var(--muted);margin-bottom:12px}
.tgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.tcard{border:1px solid var(--line);border-radius:14px;padding:16px;background:#fff;cursor:pointer;
  border-left:6px solid var(--accent)}
.tcard:hover{box-shadow:0 4px 14px rgba(0,0,0,.08)}
.tcard h3{margin:0 0 6px;font-size:16px}
.tcard .cnt{font-size:12px;color:var(--muted);margin-bottom:8px}
.tcard p{font-size:13px;color:#475569;margin:0}
/* 详情 modal */
.modal{position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:60;display:none;align-items:center;justify-content:center}
.modal.show{display:flex}
.modal .box{background:#fff;border-radius:14px;padding:20px;width:min(720px,93vw);max-height:86vh;overflow:auto}
.modal .box h2{margin:0 0 4px;font-size:19px}
.modal .close{float:right;cursor:pointer;font-size:20px;color:var(--muted)}
.rel{margin-top:16px;border-top:1px solid var(--line);padding-top:12px}
.rel h4{margin:0 0 8px;font-size:13px;color:var(--accent2)}
.rellist{display:flex;flex-direction:column;gap:6px}
.relitem{border:1px solid var(--line);border-radius:8px;padding:7px 10px;cursor:pointer;font-size:13px}
.relitem:hover{background:#f8fafc}
.relitem .rno{color:var(--muted);font-size:11px;margin-left:6px}
@media(max-width:860px){
  .wrap{flex-direction:column}
  .side{position:fixed;left:0;top:0;z-index:40;height:100%;width:260px;transform:translateX(-100%);
    transition:transform .2s;box-shadow:2px 0 12px rgba(0,0,0,.1)}
  .side.open{transform:translateX(0)}
  .barmask.show{display:block;position:fixed;inset:0;background:rgba(0,0,0,.25);z-index:35}
  .menubtn{display:inline-block!important}
}
.menubtn{display:none}
</style>
</head>
<body>
<div class="topbar">
  <button class="btn menubtn" onclick="document.getElementById('side').classList.toggle('open');document.getElementById('mask').classList.toggle('show')">☰ 筛选</button>
  <span class="ttl">副业线索库 · 关联版</span>
  <span class="sub" id="totalsub"></span>
  <div class="seg">
    <button id="vbtrack" onclick="setView('track')">🗺 赛道地图</button>
    <button id="vbbrowse" class="on" onclick="setView('browse')">🔗 关联浏览</button>
  </div>
  <div class="search"><input id="q" placeholder="搜项目 / 平台 / 玩法 / 渠道…" oninput="render()"></div>
  <button class="btn" id="minebtn" onclick="toggleMine()">我的清单 (0)</button>
  <button class="btn ghost" onclick="openExport()">导出</button>
  <button class="btn ghost" onclick="resetFilters()">重置</button>
</div>
<div class="barmask" id="mask" onclick="document.getElementById('side').classList.remove('open');this.classList.remove('show')"></div>

<div id="trackmap" style="display:none">
  <div class="tmap-h">副业不是 212 条孤立机会，而是 5 根杠杆的组合。先选一个赛道看清「打法逻辑」，再下钻到具体机会 →</div>
  <div class="tgrid" id="tgrid"></div>
</div>

<div class="wrap" id="browse">
  <aside class="side" id="side">
    <h4>赛道（赚钱逻辑）</h4>
    <div class="chips" id="f-track"></div>
    <h4>获客渠道（点标签可关联）</h4>
    <div class="chips" id="f-ch"></div>
    <h4>变现方式</h4>
    <div class="chips" id="f-mon"></div>
    <h4>所需技能</h4>
    <div class="chips" id="f-sk"></div>
    <h4>门槛</h4>
    <div class="chips" id="f-lvl"></div>
    <h4>适合人群</h4>
    <div class="chips" id="f-nov"></div>
    <h4>地区</h4>
    <div class="chips" id="f-reg"></div>
    <h4>期数</h4>
    <div class="chips" id="f-iss"></div>
    <h4>排序</h4>
    <div class="chips" id="f-sort"></div>
  </aside>
  <main class="main">
    <div class="assoc" id="assoc"></div>
    <div class="stats" id="stats"></div>
    <div class="grid" id="grid"></div>
    <div class="foot">副业线索库 · 关联版 · 离线可用 · 标记与备注存在本机浏览器(localStorage) · 换设备需手动导出</div>
  </main>
</div>

<div class="modal" id="modal"><div class="box">
  <span class="close" onclick="closeModal()">×</span>
  <div id="modalbody"></div>
</div></div>

<script>
const LEADS={data};
const ISSUES={issues};
const TRACKS={tracks};
const TCOUNT={tcount};
const CATCOLOR={catcolor};
const LS_KEY="fx_leads_assoc_v1";
let state=JSON.parse(localStorage.getItem(LS_KEY)||"{}");
const F={track:new Set(),ch:new Set(),mon:new Set(),sk:new Set(),lvl:new Set(),nov:new Set(),reg:new Set(),iss:new Set()};
let mineOnly=false, sortKey="num", assoc=null;

function save(){localStorage.setItem(LS_KEY,JSON.stringify(state));}
function esc(s){return String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));}

const COLOR={track:{},ch:"#0ea5e9",mon:"#f59e0b",sk:"#10b981"};
TRACKS.forEach(t=>COLOR.track[t.name]=t.color);

function uniq(arr){return [...new Set(arr)];}
function fill(id,arr,set,fmt){
  const box=document.getElementById(id);
  arr.forEach(a=>{const e=document.createElement("span");e.className="chip";e.textContent=fmt?fmt(a):a;
    e.onclick=()=>{if(set.has(a)){set.delete(a);e.classList.remove("on");}else{set.add(a);e.classList.add("on");}render();};
    box.appendChild(e);});
}
function buildChips(){
  const tracks=TRACKS.map(t=>t.name);
  const chs=uniq(LEADS.flatMap(l=>l.channels));
  const mons=uniq(LEADS.flatMap(l=>l.monetize));
  const sks=uniq(LEADS.flatMap(l=>l.skill));
  const lvls=["低","中","高"];
  const novs=["纯小白友好"];
  const regs=["国内","海外"];
  const sorts=[["num","默认(编号)"],["lvl","门槛↑"],["lvlD","门槛↓"]];
  fill("f-track",tracks,F.track);
  fill("f-ch",chs,F.ch);
  fill("f-mon",mons,F.mon);
  fill("f-sk",sks,F.sk);
  fill("f-lvl",lvls,F.lvl);
  fill("f-nov",novs,F.nov);
  fill("f-reg",regs,F.reg);
  fill("f-iss",ISSUES,F.iss,true);
  const sc=document.getElementById("f-sort");
  sorts.forEach(([k,t])=>{const e=document.createElement("span");e.className="chip";e.textContent=t;
    e.onclick=()=>{sortKey=k;sc.querySelectorAll(".chip").forEach(x=>x.classList.remove("on"));e.classList.add("on");render();};
    if(k==="num")e.classList.add("on");sc.appendChild(e);});
}

function match(l){
  if(F.track.size&&!F.track.has(l.track))return false;
  if(F.ch.size&&![...F.ch].some(c=>l.channels.includes(c)))return false;
  if(F.mon.size&&![...F.mon].some(c=>l.monetize.includes(c)))return false;
  if(F.sk.size&&![...F.sk].some(c=>l.skill.includes(c)))return false;
  if(F.lvl.size&&!F.lvl.has(l.lvl))return false;
  if(F.nov.size&&!l.novice)return false;
  if(F.reg.size&&!F.reg.has(l.region))return false;
  if(F.iss.size&&!F.iss.has(l.issue))return false;
  if(mineOnly){const s=state[l.num];if(!s||!s.s||!s.s.length)return false;}
  const q=document.getElementById("q").value.trim().toLowerCase();
  if(q){const hay=(l.name+l.plat+l.play+l.earn+l.track+(l.channels.join(""))+(l.monetize.join(""))+(l.skill.join(""))).toLowerCase();
    if(!hay.includes(q))return false;}
  return true;
}

function tagChip(text,color,dim){
  const cls=dim?"tag d":"tag";
  const attr=dim?(' data-dim="'+dim+'"'):'';
  return '<span class="'+cls+'" style="background:'+color+'"'+attr+'>'+esc(text)+'</span>';
}

function card(l){
  const s=state[l.num]||{s:[],n:""};
  const on=(k)=>s.s&&s.s.includes(k)?" on":"";
  let tags='';
  tags+=tagChip(l.track,COLOR.track[l.track]||"#64748b","");
  l.channels.slice(0,3).forEach(c=>tags+=tagChip(c,COLOR.ch,"ch"));
  l.monetize.slice(0,2).forEach(c=>tags+=tagChip(c,COLOR.mon,"mon"));
  l.skill.slice(0,2).forEach(c=>tags+=tagChip(c,COLOR.sk,"sk"));
  tags+='<span class="lvl '+l.lvl+'">门槛'+l.lvl+'</span>';
  if(l.novice)tags+='<span class="tag" style="background:#0ea5e9">纯小白友好</span>';
  if(l.region==='海外')tags+='<span class="tag" style="background:#7c3aed">海外</span>';
  return `<div class="card" onclick="openDetail('${l.num}')">
    <div class="hd"><div class="nm">${esc(l.name)}</div><div class="no">#${esc(l.num)}</div></div>
    <div class="tagrow">${tags}</div>
    <div class="logic"><b>赚钱逻辑：</b>${esc(l.logic)}</div>
    <div class="play">${esc(l.play)}</div>
    <div class="kv"><b>变现：</b><span class="v">${esc(l.earn)}</span></div>
    <div class="actions" onclick="event.stopPropagation()">
      <span class="act want${on('want')}" onclick="toggle('${l.num}','want',this)">★ 想做</span>
      <span class="act tried${on('tried')}" onclick="toggle('${l.num}','tried',this)">✓ 试过</span>
      <span class="act fav${on('fav')}" onclick="toggle('${l.num}','fav',this)">🔖 收藏</span>
      <span class="act" onclick="toggleNote('${l.num}',this)">✎ 备注</span>
    </div>
    <textarea class="note${s.n?' show':''}" id="n-${l.num}" oninput="saveNote('${l.num}',this.value)">${esc(s.n||'')}</textarea>
  </div>`;
}

function assocBanner(n){
  const box=document.getElementById("assoc");
  if(!assoc){box.classList.remove("show");box.innerHTML="";return;}
  const dimName={ch:"获客渠道",mon:"变现方式",sk:"所需技能"}[assoc.dim];
  box.classList.add("show");
  box.innerHTML='🔗 <b>关联筛选：</b>'+dimName+' = <b>'+esc(assoc.val)+'</b>（共 '+n+' 条）'
    +' —— 这些机会都共用这一杠杆，<b>打通一套打法即可复制</b>。'
    +' <span style="cursor:pointer;text-decoration:underline" onclick="clearAssoc()">清除 ✕</span>';
}

function render(){
  let list=LEADS.filter(match);
  if(sortKey==="lvl")list.sort((a,b)=>(a.lvl==="低"?0:a.lvl==="中"?1:2)-(b.lvl==="低"?0:b.lvl==="中"?1:2));
  if(sortKey==="lvlD")list.sort((a,b)=>(a.lvl==="高"?0:a.lvl==="中"?1:2)-(b.lvl==="高"?0:b.lvl==="中"?1:2));
  document.getElementById("grid").innerHTML=list.map(card).join("");
  document.getElementById("stats").textContent="共 "+LEADS.length+" 条 · 当前显示 "+list.length+" 条"+(mineOnly?"（仅我的清单）":"");
  const cnt=Object.values(state).filter(s=>s&&s.s&&s.s.length).length;
  document.getElementById("minebtn").textContent="我的清单 ("+cnt+")";
  assocBanner(assoc?list.length:0);
}

// 点标签 -> 关联筛选
document.addEventListener("click",e=>{
  const t=e.target.closest(".tag.d");
  if(!t)return;
  const dim=t.getAttribute("data-dim");
  const val=t.textContent;
  if(!dim)return;
  const setKey={ch:"ch",mon:"mon",sk:"sk"}[dim];
  F[setKey].clear();F[setKey].add(val);
  // 同步 sidebar 高亮
  ["f-ch","f-mon","f-sk"].forEach(id=>{
    document.getElementById(id).querySelectorAll(".chip").forEach(c=>{
      c.classList.toggle("on", c.textContent===val && ((id==="f-ch"&&dim==="ch")||(id==="f-mon"&&dim==="mon")||(id==="f-sk"&&dim==="sk")));
    });
  });
  assoc={dim,val};
  setView("browse");
  render();
});
function clearAssoc(){assoc=null;F.ch.clear();F.mon.clear();F.sk.clear();
  ["f-ch","f-mon","f-sk"].forEach(id=>document.getElementById(id).querySelectorAll(".chip").forEach(c=>c.classList.remove("on")));
  render();}

function toggle(num,k,el){const s=state[num]||{s:[],n:""};if(!s.s)s.s=[];
  const i=s.s.indexOf(k);if(i>=0)s.s.splice(i,1);else s.s.push(k);
  state[num]=s;save();render();}
function toggleNote(num,el){const ta=document.getElementById("n-"+num);ta.classList.toggle("show");if(ta.classList.contains("show"))ta.focus();}
function saveNote(num,v){const s=state[num]||{s:[],n:""};s.n=v;state[num]=s;save();}

// ---------- 详情 + 关联推荐 ----------
function related(l){
  const ch=[],mon=[],sk=[];
  LEADS.forEach(o=>{if(o.num===l.num)return;
    if(l.channels.some(c=>o.channels.includes(c)))ch.push(o);
    if(l.monetize.some(c=>o.monetize.includes(c)))mon.push(o);
    if(l.skill.some(c=>o.skill.includes(c)))sk.push(o);
  });
  const dedup=a=>{const seen=new Set();return a.filter(o=>{if(seen.has(o.num))return false;seen.add(o.num);return true;}).slice(0,6);};
  return {ch:dedup(ch),mon:dedup(mon),sk:dedup(sk)};
}
function relHTML(title,list,l){
  if(!list.length)return "";
  const items=list.map(o=>'<div class="relitem" onclick="openDetail(\''+o.num+'\')">'+esc(o.name)
    +'<span class="rno">#'+esc(o.num)+' · '+esc(o.track)+'</span></div>').join("");
  return '<h4>'+title+'</h4><div class="rellist">'+items+'</div>';
}
function openDetail(num){
  const l=LEADS.find(x=>x.num===num);if(!l)return;
  const s=state[num]||{s:[],n:""};
  const on=k=>s.s&&s.s.includes(k)?" on":"";
  const r=related(l);
  let tags='';
  l.channels.forEach(c=>tags+=tagChip(c,COLOR.ch,"ch"));
  l.monetize.forEach(c=>tags+=tagChip(c,COLOR.mon,"mon"));
  l.skill.forEach(c=>tags+=tagChip(c,COLOR.sk,"sk"));
  const body=document.getElementById("modalbody");
  body.innerHTML=`<h2>${esc(l.name)} <span style="font-size:13px;color:var(--muted)">#${esc(l.num)}</span></h2>
    <div class="tagrow" style="margin:8px 0">${tagChip(l.track,COLOR.track[l.track]||"#64748b","")}
      <span class="lvl ${l.lvl}">门槛${l.lvl}</span>${l.novice?'<span class="tag" style="background:#0ea5e9">纯小白友好</span>':''}${l.region==='海外'?'<span class="tag" style="background:#7c3aed">海外</span>':''}</div>
    <div class="logic" style="margin:8px 0"><b>赚钱逻辑：</b>${esc(l.logic)}</div>
    <div class="kv"><b>赛道：</b><span class="v">${esc(l.track)}</span></div>
    <div class="kv"><b>平台：</b><span class="v">${esc(l.plat)}</span></div>
    <div class="kv"><b>玩法：</b><span class="v">${esc(l.play)}</span></div>
    <div class="kv"><b>变现：</b><span class="v">${esc(l.earn)}</span></div>
    <div class="kv"><b>门槛：</b><span class="v">${esc(l.barrier)}</span></div>
    <div class="kv"><b>标签：</b><span class="v">${esc(l.cat)} ${esc(l.tags.join(" / "))}</span></div>
    <div class="kv"><b>期数：</b><span class="v">${esc(l.issue)}</span></div>
    <div class="actions" style="margin-top:10px">
      <span class="act want${on('want')}" onclick="toggle('${l.num}','want',this);openDetail('${l.num}')">★ 想做</span>
      <span class="act tried${on('tried')}" onclick="toggle('${l.num}','tried',this);openDetail('${l.num}')">✓ 试过</span>
      <span class="act fav${on('fav')}" onclick="toggle('${l.num}','fav',this);openDetail('${l.num}')">🔖 收藏</span>
    </div>
    <div class="rel">
      <h4 style="margin-bottom:8px">🔗 互相关联的其它机会（共用同一条杠杆）</h4>
      ${relHTML("📡 同样用【"+esc((l.channels[0]||"某渠道"))+"】获客",r.ch,l)}
      ${relHTML("💰 同样靠【"+esc((l.monetize[0]||"某方式"))+"】变现",r.mon,l)}
      ${relHTML("🛠 同样需要【"+esc((l.skill[0]||"某技能"))+"】",r.sk,l)}
    </div>`;
  document.getElementById("modal").classList.add("show");
}
function closeModal(){document.getElementById("modal").classList.remove("show");}

function setView(v){
  const track=document.getElementById("trackmap");
  const browse=document.getElementById("browse");
  if(v==="track"){track.style.display="block";browse.style.display="none";
    document.getElementById("vbtrack").classList.add("on");document.getElementById("vbbrowse").classList.remove("on");renderTracks();}
  else{track.style.display="none";browse.style.display="flex";
    document.getElementById("vbbrowse").classList.add("on");document.getElementById("vbtrack").classList.remove("on");render();}
}
function renderTracks(){
  const g=document.getElementById("tgrid");
  g.innerHTML=TRACKS.map(t=>{
    const cnt=TCOUNT[t.name]||0;
    return `<div class="tcard" style="border-left-color:${t.color}" onclick="pickTrack('${esc(t.name)}')">
      <h3 style="color:${t.color}">${esc(t.name)}</h3>
      <div class="cnt">${cnt} 个机会</div>
      <p>${esc(t.desc)}</p>
    </div>`;
  }).join("");
}
function pickTrack(name){
  F.track.clear();F.track.add(name);
  document.getElementById("f-track").querySelectorAll(".chip").forEach(c=>c.classList.toggle("on",c.textContent===name));
  clearAssoc();assoc=null;
  setView("browse");render();
}

function toggleMine(){mineOnly=!mineOnly;document.getElementById("minebtn").classList.toggle("on",mineOnly);render();}
function resetFilters(){Object.values(F).forEach(s=>s.clear());
  document.querySelectorAll(".side .chip.on").forEach(e=>e.classList.remove("on"));
  document.getElementById("q").value="";mineOnly=false;document.getElementById("minebtn").classList.remove("on");
  assoc=null;render();}

function openExport(){
  const lines=["# 我的副业清单（"+new Date().toISOString().slice(0,10)+"）",""];
  Object.keys(state).forEach(num=>{const s=state[num];if(!s||!s.s||!s.s.length)return;
    const l=LEADS.find(x=>x.num===num);if(!l)return;
    lines.push("## "+l.name+" (#"+num+") ["+s.s.join("/")+"]");
    lines.push("- 赛道："+l.track+" · 门槛："+l.lvl+(l.novice?" · 纯小白友好":"")+" · "+l.region);
    lines.push("- 获客："+(l.channels.join("/")||"—")+" · 变现："+(l.monetize.join("/")||"—")+" · 技能："+(l.skill.join("/")||"—"));
    lines.push("- 玩法："+l.play);
    lines.push("- 变现："+l.earn);
    if(s.n)lines.push("- 备注："+s.n);
    lines.push("");});
  document.getElementById("modalbody").innerHTML='<h3 style="margin-top:0">我的清单导出</h3>'
    +'<textarea id="expout" readonly style="width:100%;height:320px;border:1px solid var(--line);border-radius:10px;padding:10px;font-family:monospace;font-size:12px">'+esc(lines.join("\n"))+'</textarea>'
    +'<div style="margin-top:10px;display:flex;gap:8px;justify-content:flex-end"><button class="btn" onclick="copyExp()">复制</button>'
    +'<button class="btn" onclick="downloadExp()">下载 .md</button><button class="btn ghost" onclick="closeModal()">关闭</button></div>';
  document.getElementById("modal").classList.add("show");
}
function copyExp(){const t=document.getElementById("expout");if(t){t.select();document.execCommand("copy");}}
function downloadExp(){const t=document.getElementById("expout");if(!t)return;
  const b=new Blob([t.value],{type:"text/markdown"});const u=URL.createObjectURL(b);
  const a=document.createElement("a");a.href=u;a.download="我的副业清单.md";a.click();URL.revokeObjectURL(u);}

buildChips();
document.getElementById("totalsub").textContent="共 "+LEADS.length+" 条 · 5 大赛道";
setView("browse");
</script>
</body>
</html>
"""

out = (TEMPLATE.replace("{data}", DATA).replace("{issues}", ISSUES)
       .replace("{tracks}", TRACKS_JSON).replace("{tcount}", TCOUNT)
       .replace("{catcolor}", CATCOLOR_JSON))
open(OUT, "w", encoding="utf-8").write(out)
print("已生成:", OUT, "大小", os.path.getsize(OUT), "bytes")
print("赛道分布:", track_counts)
