"""DBに置いた値の見分け方（references/impl-db-values.md）の計算。"""
import re

from _common import need, words

NAME = "impl-db-values"
KEY = re.compile(r"^`([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+|[A-Z]{3,})`$")
ENV_SOURCES = re.compile(r"EnvDataSources\(\s*\"[^\"]*\"\s*,\s*\((.*?)\)", re.S)


def _from_conventions(files):
    """取り決めファイルの表の行のうち、キーを持つ行。キーが先頭なら次の列、そうでなければ先頭の列を名前にする。"""
    out = []
    for path, text in files.items():
        if not (path.startswith("conventions/") and path.endswith(".md")):
            continue
        for line in text.splitlines():
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            for i, c in enumerate(cells):
                m = KEY.match(c)
                if m:
                    name = cells[1] if i == 0 and len(cells) > 1 else cells[0]
                    out.append({"ファイル": path, "キー": m.group(1), "名前": name})
                    break
    return out


def _from_scripts(files):
    out = []
    for path, text in files.items():
        if not (path.startswith("scripts/") and path.endswith(".py")):
            continue
        for body in ENV_SOURCES.findall(text):
            for key in re.findall(r"\"([a-z0-9_]+)\"", re.sub(r"#[^\n]*", "", body)):
                out.append({"ファイル": path, "キー": key.upper(), "名前": ""})
    return out


def judge(m):
    files = need(m, "ファイル")
    name_words = words(NAME, "判断や取り決めを疑うDBの名前の語")
    key_words = words(NAME, "判断や取り決めを疑うキーの語")
    dbs = {}
    read = {db["キー"] for db in _from_scripts(files)}
    for db in _from_conventions(files) + _from_scripts(files):
        # 接頭辞つきのキー（CONDITION_EVAL_DB_X_URL）と、接頭辞を除いたキー（X）を同じDBとして扱う
        short = re.sub(r"^.*_DB_|_URL$", "", db["キー"])
        # 取り決めの表の行は、スクリプトが読むキーか、.env の URL のキーのときだけDBとみなす（列名の表を拾わない）
        if db["名前"] and short not in read and not db["キー"].endswith("_URL"):
            continue
        cur = dbs.setdefault(short, {"ファイル": db["ファイル"], "キー": short, "名前": ""})
        if db["名前"] and not cur["名前"]:
            cur.update(ファイル=db["ファイル"], 名前=db["名前"])
    check, other = [], []
    for db in dbs.values():
        tokens = db["キー"].lower().split("_")
        hit = [w for w in name_words if w in db["名前"]] + [w for w in key_words if w in tokens]
        (check if hit else other).append({**db, "当たった語": hit} if hit else db)
    return {"確かめるDB": check, "そのほかのDB": other}
