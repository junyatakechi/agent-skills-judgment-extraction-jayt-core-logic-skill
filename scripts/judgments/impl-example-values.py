"""例に使う値（references/impl-example-values.md）の計算。"""
import re

from _common import need, problem, section, strip_code


def judge(m):
    out = []
    files = need(m, "ファイル")
    targets = [str(v) for v in need(m, "対象の値") if str(v).strip()]
    pats = [(v, re.compile(r"(?<![\d.])%s(?![\d])" % re.escape(v)) if re.fullmatch(r"[\d.]+", v) else re.compile(re.escape(v)))
            for v in targets]
    for path, text in sorted(files.items()):
        if not path.endswith(".md"):
            continue
        spots = re.findall(r"```.*?```", text, flags=re.S) + re.findall(r"`[^`\n]*`", strip_code(text))
        if path == "README.md":
            spots.append(section(text, "使い方"))
        for v, pat in pats:
            if any(pat.search(s) for s in spots):
                problem(out, path, f"例（コード表記か README の使い方）に、対象の値「{v}」がある")
    return {"問題": out}
