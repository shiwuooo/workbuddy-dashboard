# -*- coding: utf-8 -*-
"""爆款作战中台 · B Streamlit 真交互面板
读取/编辑 运营数据库.json，渲染三核心md + 12变体，合规闸门校验。
启动：xhs_panel venv 的 streamlit run app.py
"""
import json, os, glob, streamlit as st

BASE = "D:/workbuddy/小红书运营工作流"
DB = os.path.join(BASE, "运营数据库.json")
VAR_DIR = os.path.join(BASE, "我的爆款变体")
REVIEW_MD = os.path.join(BASE, "复盘记录表.md")

st.set_page_config(page_title="爆款作战中台 · 上岸号", layout="wide")

@st.cache_data
def load_db():
    return json.load(open(DB, encoding="utf-8"))

def save_db(d):
    json.dump(d, open(DB, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def read_md(p):
    try:
        return open(p, encoding="utf-8").read()
    except Exception as e:
        return f"读取失败: {e}"

db = load_db()
cai = db["素材库"]

st.sidebar.title("🚀 爆款作战中台")
st.sidebar.caption("上岸号 · 公考网盘推广")
mod = st.sidebar.radio("模块", ["📥 素材库", "🧠 爆款逻辑", "🚀 生成物", "🔬 分析",
                                "📆 发布排期", "🔄 复盘闭环", "🗂 资产中心", "🛡 合规闸门"])

# ---------------- 素材库 ----------------
if mod == "📥 素材库":
    st.header("📥 素材库（你的 Inbox）")
    st.caption("10大子库结构化。新增素材会落盘到 运营数据库.json，A面板与飞书表同步。")
    cats = list(cai.keys())
    sel = st.selectbox("选择子库", cats)
    items = cai[sel]
    st.write(f"共 **{len(items)}** 条")
    for it in items:
        label = it.get("内容") or it.get("模板") or it.get("名称") or it.get("金句") or it.get("观察") or it.get("案例") or it.get("事件") or str(it)
        st.markdown(f"- {label}")
    st.divider()
    st.subheader("➕ 新增素材")
    with st.form("add_cai", clear_on_submit=True):
        c1, c2 = st.columns(2)
        new_cat = c2.selectbox("子库", cats, key="nc")
        new_content = c1.text_input("内容/标题")
        new_tag = st.text_input("标签(逗号分隔)")
        submitted = st.form_submit_button("添加")
        if submitted and new_content:
            entry = {"id": f"U{len(items)+1:03d}", "内容": new_content, "标签": [t.strip() for t in new_tag.split(",") if t.strip()], "来源": "面板新增", "日期": "2026-08-05"}
            cai[new_cat].append(entry)
            save_db(db)
            st.success(f"已加入 {new_cat}！刷新面板可见。")
            st.rerun()

# ---------------- 爆款逻辑 ----------------
elif mod == "🧠 爆款逻辑":
    st.header("🧠 爆款逻辑（方法论大脑）")
    tab = st.tabs(["爆款公式", "爆款判断逻辑", "爆款底层逻辑"])
    docs = {
        "爆款公式": os.path.join(BASE, "我的爆款截图/我的爆款公式 v1.0.md"),
        "爆款判断逻辑": os.path.join(BASE, "爆款判断逻辑.md"),
        "爆款底层逻辑": os.path.join(BASE, "爆款底层逻辑（人性+小沈+dontbesilent 融合）.md"),
    }
    for i, (name, p) in enumerate(docs.items()):
        with tab[i]:
            st.markdown(read_md(p), unsafe_allow_html=True)

# ---------------- 生成物 ----------------
elif mod == "🚀 生成物":
    st.header("🚀 生成物（12篇变体）")
    vfiles = sorted(glob.glob(os.path.join(VAR_DIR, "*.md")))
    vfiles = [v for v in vfiles if os.path.basename(v) != "说明.md"]
    names = [os.path.basename(v).replace(".md", "") for v in vfiles]
    pick = st.selectbox("选择变体", names)
    if pick:
        st.markdown(read_md(os.path.join(VAR_DIR, pick + ".md")), unsafe_allow_html=True)
    st.divider()
    st.info("💡 生成新变体：在对话里说「用爆款公式生成新变体（主题：__，模块：__，老师：__）」；要高命中率用「用 xhs-debate 生成」。")

# ---------------- 分析 ----------------
elif mod == "🔬 分析":
    st.header("🔬 分析（多角度透视）")
    st.markdown("""
### ① 深度分析元技能 · xhs-deep-analysis
强制四步法：
1. **列视角(≥5)**：人性 / 传播学 / 平台算法 / 商业闭环 / 合规生存 / 竞品对照
2. **多透镜拆解**：每透镜给具体机制 + 可验证洞察
3. **自我批判**：挑"站不住/结果倒推/漏维度"，不过关降级或删
4. **改写合成**：每条结论标视角来源，末尾给3动作

### ② 多Agent辩论 · xhs-debate
生成Agent出稿 → 批判Agent挑刺(≥3条具体攻击) → 合成终稿，附"批判→修复"对照。独立上下文防自我合理化。

### ③ 触发口令
`用 xhs-deep-analysis 拆解：[主题]` · `用 xhs-debate 生成：[主题]`
""", unsafe_allow_html=True)

# ---------------- 发布排期 ----------------
elif mod == "📆 发布排期":
    st.header("📆 发布排期 / 多账号矩阵")
    sched = db["发布排期"]
    edited = st.data_editor(sched, num_rows="dynamic", use_container_width=True, key="sched")
    if st.button("💾 保存排期"):
        db["发布排期"] = edited if isinstance(edited, list) else list(edited)
        save_db(db)
        st.success("排期已落盘")

# ---------------- 复盘闭环 ----------------
elif mod == "🔄 复盘闭环":
    st.header("🔄 复盘闭环（让AI从真实胜负进化）")
    st.caption("发完一篇告诉我火/没火+原因 → 我回写进《爆款判断逻辑》。这里可先记录，再粘贴给AI。")
    with st.form("add_review", clear_on_submit=True):
        c1, c2 = st.columns(2)
        r_date = c1.date_input("日期")
        r_title = c2.text_input("标题/主题")
        r_res = st.selectbox("结果", ["火(千赞+)", "一般", "没爆"])
        r_why = st.text_area("我的判断原因")
        r_sig = st.text_input("异常信号(小眼睛卡/评论少/被限流)")
        if st.form_submit_button("记录复盘") and r_title:
            db["复盘记录"].append({"日期": str(r_date), "标题": r_title, "结果": r_res, "原因": r_why, "异常信号": r_sig, "回写结论": ""})
            save_db(db)
            # 同步复盘记录表.md
            rows = "".join(f"| {r['日期']} | {r['标题']} | {r['结果']} | {r['原因']} | {r['异常信号']} | {r['回写结论']} |\n" for r in db["复盘记录"])
            open(REVIEW_MD, "w", encoding="utf-8").write("# 复盘记录表（追加式，不覆盖）\n\n| 日期 | 标题/主题 | 结果 | 我的判断原因 | 异常信号 | 回写结论 |\n|---|---|---|---|---|---|\n" + rows + "\n## 填写说明\n- 结果三档：火(千赞+) / 一般 / 没爆\n- 异常信号：小眼睛卡住 / 评论少 / 收藏高赞低 / 被限流\n- 回写结论由 AI 填：强化项 / 避坑项\n- 每次新增一行，不改动历史行\n")
            st.success("已记录并同步 复盘记录表.md")
            st.rerun()
    st.subheader("历史复盘")
    for r in db["复盘记录"]:
        st.markdown(f"- **{r['日期']}** {r['标题']} → `{r['结果']}` {('｜'+r['原因']) if r['原因'] else ''}")

# ---------------- 资产中心 ----------------
elif mod == "🗂 资产中心":
    st.header("🗂 资产中心（一致性保障）")
    a = db["资产中心"]
    c1, c2, c3 = st.columns(3)
    c1.markdown("**人设卡**\n\n" + "\n".join(f"- {k}: {v}" for k, v in a["人设卡"].items()))
    c2.markdown("**封面模板**\n\n" + "\n".join(f"- {t}" for t in a["封面模板"]))
    c3.markdown("**图片库**\n\n" + "\n".join(f"- {t}" for t in a["图片库"]))

# ---------------- 合规闸门 ----------------
elif mod == "🛡 合规闸门":
    st.header("🛡 合规风控闸门 · 11项人性自检")
    st.caption("把待发笔记正文粘到下方，逐项勾选。11项全过才允许发布。")
    text = st.text_area("待发笔记正文", height=160)
    checks = [
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
    done = 0
    for c in checks:
        if st.checkbox(c):
            done += 1
    if done == len(checks):
        st.success(f"✅ {done}/{len(checks)} 全过 — 可以发布")
    else:
        st.error(f"❌ {done}/{len(checks)} 已过 — 还差 {len(checks)-done} 项，未过闸门不准发")
    if text:
        banned = ["网盘", "夸克", "加群", "私信", "免费"]
        hit = [w for w in banned if w in text]
        if hit:
            st.warning(f"⚠️ 检测到敏感词(可能触发限流)：{', '.join(hit)} — 改用『群聊·無償』暗号")
        else:
            st.info("✓ 未检测到明文敏感词")
