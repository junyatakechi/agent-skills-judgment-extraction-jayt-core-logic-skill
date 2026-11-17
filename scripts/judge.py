#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""ai-skill-design-jayt-core-logic-skill の計算。スキルのファイルの本文を材料として受け取り、型を確かめる。

Usage:
  uv run judge.py <判断> <材料.json>

<判断> は references/ のファイル名（拡張子なし）。計算を持つのは次の判断だけ。
  judgment-file      判断ファイルの形              → JSON（ファイルごとの問題）
  reasons            理由の書き方                  → JSON（ファイルごとの問題）
  logic-skill-shape  ロジックスキルの型            → JSON（ファイルごとの問題）
  app-skill-shape    アプリケーションスキルの型    → JSON（ファイルごとの問題）
  impl-judgment-details  判断ファイルの細かな書き方  → JSON（ファイルごとの問題）
  impl-example-values    例に使う値                  → JSON（ファイルごとの問題）

**型の決まり（章・列・キー・印・定型文）はこのスクリプトに書かない。** references/<判断>.md の
「## 判断定数」の表と、references/skill-md-sentences.md の定型文を実行時に読む。

材料のJSONは `{"ファイル": {"<スキルのフォルダからのパス>": "<本文>"}, "種類": "..."}`。
ファイルを開くのは呼び出し側で、このスクリプトはスキルの外を読み書きしない。
必須の材料が無ければ {"足りない材料": [...]} を標準出力に出して終了コード2で止まる。
使い方の誤りは標準エラーに出して終了コード1。標準ライブラリだけで動く。
"""
import json
import os
import posixpath
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REF_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references"))


class MissingMaterial(Exception):
    """必須の材料が無い。呼び出し側に、何が足りないかを返す。"""


# --- 判断定数の表 ---------------------------------------------------------------
_values = {}


def values(name):
    """references/<name>.md の「## 判断定数」の表（| 名前 | 値 | 単位 | 理由 |）を {名前: 値} で返す。"""
    if name in _values:
        return _values[name]
    out, in_section = {}, False
    with open(os.path.join(REF_DIR, f"{name}.md"), encoding="utf-8") as f:
        for line in f:
            if line.startswith("## "):
                in_section = line.strip() == "## 判断定数"
                continue
            if not in_section or not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells[0] == "名前" or set(cells[0]) <= set("-: "):
                continue
            out[cells[0]] = int(cells[1]) if cells[1].isdigit() else cells[1]
    _values[name] = out
    return out


def val(name, key):
    v = values(name)
    if key not in v:
        raise KeyError(f"references/{name}.md の「## 判断定数」の表に「{key}」が無い")
    return v[key]


def words(name, key):
    """判断定数の表の「、」区切りの語の並び。"""
    return [w.strip() for w in str(val(name, key)).split("、") if w.strip()]


def templates():
    """references/skill-md-sentences.md の定型文を {"app": [...], "logic": [...]} で返す（1項目1行）。"""
    text = open(os.path.join(REF_DIR, "skill-md-sentences.md"), encoding="utf-8").read()
    out = {}
    for key, label in (("app", "アプリケーションスキルの定型文："), ("logic", "ロジックスキルの定型文：")):
        block = text.split(label, 1)[1].split("```markdown", 1)[1].split("```", 1)[0]
        out[key] = [line.strip() for line in block.strip().splitlines() if line.strip()]
    return out


# --- 本文の読み方 ---------------------------------------------------------------
def need(m, key):
    if m.get(key) is None:
        raise MissingMaterial(key)
    return m[key]


def strip_code(text):
    """コードブロックを除いた本文。見出しを数えるときに使う。"""
    return re.sub(r"```.*?```", "", text, flags=re.S)


def strip_inline(text):
    """コードブロックとコード表記を除いた本文。指しを数えるときに使う（例として書いた所を数えない）。"""
    return re.sub(r"`[^`\n]*`", "", strip_code(text))


def headings(text, level):
    mark = "#" * level + " "
    return [line[len(mark):].strip() for line in strip_code(text).splitlines() if line.startswith(mark)]


def section(text, title, level=2):
    """「## title」から、同じ深さ以上の次の見出しまでの本文。"""
    mark = "#" * level + " "
    lines, out, inside = strip_code(text).splitlines(), [], False
    for line in lines:
        if re.match(r"^#{1,%d} " % level, line):
            if inside:
                break
            inside = line.strip() == mark + title
            continue
        if inside:
            out.append(line)
    return "\n".join(out).strip()


def first_table_header(body):
    for line in body.splitlines():
        if line.startswith("|"):
            return [c.strip() for c in line.strip().strip("|").split("|")]
    return None


