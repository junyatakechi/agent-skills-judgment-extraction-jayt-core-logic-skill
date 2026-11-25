#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""agent-skills-judgment-extraction-jayt-core-logic-skill の計算のエントリポイント。スキルのファイルの本文を材料として受け取り、型を確かめる。

Usage:
  uv run judge.py <判断> <材料.json>

<判断> は references/ のファイル名（拡張子なし）。計算を持つのは、judgments/ に同じ名前の
ファイルがある判断だけ。エントリポイントはこの1本で、失敗の返し方と依存先の読み込みをここと
judgments/_common.py だけが持つ。頼まれた判断と、その依存先のファイルだけを読み込む。
  judgment-file          判断ファイルの形              → JSON（ファイルごとの問題）
  reasons                理由の書き方                  → JSON（ファイルごとの問題）
  sources                出典の書き方                  → JSON（ファイルごとの問題）
  logic-skill-shape      ロジックスキルの型            → JSON（ファイルごとの問題）
  app-skill-shape        アプリケーションスキルの型    → JSON（ファイルごとの問題）
  impl-judgment-details  判断ファイルの細かな書き方    → JSON（ファイルごとの問題）
  impl-example-values    例に使う値                    → JSON（ファイルごとの問題）
  impl-dependency-graph  依存関係の図                  → JSON（Mermaid の flowchart と循環）
  impl-table-links       表のファイル名のリンク        → JSON（ファイルごとの問題）

**型の決まり（章・列・キー・印・定型文）はスクリプトに書かない。** references/<判断>.md の
「## 判断定数」の表と、references/skill-md-sentences.md の定型文を実行時に読む。

材料のJSONは `{"ファイル": {"<スキルのフォルダからのパス>": "<本文>"}, "種類": "..."}`。
ファイルを開くのは呼び出し側で、このスクリプトはスキルの外を読み書きしない。
必須の材料が無ければ {"足りない材料": [...]} を標準出力に出して終了コード2で止まる。
使い方の誤りは標準エラーに出して終了コード1。標準ライブラリだけで動く。
"""
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "judgments"))
from _common import MissingMaterial, available, load  # noqa: E402


def main():
    names = available()
    if len(sys.argv) != 3 or sys.argv[1] not in names:
        sys.exit(f"Usage: judge.py <{'|'.join(names)}> <材料.json>")
    with open(sys.argv[2], encoding="utf-8") as f:
        materials = json.load(f)
    try:
        result = load(sys.argv[1]).judge(materials)
    except MissingMaterial as e:
        print(json.dumps({"足りない材料": [str(e)]}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
