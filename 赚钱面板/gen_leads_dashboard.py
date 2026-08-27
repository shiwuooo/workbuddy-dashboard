# -*- coding: utf-8 -*-
"""
副业线索库 -> 作战版（可筛选 / 可标记 / 可写备注）
解析旧 side_hustle_leads_report.html 的表格，生成自包含离线 HTML。
用法: python gen_leads_dashboard.py
"""
import os, re, html, json
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = r"D:\workbuddy\2026-07-30-10-56-34\reports\side_hustle_leads_report.html"
OUT = os.path.join(ROOT, "副业线索库-作战版.html")

OVERSEAS = ["海外","TikTok","YouTube","Reddit","Upwork","Etsy","Fiverr","Gumroad",
            "Rover","Airbnb","Vrbo","Shopify","Pinterest","KDP","Substack","Mercor",
            "Discord","Whop","LemonSqueezy","Acquire","Betfair","Smarkets","MetaMask",
            "Phantom","Prolific","Respondent","UserTesting","eBay","雅虎","Amazon",
            "Outlier","LinkedIn","Flippa","GoHighLevel","Voiceflow","MicroAcquire",
            "Beehiiv","Circle","Matched","Aerostack","Printify","Printful","KDP"]

CAT_COLOR = {"内容":"#3b82f6","服务":"#10b981","电商":"#f59e0b","套利":"#ef4444","信息差":"#8b5cf6"}

class Extractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.leads = []
        self.issue = ""
        self.cat = ""
        self.in_td = False
        self.cur = None
        self.tds = []
        self.depth = 0
    def handle_starttag(self, tag, attrs):
        if tag == "h2":
            self._cap = []
            self._in_h = "h2"
        elif tag == "h3":
            self._cap = []
            self._in_h = "h3"
        elif tag == "tr":
            self.tds = []
            self.cur = []
        elif tag == "td":
            self._buf = []
            self.in_td = True
    def handle_endtag(self, tag):
        if tag == "h2":
            self.issue = "".join(self._cap).strip()
            self._in_h = None
        elif tag == "h3":
            t = "".join(self._cap).strip()
            m = re.match(r"([\u4e00-\u9fa5]+)类", t)
            self.cat = m.group(1) if m else t
            self._in_h = None
        elif tag == "td":
            self.cur.append("".join(self._buf).strip())
            self.in_td = False
        elif tag == "tr":
            if self.cur and len(self.cur) >= 7:
                self._emit(self.cur)
            self.cur = None
    def handle_data(self, data):
        if getattr(self, "_in_h", None):
            self._cap.append(data)
        if self.in_td:
            self._buf.append(data)
    def _emit(self, cells):
        num = cells[0].strip()
        if not re.match(r"^\d+$", num):
            return
        name = cells[1].strip()
        plat = cells[2].strip()
        play = cells[3].strip()
        earn = cells[4].strip()
        barrier = cells[5].strip()
        tag = cells[6].strip()
        # 去重（同项目跨类重复只留首条）
        if any(l["name"] == name for l in self.leads):
            return
        # 门槛等级
        if "高" in barrier:
            lvl = "高"
        elif "中" in barrier:
            lvl = "中"
        else:
            lvl = "低"
        # 适合小白
        novice = (lvl == "低") or any(k in (barrier+play) for k in
                  ["零成本","零门槛","零投入","零库存","零粉","当周","零基础","零技能","零囤货"])
        # 海内外
        region = "海外" if any(m.lower() in plat.lower() for m in OVERSEAS) else "国内"
        # 标签拆分
        tags = [t.strip("·⚠️（）合规 ") for t in re.split(r"[·/]", tag) if t.strip("·⚠️（）合规 ")]
        tags = [t for t in tags if t]
        self.leads.append({
            "num": num, "name": name, "plat": plat, "play": play,
            "earn": earn, "barrier": barrier, "lvl": lvl, "novice": novice,
            "region": region, "tags": tags, "cat": self.cat, "issue": self.issue,
        })

src = open(SRC, encoding="utf-8").read()
ex = Extractor()
ex.feed(src)
leads = ex.leads
print("解析到线索:", len(leads))

# 期数去重保序
issues = []
for l in leads:
    if l["issue"] and l["issue"] not in issues:
        issues.append(l["issue"])

def esc(s):
    return html.escape(str(s), quote=True)

DATA = json.dumps(leads, ensure_ascii=False)
ISSUES = json.dumps(issues, ensure_ascii=False)
CATCOLOR = json.dumps(CAT_COLOR, ensure_ascii=False)

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>副业线索库 · 作战版</title>
<style>
:root{
  --bg:#f4f6fb; --card:#fff; --ink:#1f2933; --muted:#6b7280; --line:#e5e7eb;
  --accent:#2563eb; --accent2:#1e3a8a; --soft:#eef2ff;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
  font-size:14px;line-height:1.6}
