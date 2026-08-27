# -*- coding: utf-8 -*-
"""爆款作战中台 · A 静态HTML生成器
读取 运营数据库.json + 3核心md + 12变体md → 生成自包含 index.html（零依赖双击开）
"""
import json, os, glob
import markdown

BASE = "D:/workbuddy/小红书运营工作流"
OUT_DIR = os.path.join(BASE, "中台面板")
os.makedirs(OUT_DIR, exist_ok=True)

def render_md(path):
    try:
        with open(path, encoding="utf-8") as f:
            txt = f.read()
        return markdown.markdown(txt, extensions=["tables", "fenced_code", "toc"])
    except Exception as e:
        return f"<p style='color:red'>渲染失败: {e}</p>"

# ---- 读取数据 ----
db = json.load(open(os.path.join(BASE, "运营数据库.json"), encoding="utf-8"))

core_docs = {
    "爆款公式": os.path.join(BASE, "我的爆款截图/我的爆款公式 v1.0.md"),
    "爆款判断逻辑": os.path.join(BASE, "爆款判断逻辑.md"),
    "爆款底层逻辑": os.path.join(BASE, "爆款底层逻辑（人性+小沈+dontbesilent 融合）.md"),
}
core_html = {k: render_md(v) for k, v in core_docs.items()}

variant_files = sorted(glob.glob(os.path.join(BASE, "我的爆款变体/*.md")))
variant_html = {}
for vf in variant_files:
    name = os.path.basename(vf).replace(".md", "")
    if name == "说明":
        continue
    variant_html[name] = render_md(vf)

# 复盘 SOP
review_sop = render_md(os.path.join(BASE, "复盘回写SOP.md"))
review_table = render_md(os.path.join(BASE, "复盘记录表.md"))

# ---- 分析象限内容（来自 skill 摘要）----
analysis_html = """
<h3>① 深度分析元技能 · xhs-deep-analysis</h3>
<p>强制四步法，杜绝泛泛：</p>
<ol>
<li><b>列视角（≥5个）</b>：人性透镜 / 传播学透镜 / 平台算法透镜 / 商业闭环透镜 / 合规生存透镜 / 竞品对照透镜</li>
<li><b>多透镜拆解</b>：每透镜给"为什么成立/不成立"的具体机制 + 至少1条可验证洞察</li>
<li><b>自我批判（反对者视角）</b>：挑"站不住/结果倒推/漏维度"的论点，不过关降级或删除</li>
<li><b>改写合成</b>：每条结论标视角来源 <code>[人性·代理努力]</code>，末尾给3个可执行动作</li>
</ol>
<p><span class="tag">铁律</span>禁止"内容优质/踩中痛点"等空话；每条结论必须落到具体心理/平台机制或动作。</p>
<h3>② 多Agent辩论 · xhs-debate</h3>
<p>生成Agent出稿 → 批判Agent挑刺"为什么不会火/像硬广/触发限流"（≥3条具体攻击）→ 主Agent合成终稿，附"批判→修复"对照表。两Agent独立上下文，防自我合理化。</p>
<p><span class="tag warn">实测</span>变体12（葛欣三节）经辩论合成，批判关抓出3条致命线（自杀式暗号/虚假稀缺/零干货）并已修复。</p>
<h3>③ 一键触发</h3>
<p>在对话里说对应口令即可调用：<code>用 xhs-deep-analysis 拆解</code> · <code>用 xhs-debate 生成</code></p>
"""

# 合规闸门 11 项
checklist = [
    "捷径钩子（代理努力/走捷径自我欺骗许可）",
    "低启动成本（几节/倍速/几分钟，认知吝啬）",
    "稀缺紧迫（损失厌恶+怕错过）",
    "群体共识（别人都在冲/考公人选出来）",
    "沉默解除（替受众认怂/我替你问）",
    "立场锁定（框架理论把'学不会'归外因）",
    "表达降维（大字报/口语/真实图，降认知负荷）",
    "权威代理（老师IP背书，把羞耻外包）",
    "评论区设计（A/B版暗号+互动钩子）",
    "合规暗号（無償/群聊，且无明写敏感词）",
    "产品闭环（诱饵→群聊→网盘口令链路清晰）",
]

# ---- 嵌入 JS 的素材库数据 ----
cai = db["素材库"]
schedule = db["发布排期"]
review = db["复盘记录"]
assets = db["资产中心"]

