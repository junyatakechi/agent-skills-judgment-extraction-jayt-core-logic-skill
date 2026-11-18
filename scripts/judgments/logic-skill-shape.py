"""ロジックスキルの型（references/logic-skill-shape.md）の計算。"""
import re

from _common import (MissingMaterial, common_shape, first_table_header, judgment_files, need, problem,
                     section, table_rows, templates, val, words)


def judge(m):
    out = []
    kind = need(m, "種類")
    if kind not in ("core-logic", "generic-logic"):
        raise MissingMaterial("種類（core-logic か generic-logic）")
    rules = templates()["logic"]
    rules = [r.replace("（一般的な業務知識だけ）", "") for r in rules]
    count = val("logic-skill-shape", f"{kind} の定型文の項目数")
    files, skill = common_shape(m, out, kind, ("logic-skill-shape", f"{kind} の章"),
                                 ("logic-skill-shape", f"{kind} の metadata"), count, rules)
    index = section(skill, "索引", 1)
    header = first_table_header(index)
    cols = words("logic-skill-shape", "索引の列")
    if header != cols:
        problem(out, "SKILL.md", f"索引の列が「{'・'.join(header or [])}」。決まりは「{'・'.join(cols)}」")
    linked = set(re.findall(r"\]\(references/([^)]+\.md)\)", index))
    present = {p.split("/", 1)[1] for p in judgment_files(m)}
    for f in sorted(linked - present):
        problem(out, "SKILL.md", f"索引の {f} が references/ に無い")
    for f in sorted(present - linked):
        problem(out, f"references/{f}", "索引に無い")
    _check_dependencies(out, files, index, cols, present)
    return {"問題": out}


def _check_dependencies(out, files, index, cols, present):
    """索引の「依存する判断」（ファイル名）と、求める材料の「別の判断」の行を照らす。
    材料の行にある依存は、索引の列にすべて載っていなければならない（材料→索引の一方向）。"""
    if "ファイル" not in cols or "依存する判断" not in cols:
        return
    file_col, dep_col = cols.index("ファイル"), cols.index("依存する判断")
    for row in table_rows(index):
        if len(row) <= max(file_col, dep_col):
            continue
        hit = re.search(r"\]\(references/([^)]+\.md)\)", row[file_col])
        if not hit:
            continue
        name = hit.group(1)
        deps = set(re.findall(r"`([^`]+\.md)`", row[dep_col]))
        if row[dep_col] not in ("—", "") and not deps:
            problem(out, "SKILL.md", f"索引の {name} の依存する判断が、ファイル名で書かれていない")
        for d in sorted(deps - present):
            problem(out, "SKILL.md", f"索引の {name} の依存する判断 {d} が references/ に無い")
        body = files.get(f"references/{name}")
        if body is None:
            continue
        used = set()
        for r in table_rows(section(body, "求める材料")):
            if len(r) < 2 or r[1] != "別の判断":
                continue
            for text, target in re.findall(r"\[([^\]]+)\]\(([^)]+\.md)\)", "|".join(r)):
                if "/" in target:
                    continue
                used.add(target)
                if text != target:
                    problem(out, f"references/{name}", f"求める材料の別の判断のリンク「{text}」の表示が、ファイル名 {target} でない")
        for d in sorted(used - deps):
            problem(out, f"references/{name}", f"求める材料の別の判断 {d} が、索引の依存する判断に無い")
