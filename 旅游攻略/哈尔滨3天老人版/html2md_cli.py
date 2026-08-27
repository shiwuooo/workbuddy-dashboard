# -*- coding: utf-8 -*-
"""通用 HTML -> Markdown 转换器（保留标题/表格/列表/加粗/链接）。
用法：python html2md_cli.py -i input.html -o output.md
"""
import argparse
from bs4 import BeautifulSoup, NavigableString, Tag


def inline_children(elem):
    return "".join(inline(c) for c in elem.children)


def inline(elem):
    if isinstance(elem, NavigableString):
        return str(elem)
    if not isinstance(elem, Tag):
        return ""
    n = elem.name
    if n in ("strong", "b"):
        return "**" + inline_children(elem) + "**"
    if n in ("em", "i"):
        return "*" + inline_children(elem) + "*"
    if n == "a":
        href = elem.get("href", "")
        return "[" + inline_children(elem) + "](" + href + ")" if href else inline_children(elem)
    if n == "br":
        return "\n"
    if n == "code":
        return "`" + inline_children(elem) + "`"
    return inline_children(elem)


def clean_cell(td):
    return inline_children(td).replace("\n", " ").strip()


def table_to_md(table):
    rows = []
    for tr in table.find_all("tr"):
        rows.append([clean_cell(td) for td in tr.find_all(["td", "th"])])
    if not rows:
        return ""
    w = max(len(r) for r in rows)
    out = []
    out.append("| " + " | ".join(rows[0] + [""] * (w - len(rows[0]))) + " |")
    out.append("| " + " | ".join(["---"] * w) + " |")
    for r in rows[1:]:
        out.append("| " + " | ".join(r + [""] * (w - len(r))) + " |")
    return "\n".join(out)


def block(elem, out):
    if isinstance(elem, NavigableString):
        return
    if not isinstance(elem, Tag):
        return
    n = elem.name
    if n == "h1":
        out.append("\n# " + inline_children(elem).strip() + "\n")
    elif n == "h2":
        out.append("\n## " + inline_children(elem).strip() + "\n")
    elif n == "h3":
        out.append("\n### " + inline_children(elem).strip() + "\n")
    elif n == "h4":
        out.append("\n#### " + inline_children(elem).strip() + "\n")
    elif n == "hr":
        out.append("\n---\n")
    elif n == "table":
        out.append("\n" + table_to_md(elem) + "\n")
    elif n == "ul":
        for li in elem.find_all("li", recursive=False):
            out.append("- " + inline_children(li).strip())
        out.append("")
    elif n == "ol":
        for i, li in enumerate(elem.find_all("li", recursive=False), 1):
            out.append(f"{i}. " + inline_children(li).strip())
        out.append("")
    elif n in ("p", "div"):
        txt = inline_children(elem).strip()
        if txt:
            out.append(txt)
            out.append("")
    else:
        for c in elem.children:
            block(c, out)


def convert(html_path, md_path):
    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    for t in soup(["script", "style"]):
        t.decompose()
    body = soup.body or soup
    out = []
    for c in body.children:
        block(c, out)
    md = "\n".join(out)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    print("converted", html_path, "->", md_path, "chars:", len(md))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert HTML to Markdown")
    parser.add_argument("-i", "--input", required=True, help="input HTML file")
    parser.add_argument("-o", "--output", required=True, help="output Markdown file")
    args = parser.parse_args()
    convert(args.input, args.output)
