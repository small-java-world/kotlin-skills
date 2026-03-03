---
name: clean-code-principles-architect
description: Kotlin/Gradle（Spring Boot Kotlin含む）のコードレビューで、保守性原則（KISS・YAGNI・DRY・SRP・CQS・Naming）を適用し、根拠付きで最小変更の修正を提案する。
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
- `CC-P006` Naming: ドメイン語彙と命名の一貫性を保つ。
- `CC-K001` 構造化並行性違反: GlobalScope使用、例外伝搬漏れ。
- `CC-K002` Flow/Channel 誤用: cold/hot混同、collect内副作用。
- `CC-K003` Null安全性境界漏れ: Platform type、lateinit濫用。
- `CC-K004` スコープ関数過剰チェーン: let/run/apply/also/with の3段以上チェーン。
- `CC-K005` Data class 契約違反: var混入、継承との組み合わせ。

## 手順
1. 意図と現在の制約を把握する。
2. 各ホットスポットを主に違反している1つのルールにマッピングする。
3. 振る舞いを保持する最小修正を提案する。
4. 検証ステップとロールバックのヒントを定義する。

## 出力形式
- 共有の出力コントラクトを使用すること:
`../clean-code-_shared/references/output_contract.md`
- レビューで特定のファイル・行に起因する finding は `file`（相対パス）と
  `line_range`（例: "42-58" or "42"）を含めること。
- 複数ファイルにまたがる場合は主要ファイルの行範囲を記載すること。
- コード全体への抽象的な指摘など位置特定が不可能な場合は省略可。

## 参照
- `../clean-code-_shared/references/rules.json` — ルール定義の正（20ルール）
- `../clean-code-_shared/references/output_contract.md` — 出力フォーマット仕様
- `../clean-code-_shared/references/principles_map.md` — 原則ルール詳細（CC-P 用）
- `../clean-code-_shared/references/anti_patterns.md` — テスタビリティ反パターン（参考）
