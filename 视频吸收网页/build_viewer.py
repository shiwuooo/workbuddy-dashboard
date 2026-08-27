# -*- coding: utf-8 -*-
"""把 Obsidian 视频吸收/ 下所有分析 md 生成单文件网页看板（零外部依赖）。"""
import os, re, html, json
import markdown

ROOT = r"D:/workbuddy/ObsidianVault/视频吸收"
OUT_DIR = r"D:/workbuddy/视频吸收网页"
OUT = os.path.join(OUT_DIR, "index.html")

CAT_ORDER = ["公考", "成长", "埃德蒙", "小六壬", "创业"]
CAT_COLOR = {
    "公考": "#e0563b",
    "成长": "#1f9d72",
    "埃德蒙": "#3b6fe0",
    "小六壬": "#9b59b6",
    "创业": "#d98b1f",
}

def clean_wikilinks(text):
    # [[xxx|y]] -> y ; [[xxx]] -> xxx
    text = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    return text

def slugify(cat, title, i):
    s = re.sub(r"[^\w一-鿿-]", "_", title)
    return f"{cat}_{i}_{s}"[:80]

MD = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists", "toc"])

def md_to_html(md_text):
    MD.reset()
    return MD.convert(clean_wikilinks(md_text))

def collect():
    cats = []
    names = [d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d))]
    names.sort(key=lambda n: CAT_ORDER.index(n) if n in CAT_ORDER else 99)
    for cat in names:
        catdir = os.path.join(ROOT, cat)
        items = []
        for dp, dn, fns in os.walk(catdir):
            for fn in fns:
                if not fn.endswith(".md"):
                    continue
                full = os.path.join(dp, fn)
                title = fn[:-3]
                is_summary = ("汇总" in fn) or ("深度分析" in fn)
                items.append((title, full, is_summary, dp))
        # summaries first, then by folder depth then name
        items.sort(key=lambda x: (not x[2], x[3] != catdir, x[0]))
        cats.append({"name": cat, "items": items})
    return cats

