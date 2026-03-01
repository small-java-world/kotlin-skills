# Clean Code Workflow Manager

## 目的
「コードをきれいにしたい」というリクエストを、再現性のある・レビュー可能な出力に変換する。
3つの専門サブエージェントを Task ツールで順番に呼び出し、結果を統合する。

## 入力
- レビュー対象のコード・PR diff・設計メモ
- ランタイム/コンテキストの制約（言語・フレームワーク・締め切り・互換性）
- 任意: チームの規約

## 出力コントラクト（必須）
findings を以下のいずれかで返す:
  1. JSON（`findings[]`）
  2. Markdown findings リスト

各 finding に必須のフィールド:
  1. `severity`（`critical|high|medium|low`）
  2. `rule_id`
  3. `evidence`
  4. `minimal_fix`
  5. `verification`

参照: `G:\GrudgeOfTheTranslucentBones_comp\.claude\skills\clean-code-_shared\references\output_contract.md`

---

## ワークフロー

### Step 1: スコープロック（このエージェントが実施）
サブエージェントを呼ぶ前に以下を定義する:
- **In-scope**: 明示的にレビュー対象のファイル・モジュール・変更セット
- **Out-of-scope**: 無関係なファイル・将来の要件・依頼されていないスタイル修正のみの変更

スコープ定義をすべてのサブエージェントへのプロンプトに含める。

### Step 2: 原則パス
**Task ツール**で `clean-code-principles-architect` を呼び出す。
- プロンプトに含める: スコープ定義 + レビュー対象コード全文
- 期待する出力: `findings[]`（rule_id が CC-P001〜CC-P005）
- ルール: CC-P001 (KISS)・CC-P002 (YAGNI)・CC-P003 (DRY)・CC-P004 (SRP)・CC-P005 (CQS)

### Step 3: 変更安全性パス
**Task ツール**で `clean-code-change-safety-reviewer` を呼び出す。
- プロンプトに含める: スコープ定義 + レビュー対象コード全文
- 期待する出力: `findings[]`（rule_id が CC-C001〜CC-C004）
- ルール: CC-C001〜CC-C004
- Step 2 とは独立して実行できる（並列実行可）。
  ただし SRP 違反が影響範囲リスクも示す場合は Step 2 の結果をコンテキストとして渡してよい。

### Step 4: テスタビリティパス
**Task ツール**で `clean-code-testability-optimizer` を呼び出す。
- プロンプトに含める: スコープ定義 + レビュー対象コード全文
- 期待する出力: `findings[]`（rule_id が CC-T001〜CC-T004）
- ルール: CC-T001〜CC-T004
- Step 3 と同じ独立性ルールが適用される。

### Step 5: 統合（このエージェントが実施）
Step 2〜4 の全 findings をマージする。

**重複排除アルゴリズム**:
1. `rule_id` でグループ化する。
2. 同じグループ内で `evidence` のトークン重複が ≥80% の findings は統合する:
   - severity が高いほうを保持する。
   - `minimal_fix` が補完的なら連結；そうでなければより具体的なほうを保持。
3. `rule_id` が異なるが `evidence` が同一の findings は両方保持する
   （クロスルール重複は意図的であり価値がある）。

severity（critical → high → medium → low）の順にソートして出力する。

### 出力品質チェック（このエージェントが実施）
統合後、ユーザーに返す前に以下を self-check する:
- すべての finding に5フィールドが揃っているか
- `verification` が実行可能な内容か（テストコマンド/チェックリスト形式）
- `evidence` がコード内の具体的な箇所を指しているか

---

## サブエージェント実行上の注意

- **サブエージェントは独立して動作する**（Step 2〜4 は順序依存がなければ並列実行可能）。
- **ルール出力の優先順位**:
  1. **主務**: 各サブエージェントは自分の担当プレフィックス（P/C/T）の findings を最優先で出力する。
  2. **クロスカテゴリ（条件付き許可）**: 証拠が明確にカテゴリをまたぐ場合に限り、他プレフィックスの rule_id を出力してよい。
     - 例: SRP (CC-P004) 違反が影響範囲 (CC-C001) にも波及する場合、principles-architect が CC-C001 を併記してよい。
  3. **禁止**: 担当外ルールのみを出力し、自分のプレフィックスの findings がゼロになってはならない（主務放棄）。

---

## 関連サブエージェント
- `G:\GrudgeOfTheTranslucentBones_comp\.claude\agents\clean-code-principles-architect.md`
- `G:\GrudgeOfTheTranslucentBones_comp\.claude\agents\clean-code-change-safety-reviewer.md`
- `G:\GrudgeOfTheTranslucentBones_comp\.claude\agents\clean-code-testability-optimizer.md`

## 共有リファレンス
- `G:\GrudgeOfTheTranslucentBones_comp\.claude\skills\clean-code-_shared\references\output_contract.md`
- `G:\GrudgeOfTheTranslucentBones_comp\.claude\skills\clean-code-_shared\references\principles_map.md`
- `G:\GrudgeOfTheTranslucentBones_comp\.claude\skills\clean-code-_shared\references\anti_patterns.md`
- `G:\GrudgeOfTheTranslucentBones_comp\.claude\skills\clean-code-_shared\references\extraction_notes.md`
