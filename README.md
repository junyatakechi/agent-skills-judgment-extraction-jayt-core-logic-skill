# agent-skills-judgment-extraction-jayt-core-logic-skill

設計文書「人の判断を切り出すAgent Skillsの設計」を、作成者がどう実装するかの中核判断を、理由とともに持つロジックスキル。
設計文書の型と定型文を写した判断と、設計文書に書かれていない実装の判断を持ち、スキルを作る・直すときの型の確認を計算で返す。

## 必要なもの

- [Claude Code](https://docs.claude.com/en/docs/claude-code/overview)
- Python 3.11以上と [uv](https://docs.astral.sh/uv/)（型の確認の計算に使う）
- 設計文書（`SKILL.md` の frontmatter の `metadata.design-version`）

## インストール

```bash
git clone https://github.com/junyatakechi/agent-skills-judgment-extraction-jayt-core-logic-skill.git ~/.claude/skills/agent-skills-judgment-extraction-jayt-core-logic-skill
```

特定のプロジェクトだけで使うなら、`<プロジェクト>/.claude/skills/` の中でクローンする。

## セットアップ

なし。

## 使い方

スキルを作る・直す作業のときに、名前を指名して呼ぶ。指名しないと、このスキルは読み込まれない。

- 「/agent-skills-judgment-extraction-jayt-core-logic-skill この判断ファイルを今の型に直して」
- 「/agent-skills-judgment-extraction-jayt-core-logic-skill この値は判断定数？取り決め？」
- 「/agent-skills-judgment-extraction-jayt-core-logic-skill 新しいロジックスキルを作りたい」
