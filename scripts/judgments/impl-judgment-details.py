"""判断ファイルの細かな書き方（references/impl-judgment-details.md）の計算。"""
import posixpath
import re

from _common import judgment_files, need, problem, section, strip_inline, val, words


def judge(m):
    out = []
    sep = val("impl-judgment-details", "未決のIDの区切り")
    ending = val("impl-judgment-details", "ほかの理由を指す項目の結び")
    kinds = words("reasons", "理由の種類")
    typed = re.compile(r"^(?:\d+\.|-) （(%s)）" % "|".join(kinds))
    for path, text in sorted(judgment_files(m).items()):
        for line in section(text, "未決").splitlines():
            hit = re.match(r"^- (U\d+)(.?)", line.strip())
            if hit and hit.group(2) != sep:
                problem(out, path, f"未決 {hit.group(1)} のIDの後ろが「{sep}」でない")
        for line in section(text, "答え方と理由").splitlines():
            line = line.strip()
            if typed.match(line) and line.endswith(ending):
                problem(out, path, f"ほかの理由を指すだけの項目に種類が付いている: {line[:40]}")
    files = need(m, "ファイル")
    for path, text in sorted(files.items()):
        if not path.endswith(".md"):
            continue
        for link in re.findall(r"\]\(([^)\s#]+\.md)(?:#[^)]*)?\)", strip_inline(text)):
            if "://" in link:
                continue
            target = posixpath.normpath(posixpath.join(posixpath.dirname(path), link))
            if target not in files:
                problem(out, path, f"リンク先が無い: {link}")
    return {"問題": out}