def table_rows(body):
    rows = []
    for line in body.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if set("".join(cells)) <= set("-: "):
            continue
        rows.append(cells)
    return rows[1:]


def frontmatter_metadata(text):
    parts = text.split("---")
    if len(parts) < 3 or not text.startswith("---"):
        return None
    keys, in_meta = [], False
    for line in parts[1].splitlines():
        if line.startswith("metadata:"):
            in_meta = True
            continue
        if in_meta:
            m = re.match(r"^  ([A-Za-z-]+):", line)
            if m:
                keys.append(m.group(1))
            elif line and not line.startswith(" "):
                in_meta = False
    return keys


def problem(out, path, msg):
    out.append({"ファイル": path, "内容": msg})


def judgment_files(m):
    files = need(m, "ファイル")
    return {p: t for p, t in files.items() if p.startswith("references/") and p.endswith(".md")}


# --- 判断ごとの計算 -------------------------------------------------------------
def judge_judgment_file(m):
    out = []
    want = words("judgment-file", "判断ファイルの章")
    banned = words("judgment-file", "使わない見出し")
    const_cols = words("judgment-file", "判断定数の表の列")
    material_cols = words("judgment-file", "求める材料の表の列")
    not_answered = val("judgment-file", "答えない問いの言い回し")
    for path, text in sorted(judgment_files(m).items()):
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


def judge_reasons(m):
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


def _common_shape(m, out, kind, chapter_key, meta_key, rule_count, rules):
    files = need(m, "ファイル")
    skill = files.get("SKILL.md")
    if skill is None:
        raise MissingMaterial("ファイル.SKILL.md")
    for f in ("README.md", "LICENSE"):
        if f not in files:
            problem(out, f, "無い")
    meta = frontmatter_metadata(skill)
    want_meta = words(*meta_key)
    if meta is None:
        problem(out, "SKILL.md", "frontmatter が無い")
    else:
        if sorted(meta) != sorted(want_meta):
            problem(out, "SKILL.md", f"metadata のキーが「{'・'.join(meta)}」。決まりは「{'・'.join(want_meta)}」")
    h1 = headings(skill, 1)
    want_h1 = words(*chapter_key)
    if h1 != want_h1:
        problem(out, "SKILL.md", f"章が「{'・'.join(h1)}」。決まりは「{'・'.join(want_h1)}」")
    got = [l.strip() for l in section(skill, "このスキルの設計上の決まりごと", 1).splitlines() if l.strip()]
    if len(got) != rule_count or got != rules[:rule_count]:
        problem(out, "SKILL.md", "「このスキルの設計上の決まりごと」が定型文と同じでない")
    readme = files.get("README.md")
    if readme is not None:
        rh = headings(readme, 2)
        want_rh = words("readme", "README の章")
        if rh != want_rh:
            problem(out, "README.md", f"章が「{'・'.join(rh)}」。決まりは「{'・'.join(want_rh)}」")
    return files, skill


def judge_logic_skill_shape(m):
    out = []
    kind = need(m, "種類")
    if kind not in ("core-logic", "generic-logic"):
        raise MissingMaterial("種類（core-logic か generic-logic）")
    rules = templates()["logic"]
    rules = [r.replace("（一般的な業務知識だけ）", "") for r in rules]
    count = val("logic-skill-shape", f"{kind} の定型文の項目数")
    files, skill = _common_shape(m, out, kind, ("logic-skill-shape", f"{kind} の章"),
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


def judge_app_skill_shape(m):
    out = []
    rules = templates()["app"]
    count = val("app-skill-shape", "アプリケーションスキルの定型文の項目数")
    files, skill = _common_shape(m, out, "app", ("app-skill-shape", "アプリケーションスキルの章"),
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


def judge_impl_judgment_details(m):
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


def judge_impl_example_values(m):
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


JUDGMENTS = {
    "judgment-file": judge_judgment_file,
    "reasons": judge_reasons,
    "logic-skill-shape": judge_logic_skill_shape,
    "app-skill-shape": judge_app_skill_shape,
    "impl-judgment-details": judge_impl_judgment_details,
    "impl-example-values": judge_impl_example_values,
}


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in JUDGMENTS:
        sys.exit(f"Usage: judge.py <{'|'.join(JUDGMENTS)}> <材料.json>")
    with open(sys.argv[2], encoding="utf-8") as f:
        materials = json.load(f)
    try:
        result = JUDGMENTS[sys.argv[1]](materials)
    except MissingMaterial as e:
        print(json.dumps({"足りない材料": [str(e)]}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
