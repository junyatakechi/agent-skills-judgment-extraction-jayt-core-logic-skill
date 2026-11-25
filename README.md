# agent-skills-judgment-extraction-jayt-core-logic-skill

設計文書「人の判断を切り出すAgent Skillsの設計」を、作成者がどう実装するかの中核判断を、理由とともに持つロジックスキル。
設計文書の型と定型文を写した判断と、設計文書に書かれていない実装の判断を持ち、スキルを作る・直すときの型の確認を計算で返す。

## 必要なもの

- [Claude Code](https://docs.claude.com/en/docs/claude-code/overview)
- Python 3.11以上と [uv](https://docs.astral.sh/uv/)（型の確認の計算に使う）

## インストール

```bash
git clone https://github.com/junyatakechi/agent-skills-judgment-extraction-jayt-core-logic-skill.git ~/.claude/skills/agent-skills-judgment-extraction-jayt-core-logic-skill
```

特定のプロジェクトだけで使うなら、`<プロジェクト>/.claude/skills/` の中でクローンする。

## セットアップ

なし。

## 使い方

スキルを作る・直す作業のときに、名前を指名して呼ぶ。指名しないと、このスキルは読み込まれない。

### 新しいスキルを作る

1. AIエージェントにいろいろ頼みながら、作業を終える。
2. この作業をまた繰り返すと思ったら、その会話のまま、このスキルを名前で指名して頼む。
   - 「/agent-skills-judgment-extraction-jayt-core-logic-skill ここまでの作業を、また繰り返せるようにスキルにして」
3. AIエージェントがこのスキルに聞きながらスキルを作り、型どおりかを計算で確かめる。

### すでにあるスキルに使う

- 「/agent-skills-judgment-extraction-jayt-core-logic-skill このスキルにある知識を整理して」
- 「/agent-skills-judgment-extraction-jayt-core-logic-skill 環境に依存しているところを切り出して分けて」
- 「/agent-skills-judgment-extraction-jayt-core-logic-skill この回答はどこで判断していますか？」