import html as _html
def esc(s):
    return _html.escape(str(s))

# 素材库分类渲染
cai_blocks = ""
cat_labels = {
    "选题库": "📌 选题库", "标题库": "🔤 标题库", "封面模板库": "🎨 封面模板库",
    "钩子金句库": "🔥 钩子金句库", "评论话术库": "💬 评论话术库", "竞品对标库": "🆚 竞品对标库",
    "爆款档案": "🏆 爆款档案", "人设声音档案": "👤 人设声音档案", "热点日历": "📅 热点日历",
    "违规限流案例库": "⚠️ 违规限流案例库",
}
for cat, label in cat_labels.items():
    items = cai.get(cat, [])
    rows = ""
    for it in items:
        if cat == "爆款档案":
            rows += f"<li><b>{esc(it.get('标题',''))}</b> · {esc(it.get('模块',''))}/{esc(it.get('老师',''))} · <span class='muted'>{esc(it.get('人性落点',''))}</span></li>"
        elif cat == "评论话术库":
            rows += f"<li><b>[{esc(it.get('id',''))}] {esc(it.get('版本',''))}</b><br><span class='quote'>{esc(it.get('话术',''))}</span></li>"
        elif cat in ("人设声音档案",):
            rows += f"<li>{esc(it)}</li>"
        else:
            content = it.get("内容") or it.get("模板") or it.get("名称") or it.get("金句") or it.get("观察") or it.get("案例") or it.get("事件") or ""
            extra = it.get("范例") or it.get("要素") or it.get("人性") or it.get("对照结论") or it.get("教训") or it.get("动作") or it.get("标签") or it.get("来源") or ""
            rows += f"<li><b>{esc(content)}</b>" + (f"<br><span class='muted'>{esc(extra)}</span>" if extra else "") + "</li>"
    cai_blocks += f"""
    <div class="cat">
      <div class="cat-h" onclick="this.parentElement.classList.toggle('open')">{label} <span class="cnt">{len(items)}</span></div>
      <div class="cat-b"><ul>{rows}</ul></div>
    </div>"""

# 变体列表
var_list = "".join(
    f'<li class="var-item" onclick="showVar({i})">{esc(n)}</li>'
    for i, n in enumerate(variant_html.keys())
)
var_panels = "".join(
    f'<div class="var-panel" id="var{i}" style="display:none">{h}</div>'
    for i, (n, h) in enumerate(variant_html.items())
)

# 排期表
sched_rows = "".join(
    f"<tr><td>{esc(r.get('日期',''))}</td><td>{esc(r.get('账号',''))}</td><td>{esc(r.get('模块',''))}</td><td>{esc(r.get('变体',''))}</td><td>{esc(r.get('状态',''))}</td><td class='{'fail' if r.get('合规闸门')=='未过' else 'ok'}'>{esc(r.get('合规闸门',''))}</td></tr>"
    for r in schedule
)

# 复盘表
review_rows = "".join(
    f"<tr><td>{esc(r.get('日期',''))}</td><td>{esc(r.get('标题',''))}</td><td>{esc(r.get('结果',''))}</td><td>{esc(r.get('原因',''))}</td><td>{esc(r.get('异常信号',''))}</td><td>{esc(r.get('回写结论',''))}</td></tr>"
    for r in review
)

# 资产中心
asset_html = f"""
<div class="cards">
  <div class="card"><h4>人设卡</h4><p>{esc(assets['人设卡'])}</p></div>
  <div class="card"><h4>封面模板</h4><p>{esc('、'.join(assets['封面模板']))}</p></div>
  <div class="card"><h4>图片库</h4><p>{esc('、'.join(assets['图片库']))}</p></div>
</div>"""

# 合规闸门 checkboxes
chk_html = "".join(
    f'<label class="chk"><input type="checkbox" onchange="checkGate()"> {esc(c)}</label>'
    for c in checklist
)