.topbar{position:sticky;top:0;z-index:30;background:rgba(255,255,255,.95);
  backdrop-filter:blur(8px);border-bottom:1px solid var(--line);
  display:flex;align-items:center;gap:12px;padding:10px 18px;flex-wrap:wrap}
.topbar .ttl{font-weight:800;font-size:17px;color:var(--accent2)}
.topbar .sub{font-size:12px;color:var(--muted)}
.search{flex:1;min-width:180px;display:flex;align-items:center;gap:6px}
.search input{width:100%;max-width:360px;padding:8px 12px;border:1px solid var(--line);
  border-radius:999px;font-size:14px;outline:none}
.search input:focus{border-color:var(--accent)}
.btn{border:1px solid var(--line);background:#fff;border-radius:8px;padding:7px 12px;
  font-size:13px;cursor:pointer;white-space:nowrap}
.btn.on{background:var(--accent);color:#fff;border-color:var(--accent)}
.btn.ghost{background:#fff}
.wrap{display:flex;align-items:flex-start;max-width:1280px;margin:0 auto}
.side{position:sticky;top:56px;width:236px;flex:0 0 236px;align-self:flex-start;
  height:calc(100vh - 56px);overflow:auto;padding:16px 14px;border-right:1px solid var(--line);background:#fbfcfe}
.side h4{margin:14px 0 8px;font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}
.side h4:first-child{margin-top:0}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{border:1px solid var(--line);background:#fff;border-radius:999px;padding:4px 10px;
  font-size:12px;cursor:pointer;user-select:none}
.chip.on{background:var(--accent);color:#fff;border-color:var(--accent)}
.main{flex:1;padding:18px;min-width:0}
.stats{font-size:13px;color:var(--muted);margin-bottom:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px;
  box-shadow:0 1px 2px rgba(0,0,0,.04);display:flex;flex-direction:column;gap:8px}
.card .hd{display:flex;align-items:flex-start;gap:8px;justify-content:space-between}
.card .nm{font-weight:700;font-size:15px;color:var(--ink)}
.card .no{font-size:12px;color:var(--muted);flex:0 0 auto}
.tagrow{display:flex;flex-wrap:wrap;gap:5px}
.tag{font-size:11px;padding:2px 8px;border-radius:999px;color:#fff}
.lvl{font-size:11px;padding:2px 8px;border-radius:6px;font-weight:700;color:#fff}
.lvl.低{background:#10b981}.lvl.中{background:#f59e0b}.lvl.高{background:#ef4444}
.kv{font-size:13px}
.kv b{color:#374151}
.kv .v{color:#4b5563}
.play{font-size:13px;color:#374151;background:#f8fafc;border-radius:8px;padding:8px 10px}
.actions{display:flex;gap:6px;flex-wrap:wrap;margin-top:4px}
.act{border:1px solid var(--line);background:#fff;border-radius:8px;padding:5px 9px;
  font-size:12px;cursor:pointer}
.act.on.want{background:#fef3c7;border-color:#f59e0b;color:#92400e}
.act.on.tried{background:#dbeafe;border-color:#3b82f6;color:#1e40af}
.act.on.fav{background:#fce7f3;border-color:#ec4899;color:#9d174d}
.note{border:1px dashed var(--line);border-radius:8px;padding:7px 9px;font-size:12px;
  width:100%;resize:vertical;min-height:38px;display:none;font-family:inherit}
.note.show{display:block}
.foot{text-align:center;color:var(--muted);font-size:12px;margin:24px 0}
.barmask{display:none}
@media(max-width:820px){
  .wrap{flex-direction:column}
  .side{position:fixed;left:0;top:0;z-index:40;height:100%;width:260px;transform:translateX(-100%);
    transition:transform .2s;box-shadow:2px 0 12px rgba(0,0,0,.1)}
  .side.open{transform:translateX(0)}
  .barmask.show{display:block;position:fixed;inset:0;background:rgba(0,0,0,.25);z-index:35}
  .menubtn{display:inline-block!important}
}
.menubtn{display:none}
.modal{position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:60;display:none;align-items:center;justify-content:center}
.modal.show{display:flex}
.modal .box{background:#fff;border-radius:14px;padding:20px;width:min(680px,92vw);max-height:84vh;overflow:auto}
.modal textarea{width:100%;height:300px;border:1px solid var(--line);border-radius:10px;padding:10px;font-family:monospace;font-size:12px}
</style>
</head>
<body>
<div class="topbar">
  <button class="btn menubtn" onclick="document.getElementById('side').classList.toggle('open');document.getElementById('mask').classList.toggle('show')">☰ 筛选</button>
  <span class="ttl">副业线索库 · 作战版</span>
  <span class="sub" id="totalsub"></span>
  <div class="search"><input id="q" placeholder="搜项目名 / 平台 / 玩法…" oninput="render()"></div>
  <button class="btn" id="minebtn" onclick="toggleMine()">我的清单 (0)</button>
  <button class="btn ghost" onclick="openExport()">导出</button>
  <button class="btn ghost" onclick="resetFilters()">重置</button>
</div>
<div class="barmask" id="mask" onclick="document.getElementById('side').classList.remove('open');this.classList.remove('show')"></div>
<div class="wrap">
  <aside class="side" id="side">
    <h4>类型（可多选）</h4>
    <div class="chips" id="f-cat"></div>
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
    <div class="stats" id="stats"></div>
    <div class="grid" id="grid"></div>
    <div class="foot">副业线索库 · 作战版 · 离线可用 · 标记与备注存在本机浏览器(localStorage)，换设备不丢需手动导出</div>
  </main>
</div>
<div class="modal" id="modal"><div class="box">
  <h3 style="margin-top:0">我的清单导出</h3>
  <textarea id="expout" readonly></textarea>
  <div style="margin-top:10px;display:flex;gap:8px;justify-content:flex-end">
    <button class="btn" onclick="copyExp()">复制</button>
    <button class="btn" onclick="downloadExp()">下载 .md</button>
    <button class="btn ghost" onclick="closeExport()">关闭</button>
  </div>
</div></div>
<script>
const LEADS={data};
const ISSUES={issues};
const CATCOLOR={catcolor};
const LS_KEY="fx_leads_state_v1";
let state=JSON.parse(localStorage.getItem(LS_KEY)||"{}");
const F={cat:new Set(),lvl:new Set(),nov:new Set(),reg:new Set(),iss:new Set()};
let mineOnly=false, sortKey="num";

function save(){localStorage.setItem(LS_KEY,JSON.stringify(state));}

// 构建筛选 chips
function buildChips(){
  const cats=[...new Set(LEADS.map(l=>l.cat))];
  const lvls=["低","中","高"];
  const novs=["纯小白友好"];
  const regs=["国内","海外"];
  const sorts=[["num","默认(编号)"],["lvl","门槛↑"],["lvlD","门槛↓"]];
  fill("f-cat",cats,c=>c,F.cat);
  fill("f-lvl",lvls,c=>c,F.lvl);
  fill("f-nov",novs,c=>c,F.nov);
  fill("f-reg",regs,c=>c,F.reg);
  fill("f-iss",ISSUES.map((s,i)=>s),c=>c,F.iss,true);
  const sc=document.getElementById("f-sort");
  sorts.forEach(([k,t])=>{const e=document.createElement("span");e.className="chip";e.textContent=t;
    e.onclick=()=>{sortKey=k;sc.querySelectorAll(".chip").forEach(x=>x.classList.remove("on"));e.classList.add("on");render();};
    if(k==="num")e.classList.add("on");sc.appendChild(e);});
}
function fill(id,arr,key,set,long){
  const box=document.getElementById(id);
  arr.forEach(a=>{const e=document.createElement("span");e.className="chip";e.textContent=long?a.slice(0,12):a;
    e.title=long?a:"";e.onclick=()=>{if(set.has(a)){set.delete(a);e.classList.remove("on");}else{set.add(a);e.classList.add("on");}render();};
    box.appendChild(e);});
}

function lvlOf(l){return l.lvl;}
function match(l){
  if(F.cat.size&&!F.cat.has(l.cat))return false;
  if(F.lvl.size&&!F.lvl.has(l.lvl))return false;
  if(F.nov.size&&!l.novice)return false;
  if(F.reg.size&&!F.reg.has(l.region))return false;
  if(F.iss.size&&!F.iss.has(l.issue))return false;
  if(mineOnly){const s=state[l.num];if(!s||!s.s||!s.s.length)return false;}
  const q=document.getElementById("q").value.trim().toLowerCase();
  if(q){const hay=(l.name+l.plat+l.play+l.earn+l.tags.join("")+l.cat).toLowerCase();
    if(!hay.includes(q))return false;}
  return true;
}
function render(){
  let list=LEADS.filter(match);
  if(sortKey==="lvl")list.sort((a,b)=>(a.lvl==="低"?0:a.lvl==="中"?1:2)-(b.lvl==="低"?0:b.lvl==="中"?1:2));
  if(sortKey==="lvlD")list.sort((a,b)=>(a.lvl==="高"?0:a.lvl==="中"?1:2)-(b.lvl==="高"?0:b.lvl==="中"?1:2));
  const grid=document.getElementById("grid");
  grid.innerHTML=list.map(card).join("");
  document.getElementById("stats").textContent=
    "共 "+LEADS.length+" 条 · 当前显示 "+list.length+" 条"+(mineOnly?"（仅我的清单）":"");
  const cnt=Object.values(state).filter(s=>s&&s.s&&s.s.length).length;
  document.getElementById("minebtn").textContent="我的清单 ("+cnt+")";
}
function tagChips(l){
  const t=[l.cat,...l.tags.filter(t=>t!==l.cat)];
  return t.map(x=>{const c=CATCOLOR[x]||"#64748b";return '<span class="tag" style="background:'+c+'">'+esc(x)+'</span>';}).join("");
}
function card(l){
  const s=state[l.num]||{s:[],n:""};
  const on=(k)=>s.s&&s.s.includes(k)?" on":"";
  return `<div class="card">
    <div class="hd"><div class="nm">${esc(l.name)}</div><div class="no">#${esc(l.num)}</div></div>
    <div class="tagrow">${tagChips(l)}<span class="lvl ${l.lvl}">门槛${l.lvl}</span>${l.novice?'<span class="tag" style="background:#0ea5e9">纯小白友好</span>':''}${l.region==='海外'?'<span class="tag" style="background:#7c3aed">海外</span>':''}</div>
    <div class="kv"><b>平台：</b><span class="v">${esc(l.plat)}</span></div>
    <div class="play">${esc(l.play)}</div>
    <div class="kv"><b>变现：</b><span class="v">${esc(l.earn)}</span></div>
    <div class="kv"><b>门槛：</b><span class="v">${esc(l.barrier)}</span></div>
    <div class="actions">
      <span class="act want${on('want')}" onclick="toggle('${l.num}','want',this)">★ 想做</span>
      <span class="act tried${on('tried')}" onclick="toggle('${l.num}','tried',this)">✓ 试过</span>
      <span class="act fav${on('fav')}" onclick="toggle('${l.num}','fav',this)">🔖 收藏</span>
      <span class="act" onclick="toggleNote('${l.num}',this)">✎ 备注</span>
    </div>
    <textarea class="note${s.n?' show':''}" id="n-${l.num}" oninput="saveNote('${l.num}',this.value)">${esc(s.n||'')}</textarea>
  </div>`;
}
function toggle(num,k,el){
  const s=state[num]||{s:[],n:""};
  if(!s.s)s.s=[];
  const i=s.s.indexOf(k);
  if(i>=0)s.s.splice(i,1);else s.s.push(k);
  state[num]=s;save();render();
}
function toggleNote(num,el){
  const ta=document.getElementById("n-"+num);
  ta.classList.toggle("show");
  if(ta.classList.contains("show"))ta.focus();
}
function saveNote(num,v){
  const s=state[num]||{s:[],n:""};
  s.n=v;state[num]=s;save();
}
function toggleMine(){mineOnly=!mineOnly;document.getElementById("minebtn").classList.toggle("on",mineOnly);render();}
function resetFilters(){F.cat.clear();F.lvl.clear();F.nov.clear();F.reg.clear();F.iss.clear();
  document.querySelectorAll(".side .chip.on").forEach(e=>e.classList.remove("on"));
  document.getElementById("q").value="";mineOnly=false;document.getElementById("minebtn").classList.remove("on");render();}
function esc(s){return String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));}
function openExport(){
  const lines=["# 我的副业清单（"+new Date().toISOString().slice(0,10)+"）",""];
  Object.keys(state).forEach(num=>{const s=state[num];if(!s||!s.s||!s.s.length)return;
    const l=LEADS.find(x=>x.num===num);if(!l)return;
    lines.push("## "+l.name+" (#"+num+") ["+s.s.join("/")+"]");
    lines.push("- 类型："+l.cat+" · 门槛："+l.lvl+(l.novice?" · 纯小白友好":"")+" · "+l.region);
    lines.push("- 平台："+l.plat);
    lines.push("- 玩法："+l.play);
    lines.push("- 变现："+l.earn);
    if(s.n)lines.push("- 备注："+s.n);
    lines.push("");});
  document.getElementById("expout").value=lines.join("\n");
  document.getElementById("modal").classList.add("show");
}
function closeExport(){document.getElementById("modal").classList.remove("show");}
function copyExp(){const t=document.getElementById("expout");t.select();document.execCommand("copy");}
function downloadExp(){const t=document.getElementById("expout").value;
  const b=new Blob([t],{type:"text/markdown"});const u=URL.createObjectURL(b);
  const a=document.createElement("a");a.href=u;a.download="我的副业清单.md";a.click();URL.revokeObjectURL(u);}
buildChips();render();
</script>
</body>
</html>
"""

out = TEMPLATE.replace("{data}", DATA).replace("{issues}", ISSUES).replace("{catcolor}", CATCOLOR)
open(OUT, "w", encoding="utf-8").write(out)
print("已生成:", OUT, "大小", os.path.getsize(OUT), "bytes")
