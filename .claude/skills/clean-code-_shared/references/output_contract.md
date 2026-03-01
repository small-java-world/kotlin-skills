# 出力コントラクト

## JSON スキーマ（実用的なコントラクト）

```json
{
  "summary": "全体の概要（短く）※任意フィールド",
  "findings": [
    {
      "severity": "high",
      "rule_id": "CC-P004",
      "evidence": "現在のコードの具体的な問題箇所と理由",
      "minimal_fix": "振る舞いを保ちながら最小限の変更で直す方法",
      "verification": "修正が機能することを証明する方法"
    }
  ]
}
```

> **注意**: `summary` は任意フィールド。lint/score は `findings[]` のみを評価する。
> `findings` が空の場合（指摘ゼロが正解のケース）は `--allow-empty-findings` で許可する。

## Markdown コントラクト

```markdown
## Findings

1. タイトル
Severity: high
Rule_ID: CC-P004
Evidence: ...
Minimal_Fix: ...
Verification: ...
```

## Severity ポリシー
- `critical`: 障害/データ消失/セキュリティ回帰の高いリスク
- `high`: 機能回帰または大きな保守性破壊の高い可能性
- `medium`: 影響範囲が限定された明確な保守性の負債
- `low`: 軽微な可読性/一貫性の問題

## 品質基準
1. すべての指摘は5つの必須フィールドを全て含むこと。
2. 最小修正は振る舞いを保持する変更差分を優先すること。
3. 検証は実行可能なもの（テストコマンド/チェックリスト）にすること。曖昧な文言は不可。
