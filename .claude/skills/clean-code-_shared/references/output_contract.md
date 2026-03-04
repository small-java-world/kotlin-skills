# 出力コントラクト

## 出力形式の優先順

- **JSON を優先する**。プログラム的な lint 検証・スコアリング・重複排除に最適化されている。
- Markdown は人間向けのデバッグ用途でのみサポートする。
- フィールド名は小文字（`severity`, `rule_id`, `file`, `line_range`, `evidence`, `minimal_fix`, `verification`）を使用する。

## JSON スキーマ（実用的なコントラクト）

```json
{
  "summary": "全体の概要（短く）※任意フィールド",
  "findings": [
    {
      "severity": "high",
      "rule_id": "CC-P004",
      "file": "src/UserService.kt",
      "line_range": "42-58",
      "evidence": "現在のコードの具体的な問題箇所と理由",
      "minimal_fix": "振る舞いを保ちながら最小限の変更で直す方法",
      "verification": "修正が機能することを証明する方法"
    }
  ]
}
```

> **注意**: `summary` は任意フィールド。lint/score は `findings[]` のみを評価する。
> `findings` が空の場合（指摘ゼロが正解のケース）は `--allow-empty-findings` で許可する。
> `file` と `line_range` は両方そろって初めてコード位置として有効。workflow-manager はこの情報を重複排除に使用する。両フィールドとも省略可能（オプション）。

## Markdown コントラクト

```markdown
## Findings

1. タイトル
Severity: high
Rule_ID: CC-P004
File: src/UserService.kt
Line_Range: 42-58
Evidence: ...
Minimal_Fix: ...
Verification: ...
```

> **注意**: `File` と `Line_Range` はオプションフィールド。JSON の `file`/`line_range` と同じ役割。
> `Rule_ID:` を推奨。lint は `RuleID:`（アンダースコアなし）も受容するが、契約上の正式名称は `Rule_ID:` とする。

## Severity ポリシー
- `critical`: 障害/データ消失/セキュリティ回帰の高いリスク
- `high`: 機能回帰または大きな保守性破壊の高い可能性
- `medium`: 影響範囲が限定された明確な保守性の負債
- `low`: 軽微な可読性/一貫性の問題

## 品質基準
1. すべての指摘は5つの必須フィールドを全て含むこと。
2. `rule_id` は `rules.json` に定義された20ルールのいずれかでなければならない（lint が ERROR として強制）。
3. 最小修正は振る舞いを保持する変更差分を優先すること。
4. 検証は実行可能なもの（テストコマンド/チェックリスト）にすること。曖昧な文言は不可。
