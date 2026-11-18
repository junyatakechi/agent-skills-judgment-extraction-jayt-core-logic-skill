"""アプリケーションスキルの型（references/app-skill-shape.md）の計算。"""
import re

from _common import common_shape, judgment_files, problem, section, table_rows, templates, val


def judge(m):
    out = []
    rules = templates()["app"]
    count = val("app-skill-shape", "アプリケーションスキルの定型文の項目数")
    files, skill = common_shape(m, out, "app", ("app-skill-shape", "アプリケーションスキルの章"),
                                 ("app-skill-shape", "アプリケーションスキルの metadata"), count, rules)
    steps = section(skill, "手順", 1)
    tables = ["中核判断の委任表", "まだ切り出していない判断の表", "一般的な業務知識の参照表", "外部手順の依頼表", "取り決めの表"]
    for t in tables:
        for row in table_rows(section(skill, t, 1)):
            if row and re.match(r"^[JGRC]\d+$", row[0]) and f"`{row[0]}`" not in steps:
                problem(out, "SKILL.md", f"{t}の {row[0]} が手順から指されていない")
    listed = {r[2].strip("`") for r in table_rows(section(skill, "まだ切り出していない判断の表", 1)) if len(r) > 2}
    present = {p.split("/", 1)[1] for p in judgment_files(m)}
    for f in sorted(listed - present):
        problem(out, "SKILL.md", f"まだ切り出していない判断の表の {f} が references/ に無い")
    for f in sorted(present - listed):
        problem(out, f"references/{f}", "まだ切り出していない判断の表に無い")
    return {"問題": out}
