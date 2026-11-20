"""アプリケーションスキルの型（references/app-skill-shape.md）の計算。"""
import re

from _common import (common_shape, headings, judgment_files, problem, section, strip_code, table_rows,
                     templates, val, words)

NAME = "app-skill-shape"
CHAPTER = "要求と打ち手"


def _is_request(heading, ends):
    """見出しが【要求の文末】のどれかで終わるか（答え方4）。番号と句点は除く。"""
    text = re.sub(r"^\d+\.\s*", "", heading).rstrip("。 　")
    return any(text.endswith(e) for e in ends)


def _check_requests(body, out):
    """「要求と打ち手」の ## が、要求か、最後の1つだけの記録と報告かと、要求の下の打ち手（答え方4・6）。"""
    ends = words(NAME, "要求の文末")
    h2 = headings(body, 2)
    requests = [h for h in h2 if _is_request(h, ends)]
    others = [i for i, h in enumerate(h2) if not _is_request(h, ends)]
    if not requests:
        problem(out, "SKILL.md", f"「{CHAPTER}」に、要求の ## が無い")
    if len(others) > 1 or (others and others[0] != len(h2) - 1):
        names = "・".join(h2[i] for i in others)
        problem(out, "SKILL.md", f"「{CHAPTER}」の ## のうち、要求でない節（{names}）は最後の1つだけにする")
    for h in requests:
        if not headings(section(body, h, 2), 3):
            problem(out, "SKILL.md", f"要求「{h}」の下に、### の打ち手が無い")


def judge(m):
    out = []
    rules = templates()["app"]
    count = val(NAME, "アプリケーションスキルの定型文の項目数")
    files, skill = common_shape(m, out, "app", (NAME, "アプリケーションスキルの章"),
                                 (NAME, "アプリケーションスキルの metadata"), count, rules)
    body = section(skill, CHAPTER, 1)
    _check_requests(body, out)
    if "→ 要件" in strip_code(skill):
        problem(out, "SKILL.md", "要件を番号で指す所（→ 要件）が残っている")
    tables = ["中核判断の委任表", "まだ切り出していない判断の表", "一般的な業務知識の参照表", "外部手順の依頼表", "取り決めの表"]
    for t in tables:
        for row in table_rows(section(skill, t, 1)):
            if row and re.match(r"^[JGRC]\d+$", row[0]) and f"`{row[0]}`" not in body:
                problem(out, "SKILL.md", f"{t}の {row[0]} が手順から指されていない")
    listed = {r[2].strip("`") for r in table_rows(section(skill, "まだ切り出していない判断の表", 1)) if len(r) > 2}
    present = {p.split("/", 1)[1] for p in judgment_files(m)}
    for f in sorted(listed - present):
        problem(out, "SKILL.md", f"まだ切り出していない判断の表の {f} が references/ に無い")
    for f in sorted(present - listed):
        problem(out, f"references/{f}", "まだ切り出していない判断の表に無い")
    return {"問題": out}
