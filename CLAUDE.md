# CLAUDE.md — Kotlin Clean-Code Skills プロジェクト

## プロジェクト概要

Kotlin/Gradle（Spring Boot Kotlin・coroutines含む）のコードレビューを自動化する
Claude Code スキルスイート。4つのスキル + 共有インフラで構成。

## ディレクトリ構成

```
.claude/
  skills/
    clean-code-workflow-manager/     # 統合ワークフロー（3エージェント振り分け）
    clean-code-principles-architect/ # 原則チェック（CC-P, CC-K）
    clean-code-change-safety-reviewer/ # 変更安全性（CC-C）
    clean-code-testability-optimizer/  # テスタビリティ（CC-T）
    clean-code-_shared/              # 共有リソース
      references/                    # ルール定義、出力契約、抽出ノート
      scripts/                       # lint, scoring スクリプト
      tests/                         # eval コーパス、テストフィクスチャ
  hooks/
    validate-bash.py                 # 破壊的コマンドブロック hook
```

## ルール体系（20ルール）

- `CC-P001`〜`CC-P006`: 原則（KISS, YAGNI, DRY, SRP, CQS, Naming）
- `CC-C001`〜`CC-C004`: 変更安全性（影響範囲, 隠れ結合, 混合変更, マイグレーション）
- `CC-T001`〜`CC-T005`: テスタビリティ（回帰テスト, テスト品質, 結合度, 表現力, 非決定性）
- `CC-K001`〜`CC-K005`: Kotlin固有（構造化並行性, Flow/Channel, Null安全, スコープ関数, Data class）

ルール定義の正: `.claude/skills/clean-code-_shared/references/rules.json`

## リファレンスファイル

| ファイル | 用途 |
|---------|------|
| `references/rules.json` | 20ルールの定義（lint が自動読み込み） |
| `references/output_contract.md` | 出力フォーマット仕様（JSON/Markdown） |
| `references/extraction_notes.md` | ルール抽出方針、クロスカテゴリ所属基準 |
| `references/principles_map.md` | 各原則ルールの詳細解説・スメルパターン・修正例 |
| `references/anti_patterns.md` | テスタビリティのアンチパターン集 |

## 開発コマンド

### Lint（出力フォーマット検証）
```bash
python .claude/skills/clean-code-_shared/scripts/skill_output_lint.py \
  --input <output-file.json> --profile clean-code
```

### スコアリング（eval コーパス実行）
```bash
python .claude/skills/clean-code-_shared/scripts/score_kotlin_eval.py \
  --manifest .claude/skills/clean-code-_shared/tests/kotlin_eval/kotlin_eval_manifest.json \
  --actual-dir .claude/skills/clean-code-_shared/tests/kotlin_eval/baseline_actual \
  --out .claude/skills/clean-code-_shared/tests/kotlin_eval/score_report.json
```

## コミット規約

- `feat(eval):` — eval ケース追加
- `fix(eval):` — eval ケース修正
- `feat(skill):` — スキル定義変更
- `fix(infra):` — lint/scoring/hook 修正
- `docs:` — ドキュメント更新

## 注意事項

- `score_report.json` と `kotlin_eval_manifest.json` は `.gitignore` 済み（生成物）
- `baseline_actual/` のファイルは現在 expected_findings のコピー（gold-vs-gold モード）
- AI 実行による実際の出力で置き換えることで真のスコアを計測可能
