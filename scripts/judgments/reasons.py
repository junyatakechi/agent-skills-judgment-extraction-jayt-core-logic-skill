"""理由の書き方（references/reasons.md）の計算。"""
import re

from _common import judgment_files, judgment_frontmatter, problem, section, strip_inline, val, words


def judge(m):
    out = []
    kinds = words("reasons", "理由の種類")
    marks = {k: words("reasons", f"{k}の印") for k in kinds}
    head = re.compile(r"^(?:\d+\.|-) （(%s)）" % "|".join(kinds))
    top = val("reasons", "出典を置くキー")
    src_keys = words("reasons", "出典のキー")
    must = words("reasons", "省かない出典のキー")
    for path, text in sorted(judgment_files(m).items()):
        sources = (judgment_frontmatter(text) or {}).get(top, {})
        used = set()
        for ref in re.findall(r"（出典：([^）]*)）", strip_inline(text)):
            ref = ref.strip()
            if ref == "なし":
                continue
            ids = [x.strip() for x in ref.split(",")]
            bad = [x for x in ids if not re.fullmatch(r"S\d+", x) or x not in sources]
            if bad:
                problem(out, path, f"（出典：{ref[:40]}）が、frontmatter の {top} に定義したIDで書かれていない")
            used.update(ids)
        for sid, src in sources.items():
            for k in must:
                if not src.get(k):
                    problem(out, path, f"出典 {sid} に「{k}」が無い")
            extra = [k for k in src if k not in src_keys]
            if extra:
                problem(out, path, f"出典 {sid} に、決まりの外のキー「{'・'.join(extra)}」がある")
            if sid not in used:
                problem(out, path, f"出典 {sid} が、どの理由からも指されていない")
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
