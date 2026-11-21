"""表のファイル名のリンク（references/impl-table-links.md）の計算。"""
import posixpath
import re

from _common import need, problem, section, words

NAME = "impl-table-links"
LINK = re.compile(r"^\[([^\]]+)\]\(([^)\s]+)\)$")


def _columns(key):
    """判断定数の「<表>の<列>」の並びを、(表, 列) の並びにする。"""
    return [tuple(w.rsplit("の", 1)) for w in words(NAME, key)]


def _cells(skill, table, column):
    """SKILL.md の「# <表>」の章にある表から、見出しが <列> の列のセルを並べる。"""
    out, idx = [], None
    for line in section(skill, table, 1).splitlines():
        if not line.startswith("|"):
            idx = None if not line.strip() or line.startswith("#") else idx
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if set("".join(cells)) <= set("-: "):
            continue
        if column in cells and idx is None:
            idx = cells.index(column)
            continue
        if idx is not None and idx < len(cells):
            out.append((cells[0], cells[idx]))
    return out


def judge(m):
    out = []
    files = need(m, "ファイル")
    skill = files.get("SKILL.md") or ""
    exts = {posixpath.splitext(p)[1] for p in files}
    for table, column in _columns("リンクにする列"):
        for row_id, cell in _cells(skill, table, column):
            hit = LINK.match(cell)
            if not hit or "://" in hit.group(2):
                problem(out, "SKILL.md", f"{table}の {row_id} の{column}が、相対リンクでない: {cell}")
                continue
            target = posixpath.normpath(hit.group(2))
            if posixpath.splitext(target)[1] in exts and target not in files:
                problem(out, "SKILL.md", f"{table}の {row_id} の{column}のリンク先 {target} が無い")
    for table, column in _columns("リンクにしない列"):
        for row_id, cell in _cells(skill, table, column):
            if re.search(r"\]\([^)]+\)", cell):
                problem(out, "SKILL.md", f"{table}の {row_id} の{column}が、リンクになっている: {cell}")
    return {"問題": out}
