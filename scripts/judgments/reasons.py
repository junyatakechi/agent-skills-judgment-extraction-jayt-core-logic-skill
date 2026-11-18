"""理由の書き方（references/reasons.md）の計算。"""
import re

from _common import judgment_files, problem, section, words


def judge(m):
    out = []
    kinds = words("reasons", "理由の種類")
    marks = {k: words("reasons", f"{k}の印") for k in kinds}
    head = re.compile(r"^(?:\d+\.|-) （(%s)）" % "|".join(kinds))
    for path, text in sorted(judgment_files(m).items()):
        body = section(text, "答え方と理由")
        for line in body.splitlines():
            hit = head.match(line.strip())
            if not hit or re.search(r"と同じ。?$", line.strip()):
                continue
            line = line.strip()
            ok = line.endswith("）") and any(f"（{mk}：" in line for mk in marks[hit.group(1)])
            if not ok:
                problem(out, path, f"（{hit.group(1)}）の文末に「{'・'.join(marks[hit.group(1)])}」の印が無い: {line[:40]}")
    return {"問題": out}
