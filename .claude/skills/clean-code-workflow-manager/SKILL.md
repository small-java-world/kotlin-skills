---
name: clean-code-workflow-manager
description: Kotlin/Gradle（Spring Boot Kotlin・coroutines含む）のコードレビューを、原則・変更安全性・テスタビリティの3専門エージェントに振り分け、根拠付き findings と最小修正・検証手順を統合出力するワークフローマネージャー。
---

# クリーンコード ワークフローマネージャー

## 目的
- 「クリーンなコードを書く」という要求を、再現性のある検証可能な出力に変換する。
- 以下の順序で3つのサブスキルに作業を振り分ける:
  1. `clean-code-principles-architect`
  2. `clean-code-change-safety-reviewer`
  3. `clean-code-testability-optimizer`

## 入力
- 対象コード、PR diff、または設計メモ
- 実行環境・制約（言語、フレームワーク、締め切り、互換性）
- 任意: チーム固有の規約

## 出力コントラクト（必須）
- findings を以下のいずれかで返す:
  1. JSON（`findings[]`）
  2. Markdown findings リスト
- 各 finding に以下を含めること:
  1. `severity`（`critical|high|medium|low`）
  2. `rule_id`
  3. `evidence`
  4. `minimal_fix`
  5. `verification`

参照:
- `../clean-code-_shared/references/output_contract.md`
- `../clean-code-_shared/references/extraction_notes.md`

## ワークフロー

### Step 1: スコープ確定（親が実施）
- **実施主体: workflow-manager（親）**
- サブスキルを呼び出す前に、以下を定義する:
  - **スコープ内**: レビュー対象のファイル・モジュール・変更セット。
  - **スコープ外**: 無関係なファイル・将来要件・依頼外のスタイル修正。
- スコープ定義を3つのサブスキル全てにコンテキストとして渡す。
- サブスキルは宣言したスコープ外の findings を出力してはならない。

```
スコープ内ファイル:   [path/to/FileA.kt, path/to/FileB.kt]
スコープ内モジュール: [module-name]
レビュートリガー:     [PR diff / 個別依頼 / モジュール全体]
```

### Step 2: 原則チェック
- スコープを適用した入力で `clean-code-principles-architect` を呼び出す。
- 対象ルール: CC-P001 (KISS)、CC-P002 (YAGNI)、CC-P003 (DRY)、CC-P004 (SRP)、CC-P005 (CQS)、CC-P006 (Naming)、CC-K001〜CC-K005 (Kotlin固有)。

### Step 3: 変更安全性チェック
- スコープを適用した入力で `clean-code-change-safety-reviewer` を呼び出す。
- 対象ルール: CC-C001〜CC-C004。
- **注意**: Step 2 と独立して実行する。Step 2 の出力を入力として必要としない。
  Step 2 の finding が有益なコンテキストになる場合（例: SRP 違反が影響範囲リスクを示唆）は参照してよいが、サブスキル間の出力依存は必須ではない。

### Step 4: テスタビリティチェック
- スコープを適用した入力で `clean-code-testability-optimizer` を呼び出す。
- 対象ルール: CC-T001〜CC-T005。
- Step 3 と同じ独立性ルールを適用する。

### Step 5: 統合（親が実施）
- **実施主体: workflow-manager（親）**
- Step 2〜4 の全 findings をマージする。
- **重複排除アルゴリズム**:
  1. `rule_id` ごとに findings をグループ化する。
  2. グループ内で、各 finding の `evidence` からコードアンカーを抽出する:
     `` `バッククォート` `` で囲まれた最初の識別子、またはCamelCase/camelCase の最初の単語。
     同じ `rule_id` かつ同じコードアンカーを持つ2つの finding はマージする:
     - **severity が高い方**のエントリを残す。
     - `minimal_fix` が補完的な場合は結合し、そうでなければより具体的な方を残す。
     - **フォールバック**（アンカーが取れない場合）: どちらの evidence にもバッククォートや CamelCase 識別子がない場合は、`evidence` の token overlap ≥80% をマージ判定基準とする。
  3. 異なる `rule_id` だが同一の `evidence` を持つ findings は両方残す（クロスルールの重複は意図的であり価値がある）。
- マージ・重複排除済みのリストを severity 降順（critical → high → medium → low）で出力する。

### 出力品質チェック（親が実施）
- 統合後、ユーザーに返す前に lint ツールで出力を検証する:
```powershell
python ../clean-code-_shared/scripts/skill_output_lint.py `
  --input <output-file> `
  --profile clean-code
```
- `ERROR` は必ず修正してから返す。`WARN` は可能な範囲で対処する。

## サブスキル実行に関する注意

- **サブスキルは独立して実行する**（順序依存がない場合、Step 2〜4 は並列実行可能）。
- **ルール出力の優先順位**:
  1. **本来の責務**: 各サブスキルは自身のプレフィックス（P/C/T）配下の findings を最優先する。
  2. **クロスカテゴリ（参照のみ）**: クロスカテゴリの関連性は参照注記として記録できるが、独立した正式 finding（単独の `rule_id` エントリ）としてカウントしない。代わりに、一次 finding の `minimal_fix` または `evidence` フィールド内に「（参照: CC-Xnnn）」と注記する。
  3. **禁止**: 自身のプレフィックス配下の findings がゼロのまま、クロスカテゴリの findings のみを出力してはならない（本来の責務の放棄）。

## バリデーション
- 生成した出力を lint で検証する:
```powershell
python ../clean-code-_shared/scripts/skill_output_lint.py `
  --input <output-file> `
  --profile clean-code
```

終了コード:
- `0`: 合格
- `1`: 警告のみ
- `2`: 不合格

## Kotlin 評価コーパス
- マニフェストをビルドする:
```powershell
python ../clean-code-_shared/scripts/build_kotlin_eval_manifest.py
```
- コーパスのセルフテストを実行する:
```powershell
python ../clean-code-_shared/scripts/run_kotlin_eval_tests.py --self-test
```
- 実際の出力をスコアリングする:
```powershell
python ../clean-code-_shared/scripts/score_kotlin_eval.py `
  --manifest ../clean-code-_shared/tests/kotlin_eval/kotlin_eval_manifest.json `
  --actual-dir <KBxxxのjsonまたはmdを含むディレクトリ> `
  --out ../clean-code-_shared/tests/kotlin_eval/score_report.json
```

## 関連サブスキル
- `../clean-code-principles-architect/SKILL.md`
- `../clean-code-change-safety-reviewer/SKILL.md`
- `../clean-code-testability-optimizer/SKILL.md`
