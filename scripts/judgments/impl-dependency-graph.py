"""依存関係の図（references/impl-dependency-graph.md）の計算。"""
import re

from _common import MissingMaterial, need, section, table_rows, val, words


def judge(m):
    """索引の「依存する判断」から、人に見せる依存関係の図（Mermaid の flowchart）を作る。"""
    name = "impl-dependency-graph"
    files = need(m, "ファイル")
    skill = files.get("SKILL.md")
    if skill is None:
        raise MissingMaterial("ファイル（SKILL.md）")
    header = str(val(name, "図の書き方"))
    line, material_mark = str(val(name, "依存の線")), str(val(name, "材料の印"))
    index_cols = words("logic-skill-shape", "索引の列")
    nc, fc, dc = (index_cols.index(c) for c in ("判断名", "ファイル", "依存する判断"))
    rows = {}
    for row in table_rows(section(skill, "索引", 1)):
        if len(row) <= max(nc, fc, dc):
            continue
        hit = re.search(r"\]\(references/([^)]+\.md)\)", row[fc])
        if not hit:
            continue
        f = hit.group(1)
        used = set()
        for r in table_rows(section(files.get(f"references/{f}") or "", "求める材料")):
            if len(r) > 1 and r[1] == "別の判断":
                used |= {t for t in re.findall(r"\]\(([^)]+\.md)\)", "|".join(r)) if "/" not in t}
        rows[f] = {"判断名": row[nc], "依存": re.findall(r"`([^`]+\.md)`", row[dc]), "材料": used}

    def node(f):
        return "n_" + re.sub(r"[^0-9A-Za-z]", "_", f[:-3])

    lines = [header]
    for f in sorted(rows):
        label = rows[f]["判断名"].replace('"', "'")
        lines.append(f'    {node(f)}["{label}<br/>{f}"]')
    for f in sorted(rows):
        for d in rows[f]["依存"]:
            if d in rows:
                arrow = f"{line}|{material_mark}|" if d in rows[f]["材料"] else line
                lines.append(f"    {node(f)} {arrow} {node(d)}")

    done, visiting, cycle = set(), set(), []

    def visit(f, chain):
        if f in done or cycle:
            return
        if f in visiting:
            cycle.extend(chain[chain.index(f):] + [f])
            return
        visiting.add(f)
        for d in rows[f]["依存"]:
            if d in rows:
                visit(d, chain + [f])
        visiting.discard(f)
        done.add(f)

    for f in sorted(rows):
        visit(f, [])
    return {"図": "\n".join(lines), "循環": cycle}
