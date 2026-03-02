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
- **重複排除アルゴリズム（3段階）**:

  [優先度1] コード位置ベース（file + line_range が両方ある場合）
  - 同じ (file, line_range) を持つ findings はマージ対象。
  - rule_id が異なっていてもマージする（同じコード箇所への異なる視点）。
  - 残す finding: severity が高い方を採用。
  - 他の finding の rule_id を "（参照: CC-Xnnn）" として evidence または minimal_fix に注記する。

  [優先度2] コードアンカーベース（コード位置がない場合）
  - まず rule_id でグループ化する。
  - グループ内で、evidence からコードアンカーを抽出:
    バッククォートで囲まれた最初の識別子 or CamelCase/camelCase の最初の単語。
  - 同じ rule_id かつ同じコードアンカー → マージ（severity 高い方を残す）。

  [優先度3] マージしない
  - 上記どちらも該当しない場合は独立した finding として保持する。
  - ※ 80% token overlap フォールバックは廃止。不明確な一致は誤マージより見落としの方が安全。

- マージ済みリストを severity 降順（critical → high → medium → low）で出力する。

### 出力品質チェック（親が実施）
- 統合後、ユーザーに返す前に lint ツールで出力を検証する:
```powershell
python ../clean-code-_shared/scripts/skill_output_lint.py `
  --input <output-file> `
  --profile clean-code
```
- `ERROR` は必ず修正してから返す。`WARN` は可能な範囲で対処する。

## エージェント間の情報フロー

- **基本原則: 独立実行**。各サブスキルは対象コードとスコープ定義のみを入力として受け取り、先行エージェントの出力に依存しない。
- **任意参照**: 先行エージェントの findings が後続の分析に有益な場合（例: principles が検出した SRP 違反を change-safety が影響範囲リスクとして参照）、ワークフローマネージャーがコンテキストとして渡してよい。ただしこれは**最適化であり必須ではない**。
- **根拠**: 独立実行により (a) 並列化可能、(b) 1エージェントの障害が他に波及しない、(c) 各エージェントの出力が独立に検証可能。

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
