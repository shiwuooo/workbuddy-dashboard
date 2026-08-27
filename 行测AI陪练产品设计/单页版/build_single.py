# -*- coding: utf-8 -*-
"""从完整真题库抽取精选卷，导出为 window.BANK 结构的 bank.js（单页版可直接 file:// 加载）。"""
import json, random, os
from collections import defaultdict

SRC = "D:/workbuddy/Claw/考公刷题网站/bank/_dump_all.json"
OUT_DIR = "D:/workbuddy/行测AI陪练产品设计/单页版"
OUT = os.path.join(OUT_DIR, "bank.js")
os.makedirs(OUT_DIR, exist_ok=True)

print("加载题库(228MB)，稍候...")
data = json.load(open(SRC, encoding="utf-8"))
print("总套卷:", len(data))

random.seed(20260815)
byyear = defaultdict(list)
for p in data:
    y = str(p.get("year") or (p.get("name", "")[:4]))
    byyear[y].append(p)

# 每年份均衡抽取，保证年份覆盖；再打乱取 N 套
sel = []
per = 7
for y in sorted(byyear.keys()):
    ps = byyear[y]
    random.shuffle(ps)
    sel += ps[:per]
random.shuffle(sel)
N = min(90, len(sel))
sel = sel[:N]

CN = {"changshi": "常识判断", "yanyu": "言语理解与表达", "shuliang": "数量关系",
      "panduan": "判断推理", "ziliao": "资料分析"}
QS_MODULES = set(CN.keys())  # 只保留行测 5 模块，过滤掉申论/政治等非行测题
module_names = {}
out_papers = []
total_q = 0
for p in sel:
    qs = []
    for q in p.get("questions", []):
        m = q.get("module")
        if m not in QS_MODULES:
            continue
        ans = q.get("answer")
        opts = q.get("options") or []
        qtext = (q.get("q") or "").strip()
        if not qtext or not opts or ans is None or ans == "":
            continue
        if m:
            module_names[m] = CN.get(m, m)
        qs.append({
            "id": q.get("id"), "module": m, "q": q.get("q", ""),
            "material": q.get("material", ""), "options": q.get("options", []),
            "answer": q.get("answer"), "explain": q.get("explain", ""),
            "keypoints": q.get("keypoints", [])
        })
    if qs:
        total_q += len(qs)
        out_papers.append({"id": str(p.get("id")), "name": p.get("name", ""),
                           "year": p.get("year", ""), "total": len(qs), "qs": qs})

with open(OUT, "w", encoding="utf-8") as f:
    f.write("window.BANK=")
    json.dump({"module_names": module_names, "papers": out_papers},
              f, ensure_ascii=False, separators=(",", ":"))
    f.write(";")

print("导出套卷:", len(out_papers), "总题数:", total_q,
      "模块:", list(module_names.keys()))
print("bank.js 大小(MB):", round(os.path.getsize(OUT) / 1024 / 1024, 2))