def build():
    cats = collect()
    nav = []
    sections = []
    for cat in cats:
        color = CAT_COLOR.get(cat["name"], "#666")
        children = []
        for i, (title, full, is_summary, dp) in enumerate(cat["items"]):
            sid = slugify(cat["name"], title, i)
            with open(full, "r", encoding="utf-8") as f:
                raw = f.read()
            body = md_to_html(raw)
            sections.append(
                f'<section class="doc" id="{sid}" data-cat="{html.escape(cat["name"])}" '
                f'data-title="{html.escape(title)}" data-summary="{"1" if is_summary else "0"}">'
                f'<div class="doc-head"><span class="tag" style="background:{color}">'
                f'{html.escape(cat["name"])}</span>'
                f'{"<span class=sumtag>汇总</span>" if is_summary else ""}'
                f'<h1>{html.escape(title)}</h1></div>{body}</section>'
            )
            children.append({"id": sid, "title": title, "summary": is_summary})
        nav.append({"name": cat["name"], "color": color, "children": children})

    nav_json = json.dumps(nav, ensure_ascii=False).replace("</", "<\\/")
    total = sum(len(c["items"]) for c in cats)

    css = """
    :root{--bg:#f6f7f9;--panel:#fff;--line:#e6e8eb;--text:#1f2329;--muted:#8a9099;--accent:#3b6fe0;}
    *{box-sizing:border-box;}
    body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
         background:var(--bg);color:var(--text);font-size:15px;line-height:1.7;}
    header{position:sticky;top:0;z-index:20;background:var(--panel);border-bottom:1px solid var(--line);
           padding:12px 20px;display:flex;align-items:center;gap:16px;flex-wrap:wrap;}
    header h2{margin:0;font-size:18px;}
    .stats{color:var(--muted);font-size:13px;}
    .search{flex:1;min-width:180px;max-width:360px;padding:8px 12px;border:1px solid var(--line);border-radius:8px;
            font-size:14px;outline:none;}
    .search:focus{border-color:var(--accent);}
    .layout{display:flex;min-height:calc(100vh - 57px);}
    nav{width:300px;flex:none;background:var(--panel);border-right:1px solid var(--line);
        overflow-y:auto;max-height:calc(100vh - 57px);padding:8px 0;}
    .cat{border-bottom:1px solid var(--line);}
    .cat-head{padding:10px 16px;cursor:pointer;display:flex;align-items:center;gap:8px;font-weight:600;
              user-select:none;}
    .cat-head .dot{width:10px;height:10px;border-radius:50%;}
    .cat-head .cnt{margin-left:auto;color:var(--muted);font-size:12px;font-weight:400;}
    .cat-head .arrow{transition:transform .15s;color:var(--muted);}
    .cat.collapsed .arrow{transform:rotate(-90deg);}
    .cat.collapsed .ep{display:none;}
    .ep{padding:2px 0 2px 0;}
    .ep a{display:block;padding:6px 16px 6px 32px;color:var(--text);text-decoration:none;font-size:13.5px;
          border-left:3px solid transparent;cursor:pointer;line-height:1.45;}
    .ep a:hover{background:#f0f4ff;}
    .ep a.active{border-left-color:var(--accent);background:#eaf1ff;font-weight:600;}
    .ep a .st{display:inline-block;font-size:10px;color:#fff;background:#b08; border-radius:3px;
              padding:0 4px;margin-right:5px;vertical-align:middle;}
    main{flex:1;overflow-y:auto;max-height:calc(100vh - 57px);padding:28px 40px 80px;}
    .doc{display:none;max-width:920px;margin:0 auto;}
    .doc.show{display:block;}
    .doc-head{margin-bottom:14px;}
    .doc-head h1{font-size:24px;margin:8px 0 0;}
    .tag{color:#fff;font-size:12px;padding:2px 9px;border-radius:5px;}
    .sumtag{font-size:11px;color:#b08;border:1px solid #b08;border-radius:4px;padding:1px 6px;margin-left:6px;}
    .doc h2{border-left:4px solid var(--accent);padding-left:10px;margin-top:30px;font-size:20px;}
    .doc h3{margin-top:22px;font-size:17px;color:#2b3340;}
    .doc p{margin:10px 0;}
    .doc ul,.doc ol{padding-left:24px;}
    .doc li{margin:5px 0;}
    .doc code{background:#eef1f5;padding:1px 5px;border-radius:4px;font-size:13px;}
    .doc pre{background:#1f2329;color:#e6e6e6;padding:14px;border-radius:8px;overflow:auto;}
    .doc pre code{background:none;color:inherit;padding:0;}
    .doc blockquote{border-left:3px solid #ccc;margin:12px 0;padding:4px 14px;color:#555;background:#fafafa;}
    .doc table{border-collapse:collapse;width:100%;margin:14px 0;font-size:14px;}
    .doc th,.doc td{border:1px solid var(--line);padding:8px 11px;text-align:left;}
    .doc th{background:#f0f4ff;font-weight:600;}
    .doc tr:nth-child(even) td{background:#fafbfc;}
    .empty{color:var(--muted);text-align:center;margin-top:80px;}
    @media(max-width:760px){nav{width:100%;max-height:40vh;} .layout{flex-direction:column;} main{max-height:none;}}
    """
    js = """
    const NAV = JSON.parse(document.getElementById('navdata').textContent);
    const navEl = document.getElementById('nav');
    const mainEl = document.getElementById('main');
    const searchEl = document.getElementById('search');
    let activeId = null;

    function buildNav(){
      NAV.forEach((c,ci)=>{
        const cat=document.createElement('div'); cat.className='cat';
        const head=document.createElement('div'); head.className='cat-head';
        head.innerHTML=`<span class="dot" style="background:${c.color}"></span>
          <span>${c.name}</span><span class="cnt">${c.children.length}</span>
          <span class="arrow">▾</span>`;
        head.onclick=()=>cat.classList.toggle('collapsed');
        cat.appendChild(head);
        const ep=document.createElement('div'); ep.className='ep';
        c.children.forEach(ch=>{
          const a=document.createElement('a');
          a.dataset.id=ch.id; a.dataset.title=ch.title; a.dataset.cat=c.name;
          a.innerHTML=(ch.summary?'<span class="st">汇总</span>':'')+ch.title;
          a.onclick=()=>show(ch.id);
          ep.appendChild(a);
        });
        cat.appendChild(ep);
        navEl.appendChild(cat);
      });
    }
    function show(id){
      document.querySelectorAll('.doc').forEach(d=>d.classList.remove('show'));
      const sec=document.getElementById(id);
      if(sec) sec.classList.add('show');
      document.querySelectorAll('.ep a').forEach(a=>a.classList.toggle('active',a.dataset.id===id));
      mainEl.scrollTop=0; activeId=id;
    }
    function filter(q){
      q=q.trim().toLowerCase();
      document.querySelectorAll('.cat').forEach((cat,ci)=>{
        let any=false;
        cat.querySelectorAll('.ep a').forEach(a=>{
          const hit=a.dataset.title.toLowerCase().includes(q)||a.dataset.cat.toLowerCase().includes(q);
          a.style.display=hit?'block':'none'; if(hit)any=true;
        });
        cat.style.display=(q===''||any)?'block':'none';
      });
    }
    searchEl.addEventListener('input',e=>filter(e.target.value));
    buildNav();
    // 默认展示第一个汇总的文档
    const firstSummary=document.querySelector('.doc');
    if(firstSummary) show(firstSummary.id);
    """
    # 把 nav_json 注入 js 数据块（用 application/json 避免括号计数问题）
    page = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>视频吸收 · 学习看板</title><style>{css}</style></head>
<body>
<header>
  <h2>📺 视频吸收 · 学习看板</h2>
  <span class="stats">共 {total} 篇 · 5 大分类</span>
  <input class="search" id="search" placeholder="搜索标题 / 分类…">
</header>
<div class="layout">
  <nav id="nav"></nav>
  <main id="main">
    {''.join(sections)}
    <div class="empty" id="empty" style="display:none">没有匹配的内容</div>
  </main>
</div>
<script type="application/json" id="navdata">{nav_json}</script>
<script>{js}</script>
</body></html>"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"OK -> {OUT}")
    print(f"分类: " + " / ".join(f"{c['name']}({len(c['items'])})" for c in cats))
    print(f"总文档数: {total}")

if __name__ == "__main__":
    build()
