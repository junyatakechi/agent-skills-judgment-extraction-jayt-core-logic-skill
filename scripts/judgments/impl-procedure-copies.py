"""手順の写し（references/impl-procedure-copies.md）の計算。"""
import re
from difflib import SequenceMatcher

from _common import need, problem, section, strip_inline, val, words

NAME = "impl-procedure-copies"
# 「〜は、`J1`に聞く。」のように、IDで指す前に話題を添えた文。コード表記を除いたあとの形で見分ける。
HINT = re.compile(r"^(.*?)は、[・\s]*(に聞く|に従う|に頼む|を参照する)")


def _sentences(text):
    """手順の本文を、文ごとに分ける。表の行・見出し・空行は除く。"""
    out = []
    for line in strip_inline(text).splitlines():
        line = line.strip()
        if not line or line.startswith(("|", "#")):
            continue
        line = re.sub(r"^(\d+\.|-)\s*", "", line)
        out += [s.strip() for s in re.split(r"(?<=。)", line) if s.strip()]
    return out


def _longest(a, b):
    m = SequenceMatcher(None, a, b, autojunk=False).find_longest_match(0, len(a), 0, len(b))
    return a[m.a:m.a + m.size]


def judge(m):
    out = []
    files = need(m, "ファイル")
    steps = section(files.get("SKILL.md") or "", "要求と打ち手", 1)
    answer_len = val(NAME, "判断の答えの写しとみなす長さ")
    allowed = words(NAME, "写しとみなさない言い回し")

    # 答え方1：手順の中に表を置かない
    if any(line.startswith("|") for line in steps.splitlines()):
        problem(out, "SKILL.md", "手順の中に表がある")

    # 答え方2：判断先の答え方を、手順に書き直さない
    answers = {p: strip_inline(section(t, "答え方と理由")) for p, t in (m.get("判断先のファイル") or {}).items()}
    answers.update({p: strip_inline(section(t, "答え方と理由")) for p, t in files.items()
                    if p.startswith("references/") and p.endswith(".md")})
    for s in _sentences(steps):
        hint = HINT.match(s)
        if hint:
            s = s[len(hint.group(1)):]
        for phrase in allowed:
            s = s.replace(phrase, "")
        best = max(((_longest(s, a), p) for p, a in answers.items()), key=lambda x: len(x[0]), default=("", ""))
        if len(best[0]) >= answer_len:
            problem(out, "SKILL.md", f"手順に、{best[1]} の答え方の写し「{best[0]}」がある")
    return {"問題": out}
