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

**型の決まり（章・列・キー・印・定型文）はこのスクリプトに書かない。** references/<判断>.md の
「## 判断定数」の表と、references/skill-md-sentences.md の定型文を実行時に読む。

材料のJSONは `{"ファイル": {"<スキルのフォルダからのパス>": "<本文>"}, "種類": "..."}`。
ファイルを開くのは呼び出し側で、このスクリプトはスキルの外を読み書きしない。
必須の材料が無ければ {"足りない材料": [...]} を標準出力に出して終了コード2で止まる。
使い方の誤りは標準エラーに出して終了コード1。標準ライブラリだけで動く。
"""
import json
import os
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
    return {"問題": out}


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


JUDGMENTS = {
    "judgment-file": judge_judgment_file,
    "reasons": judge_reasons,
    "logic-skill-shape": judge_logic_skill_shape,
    "app-skill-shape": judge_app_skill_shape,
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
