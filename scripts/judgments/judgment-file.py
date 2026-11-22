"""判断ファイルの形（references/judgment-file.md）の計算。"""
import re

from _common import first_table_header, headings, judgment_files, judgment_frontmatter, problem, section, strip_inline, val, words


def judge(m):
    out = []
    want = words("judgment-file", "判断ファイルの章")
    banned = words("judgment-file", "使わない見出し")
    const_cols = words("judgment-file", "判断定数の表の列")
    material_cols = words("judgment-file", "求める材料の表の列")
    not_answered = val("judgment-file", "答えない問いの言い回し")
    fm_keys = words("judgment-file", "判断ファイルの frontmatter のキー")
    for path, text in sorted(judgment_files(m).items()):
        fm = judgment_frontmatter(text)
        if text.startswith("---\n") and fm is None:
            problem(out, path, "frontmatter が閉じていない")
        if fm is not None:
            extra = [k for k in fm if k not in fm_keys]
            if extra:
                problem(out, path, f"frontmatter に、決まりの外のキー「{'・'.join(extra)}」がある")
            if not any(fm.get(k) for k in fm_keys):
                problem(out, path, "frontmatter に出典が無い。出典が無ければ frontmatter を置かない")
        h2 = headings(text, 2)
        if h2 != want:
            problem(out, path, f"章が「{'・'.join(h2)}」。決まりは「{'・'.join(want)}」")
        for b in banned:
            if b in h2:
                problem(out, path, f"使わない見出し「## {b}」がある")
        body = section(text, "答え方と理由")
        nums = re.findall(r"^### (\d+)\. ", body, re.M)
        if not nums or nums[0] != "0" or "### 0. 判断全体" not in body:
            problem(out, path, "「### 0. 判断全体」から始まっていない")
        if nums != [str(i) for i in range(len(nums))]:
            problem(out, path, f"答え方の番号が {', '.join(nums)}。0から順に振る")
        for part in re.split(r"^### ", body, flags=re.M)[1:]:
            if not part.startswith("0. ") and not_answered in strip_inline(part):
                problem(out, path, f"「{not_answered}」が「0. 判断全体」の外（### {part.splitlines()[0]}）にある")
        for title, cols in (("判断定数", const_cols), ("求める材料", material_cols)):
            sec = section(text, title)
            header = first_table_header(sec)
            if header is not None and header != cols:
                problem(out, path, f"「{title}」の表の列が「{'・'.join(header)}」。決まりは「{'・'.join(cols)}」")
            if header is None and not sec.startswith("なし"):
                problem(out, path, f"「{title}」に表も「なし」も無い")
        undecided = section(text, "未決")
        ids = re.findall(r"^- (U\d+)", undecided, re.M)
        for ref in sorted(set(re.findall(r"（未決 (U\d+)）", strip_inline(text)))):
            if ref not in ids:
                problem(out, path, f"（未決 {ref}）が指す項目が「未決」に無い")
        if not ids and not undecided.startswith("なし"):
            problem(out, path, "「未決」に項目も「なし」も無い")
    return {"問題": out}
