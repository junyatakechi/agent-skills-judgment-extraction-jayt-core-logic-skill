---
name: agent-skills-judgment-extraction-jayt-core-logic-skill
description: "文脈: 人の判断を切り出すAgent Skillsの設計。種類: 中核判断。使う場面: 名前で指名されたときだけ使い、会話の内容からは選ばない。"
metadata:
  skill-version: "0.31.1"
  design-name: "人の判断を切り出すAgent Skillsの設計"
  design-version: "7.0.2"
  design-url: "https://zenn.dev/jayt/articles/agent-skills-judgment-extraction"
---

# 索引

| 判断名 | 扱うこと | ファイル | 依存する判断 | 計算 |
|---|---|---|---|---|
| 判断の出所 | このスキルに判断を足す・直すとき、設計文書を写す判断か実装の判断かをどう見分け、それぞれをどう書き、どう直すか | [judgment-origin.md](references/judgment-origin.md) | — | — |
| スキルの種類 | スキルを作るとき・判断を切り出すとき、ロジックスキルとアプリケーションスキルのどちらにし、core-logic と generic-logic のどちらにするか | [skill-kinds.md](references/skill-kinds.md) | — | — |
| 判断の移し替え | 齟齬が見つかったとき・判断を別のスキルへ移すとき、どこへ切り出し、表とIDをどう直すか | [judgment-migration.md](references/judgment-migration.md) | `skill-kinds.md` | — |
| 文脈と種類の見分け方 | 判断をスキルへ振り分けるとき・スキルを分ける・まとめるとき、文脈を何で切り、core-logic と generic-logic を何で見分けるか | [impl-context-and-kind.md](references/impl-context-and-kind.md) | `skill-kinds.md` | — |
| 道具の種類 | 道具を作るとき、判断に使う道具と手続きに使う道具のどちらにし、どのスキルに置くか | [tool-kinds.md](references/tool-kinds.md) | `skill-kinds.md` | — |
| 値の置き場所 | 値を書くとき、ロジックスキル・取り決めファイル・`.env`・材料のどこに置くか | [value-placement.md](references/value-placement.md) | — | — |
| 名前 | スキルに名前を付けるとき、どの形にし、作成者を入れ、アプリケーションスキルの動詞と対象をどう選ぶか | [naming.md](references/naming.md) | `skill-kinds.md` | — |
| README | README を書くとき、どの章に何を書き、何を書かないか | [readme-contents.md](references/readme-contents.md) | `skill-kinds.md` | — |
| README に書かない読み込ませ方 | README のセットアップと使い方を書くとき、スキルを会話の最初に読み込ませる設定を書くか | [impl-readme-loading.md](references/impl-readme-loading.md) | `readme-contents.md`・`description.md` | — |
| README に書く Codex での使い方 | README を書くとき、Claude Code のほかに Codex での使い方を書くか、書くならどの章にどう書くか | [impl-readme-codex.md](references/impl-readme-codex.md) | `readme-contents.md` | — |
| description | description を書くとき、何をどの形で書くか | [description.md](references/description.md) | — | — |
| SKILL.md に入れる文 | SKILL.md に文を足すとき、入れるか、どの定型文を写し、frontmatter に何を書くか | [skill-md-sentences.md](references/skill-md-sentences.md) | `skill-kinds.md` | — |
| 判断ファイルの形 | 判断ファイルを書く・直すとき、章をどう並べ、答え方・判断定数・未決・求める材料をどう書くか | [judgment-file.md](references/judgment-file.md) | `value-placement.md` | ○ |
| 理由の書き方 | 判断ファイルに理由を書くとき、種類をどう選び、文末の印をどう付けるか | [reasons.md](references/reasons.md) | — | ○ |
| 出典の書き方 | 判断ファイルに知見の出典を書くとき、frontmatter に何をどう書き、理由からどう指すか | [sources.md](references/sources.md) | `reasons.md` | ○ |
| ロジックスキルの型 | ロジックスキルの SKILL.md を書くとき、どの章を置き、索引をどう書くか | [logic-skill-shape.md](references/logic-skill-shape.md) | `judgment-file.md` | ○ |
| 判断に使う道具の作り方 | `judge.py` を作る・直すとき、呼び方・失敗の返し方・判断定数の読み方をどうするか | [judge-tool.md](references/judge-tool.md) | `tool-kinds.md`・`value-placement.md` | — |
| ロジックスキルに書かないもの | ロジックスキルに書くとき、何を書かないか | [logic-exclusions.md](references/logic-exclusions.md) | `value-placement.md` | — |
| ロジックスキルとアプリの境目 | ロジックスキルの判断ファイルを書く・見直すとき、アプリケーションスキルに置くべき決まりが混ざっていないかを、どう見分け、どこへ移すか | [impl-logic-app-boundary.md](references/impl-logic-app-boundary.md) | `logic-exclusions.md`・`conventions.md`・`dependencies.md` | — |
| アプリケーションスキルの型 | アプリケーションスキルの SKILL.md を書くとき、どの章を置き、目的・要求・打ち手をどう書くか | [app-skill-shape.md](references/app-skill-shape.md) | — | ○ |
| 5つの表 | 委任表・まだ切り出していない判断の表・参照表・依頼表・取り決めの表を書くとき、列とIDと見出しをどう書くか | [app-tables.md](references/app-tables.md) | `judgment-migration.md` | — |
| 依存の宣言とバージョン | 依存するスキルを書くとき・判断ファイルを変えたとき、バージョンの範囲とバージョンをどう上げるか | [dependencies.md](references/dependencies.md) | — | — |
| 取り決めファイル | 取り決めファイルを書くとき、何を書き、判断ファイルとどう分けるか | [conventions.md](references/conventions.md) | `value-placement.md` | — |
| 旧形式からの移し替え | 旧形式の判断ファイルや SKILL.md を今の型に移すとき、型に無い項目をどこへ移すか | [impl-legacy-migration.md](references/impl-legacy-migration.md) | `judgment-file.md`・`impl-procedure-copies.md`・`app-skill-shape.md` | — |
| 判断ファイルの細かな書き方 | 判断ファイルを書くとき、実測の印の欠け・未決のIDの区切り・ほかの理由を指す項目・リンクをどう書くか | [impl-judgment-details.md](references/impl-judgment-details.md) | `reasons.md` | ○ |
| 例に使う値 | 求める材料の形・README の頼み方・計算の例を書くとき、どの値を使うか | [impl-example-values.md](references/impl-example-values.md) | `logic-exclusions.md` | ○ |
| 設定の不足の判断 | 一般的な業務知識のスキルを作る・直すとき、設定の不足の判断を足すか | [impl-missing-setup.md](references/impl-missing-setup.md) | `tool-kinds.md` | — |
| 形だけ直したときのバージョン | 中身を変えずに形だけを直したとき、バージョンをどう上げるか | [impl-version-bump.md](references/impl-version-bump.md) | `dependencies.md` | — |
| 表のファイル名のリンク | アプリケーションスキルの SKILL.md の表にファイル名を書くとき、リンクにするか | [impl-table-links.md](references/impl-table-links.md) | `app-tables.md` | ○ |
| 出力の様式の指し方 | アプリケーションスキルの手順で、出力の様式の取り決めを、どの節から指すか | [impl-output-format-reference.md](references/impl-output-format-reference.md) | `app-skill-shape.md` | — |
| 目的と要求の言葉 | アプリケーションスキルの目的と要求を書くとき、誰の言葉で決め、AIエージェントが出した案をどう扱うか | [impl-purpose-wording.md](references/impl-purpose-wording.md) | `app-skill-shape.md` | — |
| 材料の形 | ロジックスキルの材料を決めるとき、どこまでをアプリケーションスキルで作り、どこからをロジックスキルに任せるか | [impl-material-shape.md](references/impl-material-shape.md) | `skill-kinds.md`・`value-placement.md` | ○ |
| 中核判断どうしの移し替え | 判断を、別の中核判断のスキルへ移すとき、何を一緒に移し、何を書き換えるか | [impl-core-logic-move.md](references/impl-core-logic-move.md) | `judgment-migration.md` | — |
| 判断の削除 | 判断を削除するとき、何を確かめ、何を一緒に直すか | [impl-judgment-removal.md](references/impl-judgment-removal.md) | `judgment-migration.md` | — |
| 答え方の削除 | 判断ファイルの答え方を1つ消すように頼まれたとき、消すか、「〜しない」に置き換えるか、番号をどうするか | [impl-answer-removal.md](references/impl-answer-removal.md) | `judgment-file.md` | — |
| 使われなくなった .env のキー | スキルを直して `.env` のキーを使わなくなったとき、そのキーをどうするか | [impl-unused-env-keys.md](references/impl-unused-env-keys.md) | `value-placement.md` | — |
| 書き替えたあとの確かめ方 | スキルを作った・直したあと、何で確かめるか | [impl-verification.md](references/impl-verification.md) | `judgment-file.md`・`reasons.md`・`sources.md`・`logic-skill-shape.md`・`app-skill-shape.md`・`impl-judgment-details.md`・`impl-example-values.md`・`impl-procedure-copies.md`・`impl-material-shape.md`・`impl-db-values.md`・`impl-logic-app-boundary.md`・`impl-table-links.md` | — |
| 手順の写し | アプリケーションスキルの手順を書く・直すとき、表と判断の答えの写しをどう見つけ、どう直すか | [impl-procedure-copies.md](references/impl-procedure-copies.md) | `app-skill-shape.md`・`skill-kinds.md` | ○ |
| DBに置いた値の見分け方 | アプリケーションスキルが読むDBに、判断定数・判断の定義・取り決め・公知の事実の写しが混ざっていないかを、どう見分け、どこへ移すか | [impl-db-values.md](references/impl-db-values.md) | `value-placement.md`・`impl-material-shape.md` | ○ |
| 依存関係の図 | 依存関係を人に説明するとき、索引の「依存する判断」から、どんな図を作って見せるか | [impl-dependency-graph.md](references/impl-dependency-graph.md) | `logic-skill-shape.md` | ○ |
| 設計の言葉 | スキルを作る・直すときや、このスキルの答えを指示者に伝えるとき、人・値・スキルの種類を、どの言葉で呼ぶか | [impl-design-terms.md](references/impl-design-terms.md) | `value-placement.md` | — |

# このスキルの設計上の決まりごと

1. このスキルは判断を答えるだけで、判断の対象もデータも持たない。対象の値は、材料の写しとして受け取る。データを取りに行かず、保存もせず、IDも受け取らない。
2. 答える範囲は、聞きたい事を索引の「扱うこと」と照らして決める。索引の「依存する判断」にある判断を、先に出す。
3. 判断ファイルの「求める材料」がそろわなければ答えない。計算がある判断は、`uv run <skill-dir>/scripts/judge.py <判断> <材料.json>` で計算する。<判断> は `references/` のファイル名。依存する判断の材料も、一緒に渡す。
4. 答えは、指定された形にそろえ、理由と組にして返す。
5. 中核判断は、判断ファイルで答えられなければ、一般論で答えず「判断が無い」と返す。「未決」に当たったら、未決であることと、決めるまでの暫定の扱いを含める。一般的な業務知識は、判断ファイルに無いことを一般知識で補ってよい。
