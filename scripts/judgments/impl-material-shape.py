"""材料の形（references/impl-material-shape.md）の計算。"""
import ast

from _common import need, problem

REGEX_CALLS = {"compile", "search", "match", "fullmatch", "findall", "finditer", "sub", "subn", "split"}


def _is_constant_pattern(node):
    return isinstance(node, ast.Constant) and isinstance(node.value, (str, bytes))


def judge(m):
    out = []
    for path, text in sorted(need(m, "ファイル").items()):
        if not (path.startswith("scripts/") and path.endswith(".py")):
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError as e:
            problem(out, path, f"Python として読めない（{e.lineno}行目）")
            continue
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr in REGEX_CALLS and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "re" and node.args):
                continue
            if not _is_constant_pattern(node.args[0]):
                problem(out, path, f"{node.lineno}行目：正規表現を、文字列の定数でない値で作っている（語彙を当てはめていないか確かめる）")
    return {"問題": out}
