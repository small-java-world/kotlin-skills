---
name: clean-code-principles-architect
description: コアな保守性原則（KISS・YAGNI・DRY・SRP・CQS）をコード/設計に適用し、具体的な根拠付きで最小変更の修正を提案する。
---

# Clean Code Principles Architect

## 目的
- 保守性を下げる原則違反を診断する。
- 大規模な書き直しよりも、ローカルで最小限の修正を優先する。

## 対象ルール
- `CC-P001` KISS: 偶発的な複雑さを避ける。
- `CC-P002` YAGNI: 投機的な抽象化を削除する。
- `CC-P003` DRY: 知識の重複を削減する（構文の繰り返しではなく）。
- `CC-P004` SRP: 変更される理由が異なるものを分離する。
- `CC-P005` CQS: 状態変更と情報クエリを分割する（実用的な範囲で）。

## 手順
1. 意図と現在の制約を把握する。
2. 各ホットスポットを主に違反している1つのルールにマッピングする。
3. 振る舞いを保持する最小修正を提案する。
4. 検証ステップとロールバックのヒントを定義する。

## 出力形式
- 共有の出力コントラクトを使用すること:
`D:\kotlinskills\clean-code-_shared/references/output_contract.md`

## 参照
- `D:\kotlinskills\clean-code-_shared/references/principles_map.md`
- `D:\kotlinskills\clean-code-_shared/references/anti_patterns.md`
