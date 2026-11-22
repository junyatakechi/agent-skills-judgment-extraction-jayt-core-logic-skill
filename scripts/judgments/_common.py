"""agent-skills-judgment-extraction-jayt-core-logic-skill の計算の共通の部品。

足りない材料の返し方（MissingMaterial・need）、判断定数の読み方（values・val・words）、
本文の読み方（見出し・節・表）、依存先の読み込み（load）を、すべての判断の計算がここから使う。
判断ごとの計算は judgments/<判断>.py に置き、名前を references/<判断>.md とそろえる。
"""
import importlib.util
import os
import re

JUDGMENTS_DIR = os.path.dirname(os.path.abspath(__file__))
REF_DIR = os.path.normpath(os.path.join(JUDGMENTS_DIR, "..", "..", "references"))


class MissingMaterial(Exception):
    """必須の材料が無い。呼び出し側に、何が足りないかを返す。"""


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


def judgment_frontmatter(text):
    """判断ファイルの先頭の frontmatter を {最上位のキー: {ID: {キー: 値}}} で返す。無ければ None。

    判断ファイルの frontmatter は、出典を `sources:` → `  S1:` → `    name: "..."` の決まった形で持つ。
    YAMLの全体は読まず、この形だけを標準ライブラリで読む。
    """
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 3)
    if end == -1:
        return None
    out, top, item = {}, None, None
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        m = re.match(r"^([A-Za-z_-]+):\s*$", line)
        if m:
            top, item = m.group(1), None
            out[top] = {}
            continue
        m = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line)
        if m and top is not None:
            item = m.group(1)
            out[top][item] = {}
            continue
        m = re.match(r'^    ([A-Za-z_-]+):\s*"(.*)"\s*$', line)
        if m and top is not None and item is not None:
            out[top][item][m.group(1)] = m.group(2).replace('\\"', '"').replace("\\\\", "\\")
    return out


def problem(out, path, msg):
    out.append({"ファイル": path, "内容": msg})


def judgment_files(m):
    files = need(m, "ファイル")
    return {p: t for p, t in files.items() if p.startswith("references/") and p.endswith(".md")}


def common_shape(m, out, kind, chapter_key, meta_key, rule_count, rules):
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
        want_rh = words("readme-contents", "README の章")
        if rh != want_rh:
            problem(out, "README.md", f"章が「{'・'.join(rh)}」。決まりは「{'・'.join(want_rh)}」")
    return files, skill


# --- 依存先の読み込み -------------------------------------------------------------
_loaded = {}


def available():
    """計算を持つ判断の名前（judgments/ のファイル名から拡張子を除いたもの）。"""
    return sorted(f[:-3] for f in os.listdir(JUDGMENTS_DIR) if f.endswith(".py") and not f.startswith("_"))


def load(name):
    """judgments/<name>.py を読み込む。頼まれた判断と、その依存先だけを読む。"""
    if name not in _loaded:
        path = os.path.join(JUDGMENTS_DIR, f"{name}.py")
        spec = importlib.util.spec_from_file_location(f"judgment_{name.replace('-', '_')}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _loaded[name] = module
    return _loaded[name]