PROMPTS = {
    "gen": "用爆款公式生成新变体（主题：__，模块：__，老师：__）",
    "deep": "用 xhs-deep-analysis 拆解：[链接或主题]",
    "debate": "用 xhs-debate 生成：[主题]（高命中率不翻车）",
    "add": "把这条素材加入素材库：[内容]，分类：[选题库/标题库/钩子金句库/...]",
    "review": "复盘回写：标题__ 结果(火/一般/没爆)__ 原因__ 异常信号__",
}

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>爆款作战中台 · 上岸号</title>
<style>
*{{box-sizing:border-box}}
body{{margin:0;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#f4f6fa;color:#1f2733;font-size:14px}}
.app{{display:flex;min-height:100vh}}
.side{{width:218px;background:#1f2733;color:#cfd6e0;padding:18px 0;position:fixed;height:100vh;overflow:auto}}
.side h1{{font-size:15px;color:#fff;padding:0 18px;margin:0 0 4px}}
.side .sub{{font-size:11px;color:#7c8794;padding:0 18px 14px;border-bottom:1px solid #2c3744}}
.nav{{margin-top:10px}}
.nav button{{display:block;width:100%;text-align:left;background:none;border:none;color:#cfd6e0;padding:11px 18px;font-size:13.5px;cursor:pointer;border-left:3px solid transparent}}
.nav button:hover{{background:#2a3543;color:#fff}}
.nav button.active{{background:#2a3543;color:#fff;border-left-color:#ff6a3d}}
.main{{margin-left:218px;flex:1;padding:26px 32px;max-width:1100px}}
section{{display:none}} section.active{{display:block}}
h2{{font-size:20px;margin:0 0 6px}}
.lead{{color:#6b7480;margin:0 0 18px;font-size:13px}}
.cards{{display:flex;gap:14px;flex-wrap:wrap}}
.card{{background:#fff;border:1px solid #e6eaf0;border-radius:10px;padding:14px 16px;flex:1;min-width:240px;box-shadow:0 1px 3px rgba(0,0,0,.04)}}
.card h4{{margin:0 0 8px;color:#ff6a3d;font-size:14px}}
.cat{{background:#fff;border:1px solid #e6eaf0;border-radius:10px;margin-bottom:10px;overflow:hidden}}
.cat-h{{padding:12px 16px;font-weight:600;cursor:pointer;display:flex;justify-content:space-between;align-items:center}}
.cat-h:hover{{background:#fafbfc}}
.cat .cnt{{background:#ff6a3d;color:#fff;border-radius:20px;padding:1px 9px;font-size:11px}}
.cat-b{{display:none;padding:4px 18px 14px}}
.cat.open .cat-b{{display:block}}
.cat-b ul{{margin:0;padding-left:18px}} .cat-b li{{margin:6px 0;line-height:1.6}}
.tag{{background:#e8f0ff;color:#2b6cff;padding:2px 8px;border-radius:5px;font-size:11px}}
.tag.warn{{background:#fff0e8;color:#ff6a3d}}
.muted{{color:#8a93a0;font-size:12px}} .quote{{color:#444;background:#f7f8fa;padding:4px 8px;border-radius:6px;display:inline-block;font-size:12.5px}}
table{{width:100%;border-collapse:collapse;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.04)}}
th,td{{border:1px solid #eef1f5;padding:9px 11px;text-align:left;font-size:13px}}
th{{background:#f7f9fc;color:#5a6470}}
.ok{{color:#1a9d5a;font-weight:600}} .fail{{color:#e0492f;font-weight:600}}
.tabs{{display:flex;gap:8px;margin-bottom:14px}}
.tabs button{{background:#fff;border:1px solid #e0e5ec;border-radius:8px;padding:8px 16px;cursor:pointer;font-size:13px}}
.tabs button.active{{background:#ff6a3d;color:#fff;border-color:#ff6a3d}}
.doc{{background:#fff;border:1px solid #e6eaf0;border-radius:10px;padding:20px 26px;line-height:1.75;box-shadow:0 1px 3px rgba(0,0,0,.04)}}
.doc h1,.doc h2,.doc h3{{color:#1f2733}} .doc h1{{font-size:20px;border-bottom:2px solid #ff6a3d;padding-bottom:8px}}
.doc table{{margin:12px 0}} .doc code{{background:#f1f3f7;padding:1px 6px;border-radius:4px;font-size:12.5px}}
.var-list{{background:#fff;border:1px solid #e6eaf0;border-radius:10px;padding:10px;max-height:300px;overflow:auto;margin-bottom:14px}}
.var-item{{padding:9px 12px;border-radius:7px;cursor:pointer}} .var-item:hover{{background:#f4f6fa}}
.var-panel{{background:#fff;border:1px solid #e6eaf0;border-radius:10px;padding:20px 26px;line-height:1.75}}
.btn{{background:#ff6a3d;color:#fff;border:none;border-radius:8px;padding:9px 16px;cursor:pointer;font-size:13px;margin:4px 6px 4px 0}}
.btn.ghost{{background:#fff;color:#ff6a3d;border:1px solid #ff6a3d}}
.btnrow{{margin-bottom:18px}}
.modal-mask{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:50}}
.modal{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:560px;max-width:92vw;background:#fff;border-radius:14px;padding:24px;max-height:86vh;overflow:auto}}
.modal h3{{margin-top:0;color:#ff6a3d}}
.chk{{display:block;margin:9px 0;font-size:13px}} .chk input{{margin-right:8px}}
#gateResult{{margin-top:14px;font-weight:700;font-size:15px}}
textarea{{width:100%;min-height:120px;border:1px solid #d8dee6;border-radius:8px;padding:10px;font-family:inherit;font-size:13px}}
.toast{{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:#1f2733;color:#fff;padding:10px 20px;border-radius:8px;opacity:0;transition:.3s;z-index:99}}
.toast.show{{opacity:1}}
.missing{{border:2px dashed #ff6a3d;border-radius:12px;padding:16px 18px;margin-top:14px;background:#fff8f5}}
.missing h3{{color:#ff6a3d;margin-top:0}}
</style></head>
<body><div class="app">
<aside class="side">
  <h1>爆款作战中台</h1>
  <div class="sub">上岸号 · 公考网盘推广<br>素材→逻辑→生成→分析 闭环</div>
  <nav class="nav">
    <button class="active" data-t="cailiao">📥 素材库</button>
    <button data-t="logic">🧠 爆款逻辑</button>
    <button data-t="generated">🚀 生成物</button>
    <button data-t="analysis">🔬 分析</button>
    <button data-t="schedule">📆 发布排期</button>
    <button data-t="review">🔄 复盘闭环</button>
    <button data-t="assets">🗂 资产中心</button>
  </nav>
  <div style="padding:14px 18px"><button class="btn" onclick="openGate()" style="width:100%">🛡 合规风控闸门</button></div>
</aside>
<main class="main">
  <section id="cailiao" class="active">
    <h2>📥 素材库（你的 Inbox）</h2>
    <p class="lead">不断往里放的raw素材，10大子库已结构化。点分类展开。要加新素材 → 复制下方指令发给我。</p>
    <div class="btnrow"><button class="btn ghost" onclick="copy('add')">➕ 复制「添加素材」指令</button></div>
    {cai_blocks}
  </section>

  <section id="logic">
    <h2>🧠 爆款逻辑（方法论大脑）</h2>
    <p class="lead">三份核心文档即你的"共享大脑"，生成与分析都从这儿取规则。</p>
    <div class="tabs">
      <button class="active" data-d="爆款公式">爆款公式</button>
      <button data-d="爆款判断逻辑">爆款判断逻辑</button>
      <button data-d="爆款底层逻辑">爆款底层逻辑</button>
    </div>
    <div id="logic-爆款公式" class="doc">{core_html['爆款公式']}</div>
    <div id="logic-爆款判断逻辑" class="doc" style="display:none">{core_html['爆款判断逻辑']}</div>
    <div id="logic-爆款底层逻辑" class="doc" style="display:none">{core_html['爆款底层逻辑']}</div>
  </section>

  <section id="generated">
    <h2>🚀 生成物（根据素材/公式产出）</h2>
    <p class="lead">12篇变体，点列表查看。生成时已过 11项人性自检 + 批判关。</p>
    <div class="btnrow">
      <button class="btn" onclick="copy('gen')">🚀 复制「生成新变体」指令</button>
      <button class="btn" onclick="copy('debate')">⚔ 复制「辩论生成」指令</button>
    </div>
    <div class="var-list"><ul style="list-style:none;margin:0;padding:0">{var_list}</ul></div>
    {var_panels}
  </section>

  <section id="analysis">
    <h2>🔬 分析（对生成物/竞品的多角度透视）</h2>
    <p class="lead">不是泛泛拆解，而是强制多透镜 + 自我批判 + 辩论挑刺。</p>
    <div class="doc">{analysis_html}</div>
    <div class="missing">
      <h3>⚠️ 你之前缺的分析维度（现已补齐）</h3>
      <p>① 批判复核关（反对者+平台审核双视角挑刺）— 由 xhs-debate 提供<br>
      ② 结果回灌闭环（真实火/没火→回写公式）— 由复盘回写SOP提供<br>
      这俩是"分析得透"和"越用越准"的关键缺口。</p>
    </div>
  </section>

  <section id="schedule">
    <h2>📆 发布排期 / 多账号矩阵</h2>
    <p class="lead">生成完到发布的断层。合规闸门"未过"的笔记不允许发。</p>
    <table><thead><tr><th>日期</th><th>账号</th><th>模块</th><th>变体</th><th>状态</th><th>合规闸门</th></tr></thead><tbody>{sched_rows}</tbody></table>
  </section>

  <section id="review">
    <h2>🔄 复盘闭环（让AI从真实胜负进化）</h2>
    <p class="lead">发完一篇告诉我火/没火+原因，我回写进《爆款判断逻辑》。这是第6层（结果回灌）。</p>
    <div class="btnrow"><button class="btn ghost" onclick="copy('review')">🔄 复制「复盘回写」指令</button>
    <button class="btn ghost" onclick="copy('deep')">🔬 复制「深度分析」指令</button></div>
    <div class="doc">{review_sop}</div>
    <h3 style="margin-top:18px">复盘记录表</h3>
    <table><thead><tr><th>日期</th><th>标题</th><th>结果</th><th>原因</th><th>异常信号</th><th>回写结论</th></tr></thead><tbody>{review_rows}</tbody></table>
    <div class="doc" style="margin-top:14px">{review_table}</div>
  </section>

  <section id="assets">
    <h2>🗂 资产中心（一致性保障）</h2>
    <p class="lead">人设卡/封面模板/图片库，保证跨账号跨笔记风格统一。</p>
    {asset_html}
  </section>
</main></div>

<div class="modal-mask" id="gateMask" onclick="if(event.target===this)closeGate()">
  <div class="modal">
    <h3>🛡 合规风控闸门 · 11项人性自检</h3>
    <p style="font-size:12.5px;color:#6b7480">把待发笔记正文粘到下方，逐项勾选。11项全过才允许发布。</p>
    <textarea id="gateText" placeholder="粘贴待发笔记正文..."></textarea>
    <div style="margin-top:12px">{chk_html}</div>
    <div id="gateResult"></div>
    <div style="margin-top:14px;text-align:right">
      <button class="btn ghost" onclick="closeGate()">关闭</button>
      <button class="btn" onclick="copy('gen')">据此生成新变体</button>
    </div>
  </div>
</div>
<div class="toast" id="toast"></div>

<script>
const PROMPTS = {json.dumps(PROMPTS, ensure_ascii=False)};
function copy(k){{navigator.clipboard.writeText(PROMPTS[k]).then(()=>toast('已复制指令，去对话里粘贴发送'));}}
function toast(m){{const t=document.getElementById('toast');t.textContent=m;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2200);}}
// nav
document.querySelectorAll('.nav button').forEach(b=>b.onclick=()=>{{
  document.querySelectorAll('.nav button').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('section').forEach(s=>s.classList.remove('active'));
  b.classList.add('active');document.getElementById(b.dataset.t).classList.add('active');
}});
// logic tabs
document.querySelectorAll('#logic .tabs button').forEach(b=>b.onclick=()=>{{
  document.querySelectorAll('#logic .tabs button').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('#logic .doc').forEach(d=>d.style.display='none');
  b.classList.add('active');document.getElementById('logic-'+b.dataset.d).style.display='block';
}});
// variant
function showVar(i){{document.querySelectorAll('.var-panel').forEach(p=>p.style.display='none');document.getElementById('var'+i).style.display='block';window.scrollTo({{top:document.getElementById('var'+i).offsetTop-20,behavior:'smooth'}});}}
// gate
function openGate(){{document.getElementById('gateMask').style.display='block';}}
function closeGate(){{document.getElementById('gateMask').style.display='none';}}
function checkGate(){{const boxes=document.querySelectorAll('#gateMask input[type=checkbox]');const n=boxes.length,done=[...boxes].filter(b=>b.checked).length;const r=document.getElementById('gateResult');if(done===n){{r.style.color='#1a9d5a';r.textContent='✅ 11/11 全过 — 可以发布';}}else{{r.style.color='#e0492f';r.textContent=`❌ ${{done}}/11 已过 — 还差 ${{n-done}} 项，未过闸门不准发`;}}}}
</script></body></html>"""

out = os.path.join(OUT_DIR, "index.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(HTML)
print("生成成功:", out, "| 大小:", len(HTML), "字符 | 变体数:", len(variant_html))
